import asyncio
from typing import Any, Callable, Dict, List


def async_executor(afunc: Callable, args_list: List[Dict]) -> Any:
    async def amain():
        tasks = []
        for args in args_list:
            tasks.append(afunc(**args))
        return await asyncio.gather(*tasks)
    return asyncio.run(amain())
