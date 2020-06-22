import asyncio

from bbs.telnet import start_telnet
from bbs.models import models_init, models_cleanup

async def main():
    try:
        db = await models_init()
        tserver = await start_telnet()
        async with tserver:
            await asyncio.gather(tserver.serve_forever())
    finally:
        await models_cleanup()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass