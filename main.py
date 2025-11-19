import tkinter as tk
from tkinter import messagebox
import threading
import asyncio
from crawler.crawler import WebCrawler
from crawler.database import init_db, get_db
from crawler.models import Page
from crawler.logger import logger

class CrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler")
        self.root.geometry("800x500")
        self.root.configure(bg="#f0f2f5")

        self.crawler: WebCrawler | None = None
        self.thread: threading.Thread | None = None

        self.setup_ui()
        init_db()
        self.update_stats()

    def setup_ui(self):
        title = tk.Label(self.root, text="Web Crawler",
                         font=("Helvetica", 18, "bold"),
                         bg="#f0f2f5", fg="#1a73e8")
        title.pack(pady=20)

        frame_url = tk.Frame(self.root, bg="#f0f2f5")
        frame_url.pack(pady=10)
        tk.Label(frame_url, text="URL de départ :", font=("Helvetica", 12), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)
        self.entry_url = tk.Entry(frame_url, width=60, font=("Helvetica", 11))
        self.entry_url.pack(side=tk.LEFT, padx=5)
        self.entry_url.insert(0, "https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal")

        frame_buttons = tk.Frame(self.root, bg="#f0f2f5")
        frame_buttons.pack(pady=15)

        self.btn_start = tk.Button(frame_buttons, text="DÉMARRER", command=self.start_crawl,
                                   bg="#34a853", fg="white", font=("Helvetica", 12, "bold"), width=15, height=2)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(frame_buttons, text="ARRÊTER", command=self.stop_crawl,
                                  bg="#ea4335", fg="white", font=("Helvetica", 12, "bold"), width=15, height=2, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        self.stats_frame = tk.Frame(self.root, bg="white", relief=tk.SUNKEN, bd=2)
        self.stats_frame.pack(pady=20, padx=50, fill=tk.X)

        self.labels = {}
        stats = [("Total URLs découvertes", "total"),
                 ("Pages réussies", "success"),
                 ("Échecs / Bloquées", "failed"),
                 ("Statut", "status")]

        for text, key in stats:
            frame = tk.Frame(self.stats_frame, bg="white")
            frame.pack(pady=8, anchor="w", padx=30)
            tk.Label(frame, text=text + " :", font=("Helvetica", 12, "bold"), bg="white").pack(side=tk.LEFT)
            self.labels[key] = tk.Label(frame, text="0", font=("Helvetica", 12), bg="white", fg="#1a73e8")
            self.labels[key].pack(side=tk.LEFT, padx=20)

        self.root.after(1000, self.auto_update)

    def start_crawl(self):
        url = self.entry_url.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Erreur", "Veuillez entrer une URL valide (http ou https)")
            return

        self.crawler = WebCrawler(url, self.update_stats, max_tasks=10)
        self.thread = threading.Thread(target=self.run_async_crawler, daemon=True)
        self.thread.start()

        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.labels["status"].config(text="EN COURS", fg="#f9ab00")

    def run_async_crawler(self):
        asyncio.run(self.crawler.start())

    def stop_crawl(self):
        if self.crawler:
            self.crawler.stop()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.labels["status"].config(text="ARRÊTÉ", fg="#ea4335")

    def update_stats(self):
        with get_db() as db:
            total = db.query(Page).count()
            success = db.query(Page).filter(Page.status == "success").count()
            failed = db.query(Page).filter(Page.status.in_(["failed", "blocked"])).count()

        self.labels["total"].config(text=str(total))
        self.labels["success"].config(text=str(success))
        self.labels["failed"].config(text=str(failed))

    def auto_update(self):
        if self.crawler and self.crawler.running:
            self.update_stats()
        logger.info("Stats updated")  # log chaque mise à jour
        self.root.after(1000, self.auto_update)


if __name__ == "__main__":
    root = tk.Tk()
    app = CrawlerApp(root)
    root.mainloop()
