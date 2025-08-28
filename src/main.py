import asyncio

from ini import Initializator
from logging_setup import setup_logging

async def main():
    setup_logging()
    initializator = Initializator()
    parser = await initializator.initialize()
    await parser.execute()

if __name__ == "__main__":
    asyncio.run(main())