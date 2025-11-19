import asyncio
from collections import deque
from typing import Callable
import httpx
from .database import save_page
from .utils import normalize_url, get_domain, respect_delay, extract_links
from .logger import logger  # importer le logger

class WebCrawler:
    def __init__(self, start_url: str, update_stats: Callable, max_tasks: int = 10):
        self.start_url = start_url
        self.queue = deque([start_url])
        self.visited: set[str] = set()
        self.running = False
        self.update_stats = update_stats
        self.max_tasks = max_tasks
        self.sem = asyncio.Semaphore(self.max_tasks)
        self.client: httpx.AsyncClient | None = None

    async def fetch(self, url: str) -> str | None:
        async with self.sem:
            try:
                response = await self.client.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Success: {url}")
                    return response.text
                elif response.status_code in (403, 429):
                    logger.warning(f"Blocked ({response.status_code}), retrying {url}")
                    await asyncio.sleep(2)
                    return await self.fetch(url)
                else:
                    logger.warning(f"Failed ({response.status_code}): {url}")
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
            return None

    async def process_page(self, url: str, html: str):
        normalized_url = normalize_url(base=url, link=url)  # <-- ici, on passe base ET link
        domain = get_domain(url)
        save_page(normalized_url, domain, "success")
        logger.info(f"Page saved: {normalized_url}")

        # extraction des liens
        new_urls = extract_links(html, base_url=url)
        for u in new_urls:
            if u not in self.visited:
                self.queue.append(u)


    async def worker(self):
        while self.running and self.queue:
            url = self.queue.popleft()
            if url in self.visited:
                continue
            self.visited.add(url)
            html = await self.fetch(url)
            if html:
                await self.process_page(url, html)
            # respecter le délai pour le domaine
            await respect_delay(get_domain(url))

    async def start(self):
        self.running = True
        self.client = httpx.AsyncClient(
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Accept-Language": "fr-FR,fr;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.google.com/"
            }
        )
        tasks = [asyncio.create_task(self.worker()) for _ in range(self.max_tasks)]
        await asyncio.gather(*tasks)
        await self.client.aclose()

    def stop(self):
        self.running = False
