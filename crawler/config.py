from dataclasses import dataclass

@dataclass
class CrawlerConfig:
    max_workers: int = 40
    timeout: float = 10.0
    delay_per_domain: float = 0.8
    follow_external: bool = True          # ON suit TOUS les liens externes
    obey_robots_txt: bool = True
    user_agent: str = "SchoolCrawlerBot/2.0 (+http://localhost)"