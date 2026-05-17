import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())