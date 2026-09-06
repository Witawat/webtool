import asyncio
from collections.abc import Awaitable


async def async_with_timeout[T](coro: Awaitable[T], seconds: float) -> T:
    return await asyncio.wait_for(coro, timeout=seconds)
