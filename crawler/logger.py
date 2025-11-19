import logging

# Configuration globale du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()  # affiche les logs dans la console
    ]
)

# Logger unique pour tout le projet
logger = logging.getLogger("CrawlerWeb")
