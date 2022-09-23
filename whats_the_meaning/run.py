# Imports.
import sys
import asyncio

from .app import *


# Initialize App object.
obj = App()

# Coroutine.
async def main():
    await obj.run(sys.argv[1]) if len(sys.argv) == 2 else obj.err(ErrorType.NO_ARG)


def wtm():
    asyncio.run(main())
