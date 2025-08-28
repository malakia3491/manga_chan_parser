import logging
from sqlite3 import IntegrityError
import uuid
from sqlalchemy import insert, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, Generic, TypeVar, Optional, List

from domain.cache.CacheBase import CacheBase
from persistance.mapping.MappingDirector import MappingDirector

PT = TypeVar('PT', bound=object)  # Persistence Type
DT = TypeVar('DT', bound=object)  # Domain Type

class CachedRepository(Generic[DT, PT]):
    def __init__(self, session: AsyncSession, cache: CacheBase, entity_class: Type[PT], mapper: MappingDirector):
        self._session = session
        self._cache = cache
        self._entity_class = entity_class
        self._mapper = mapper
        self._pending_add: List[DT] = []
        self._pending_update: List[DT] = []
        self._pending_remove: List[DT] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def add(self, entity: DT):
        """Add domain entity to repository"""
        self._pending_add.append(entity)
        self._cache.put(entity.id, entity)

    @property
    def count(self) -> int:
        return len(self._cache)

    async def get(self, id: uuid.UUID) -> Optional[DT]:
        """Get domain entity by ID"""
        if entity := self._cache.get(id):
            return entity
        
        persistence_entity = await self._session.get(self._entity_class, id)
        if persistence_entity:
            domain_entity = self._mapper.map(persistence_entity, PT)
            self._cache.put(id, domain_entity)
            return domain_entity
        return None

    async def get_by_field_or_create(self, field: str, entity: DT) -> DT:
        """
        Atomic-ish get-or-create: 
        - если в кэше/БД есть — вернуть;
        - иначе попытаться вставить (INSERT ... DO NOTHING / OR IGNORE) и SELECT снова;
        - в любом случае вернуть доменную сущность, привязанную к одной и той же persistence-строке.
        """
        value = getattr(entity, field)

        found = await self.get_by_field(field, value)        
        if found:
            return found
        try:
            ins = insert(self._entity_class).values(**{field: value})
            dialect = getattr(self._session.bind, "dialect", None)
            dialect_name = getattr(dialect, "name", None) if dialect is not None else None

            if dialect_name == "sqlite":
                ins = ins.prefix_with("OR IGNORE")
                await self._session.execute(ins)
            elif dialect_name in ("postgresql", "postgres"):
                try:
                    ins = ins.on_conflict_do_nothing(index_elements=[field])
                    await self._session.execute(ins)
                except Exception:
                    await self._session.execute(ins)
            else:
                try:
                    await self._session.execute(ins)
                except IntegrityError:
                    await self._session.rollback()
        except Exception:
            pass

        persistence = await self.get_by_field(field, value)
        if persistence:
            return persistence

        self.add(entity)
        return entity
    
    def update(self, entity: DT):
        """Mark domain entity as updated"""
        if entity not in self._pending_add and entity not in self._pending_update:
            self._pending_update.append(entity)

    def remove(self, entity: DT):
        """Remove domain entity"""
        self._pending_remove.append(entity)
        self._cache.remove(entity.id)

    async def commit(self):
        """Commit changes to database"""
        # Add new entities
        for domain_entity in self._pending_add:
            persistence_entity = self._mapper.map(domain_entity, PT)
            self._session.add(persistence_entity)
        
        # Update existing entities
        for domain_entity in self._pending_update:
            existing = await self._session.get(self._entity_class, domain_entity.id)
            if not existing:
                continue
                
            temp_persistence = self._mapper.map(domain_entity, self._entity_class)
            
            # Получаем только колоночные атрибуты (игнорируем отношения и прокси)
            mapper = inspect(self._entity_class)
            column_attrs = {attr.key for attr in mapper.column_attrs}
            
            # Копируем только простые атрибуты-колонки
            for attr_name in column_attrs:
                # Пропускаем первичные ключи (не должны обновляться)
                if attr_name == mapper.primary_key[0].key:
                    continue
                    
                value = getattr(temp_persistence, attr_name, None)
                setattr(existing, attr_name, value)
            
            self._cache.put(domain_entity.id, domain_entity)
        
        # Remove entities
        for domain_entity in self._pending_remove:
            persistence_entity = await self._session.get(self._entity_class, domain_entity.id)
            if persistence_entity:
                await self._session.delete(persistence_entity)
        
        # Clear pending lists
        self._pending_add.clear()
        self._pending_update.clear()
        self._pending_remove.clear()
        
        # Commit transaction
        await self._session.commit()

    async def rollback(self):
        """Rollback pending changes"""
        # Remove added entities from cache
        for domain_entity in self._pending_add:
            self._cache.remove(domain_entity.id)
        
        # Restore removed entities to cache
        for domain_entity in self._pending_remove:
            self._cache.put(domain_entity.id, domain_entity)
        
        # Clear pending lists
        self._pending_add.clear()
        self._pending_update.clear()
        self._pending_remove.clear()
        
        # Rollback transaction
        await self._session.rollback()

    async def get_by_field(self, field: str, value) -> Optional[DT]:
        """Get entity by indexed field using cache"""
        if entity := self._cache.get_by(field, value):
            return entity
        
        query = select(self._entity_class).where(getattr(self._entity_class, field) == value)
        result = await self._session.execute(query)
        persistence_entity = result.scalars().first()
        
        if persistence_entity:
            domain_entity = self._mapper.map(persistence_entity, DT)
            self._cache.put(domain_entity.id, domain_entity)
            return domain_entity
        return None

    async def get_all(self) -> List[DT]:
        """Get all domain entities"""
        # Get all from cache
        cache_entities = self._cache.get_all()
        if cache_entities:
            return cache_entities
        
        # Fetch all from database
        from sqlalchemy import select
        query = select(self._entity_class)
        result = await self._session.execute(query)
        persistence_entities = result.scalars().all()
        domain_entities = [self._mapper.map(e, DT) for e in persistence_entities]
        
        # Cache all entities
        for entity in domain_entities:
            self._cache.put(entity.id, entity)
            
        return domain_entities