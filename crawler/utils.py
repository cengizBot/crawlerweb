from urllib.parse import urljoin, urlparse
import time
from collections import defaultdict
from bs4 import BeautifulSoup
import asyncio

last_request: dict[str, float] = defaultdict(float)

def normalize_url(base: str, link: str) -> str | None:
    if not link:
        return None
    try:
        url = urljoin(base, link.strip())
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return None
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    except:
        return None

def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower()

async def respect_delay(domain: str, delay: float = 0.8):
    now = time.time()
    sleep_time = delay - (now - last_request[domain])
    if sleep_time > 0:
        await asyncio.sleep(sleep_time)
    last_request[domain] = time.time()


def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        link = normalize_url(base=base_url, link=a["href"])
        if link:  # ignore les liens invalides
            links.append(link)
    return links
