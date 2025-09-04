import asyncio
from concurrent.futures import ThreadPoolExecutor
import base64
from analyze import analyze_image

executor = ThreadPoolExecutor(max_workers=4)

async def AnalyzeImageAsync(image_base64: str) -> int:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, analyze_image, image_base64)
    return result