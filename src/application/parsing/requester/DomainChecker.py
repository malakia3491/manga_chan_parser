import asyncio
import logging
from typing import List, Optional, Dict, Any

from application.parsing.requester.Requester import Requester

class DomainChecker:
    def __init__(self, requester: Requester, timeout: float = 15.0, concurrency: int = 0):
        """
        :param requester: экземпляр Requester (контекстный менеджер). Если его сессия ещё не открыта,
                          DomainChecker откроет её локально на время проверки.
        :param timeout: максимум секунд, которые DomainChecker будет ждать ответа для каждого домена (per-task timeout)
        :param concurrency: максимум параллельных задач (0 или <=0 — без ограничения)
        """
        self.requester = requester
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout = float(timeout)
        self._concurrency = int(concurrency) if concurrency is not None else 0


    async def _check_domain(self, domain: str) -> Optional[float]:
        """
        Выполняет HEAD-запрос к https://{domain} и возвращает время отклика (в секундах),
        либо None при ошибке/таймауте.
        """
        url = f"https://{domain}"
        loop = asyncio.get_running_loop()
        start = loop.time()
        try:
            self.logger.debug("Проверка домена: %s", domain)
            await asyncio.wait_for(self.requester.head(url), timeout=self.timeout)
            elapsed = loop.time() - start
            self.logger.info("Домен %s доступен, время отклика: %.3fs", domain, elapsed)
            return elapsed
        except asyncio.TimeoutError:
            self.logger.debug("Таймаут при проверке домена %s (timeout=%s)", domain, self.timeout)
            return None
        except Exception as exc:
            self.logger.debug("Домен %s недоступен: %s", domain, exc)
            return None

    async def get_available_domain(self, domains: List[str]) -> Optional[str]:
        """
        Возвращает первый успешно ответивший домен (самый быстрый) или None, если ни один не доступен.
        Запускает параллельно проверки для всех доменов (с опциональным ограничением concurrency).
        """
        if not domains:
            return None
        return await self._run_checks(domains)

    async def _run_checks(self, domains: List[str]) -> Optional[str]:
        sem = asyncio.Semaphore(self._concurrency) if self._concurrency and self._concurrency > 0 else None

        async def worker(domain: str) -> Dict[str, Any]:
            """
            Возвращаем словарь с явными ключами:
            { "domain": str, "elapsed": Optional[float], "error": Optional[str] }
            """
            try:
                if sem:
                    async with sem:
                        elapsed = await self._check_domain(domain)
                else:
                    elapsed = await self._check_domain(domain)
                return {"domain": domain, "elapsed": elapsed, "error": None}
            except asyncio.CancelledError:
                return {"domain": domain, "elapsed": None, "error": "cancelled"}
            except Exception as exc:
                return {"domain": domain, "elapsed": None, "error": repr(exc)}

        tasks = [asyncio.create_task(worker(d)) for d in domains]

        try:
            for fut in asyncio.as_completed(tasks):
                try:
                    result = await fut  # ожидаем словарь от worker
                except asyncio.CancelledError:
                    continue
                except Exception as exc:
                    self.logger.debug("Ошибка выполнения таска проверки домена: %s", exc, exc_info=False)
                    continue

                if not isinstance(result, dict):
                    self.logger.debug("Непредвиденный результат из таска (не dict): %r", result)
                    continue

                domain = result.get("domain")
                elapsed = result.get("elapsed")
                error = result.get("error")

                self.logger.debug("Результат таска: domain=%r elapsed=%r error=%r", domain, elapsed, error)

                if elapsed is not None:
                    self.logger.info("Выбран домен: %s (время %.3fs)", domain, elapsed)
                    for t in tasks:
                        if t is not fut and not t.done():
                            t.cancel()
                    await asyncio.gather(*(t for t in tasks if t is not fut), return_exceptions=True)
                    return domain
                else:
                    self.logger.debug("Домeн %r не дал ответа (error=%r)", domain, error)

            self.logger.warning("Ни один из доменов не доступен")
            return None

        finally:
            for t in tasks:
                if not t.done():
                    t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
