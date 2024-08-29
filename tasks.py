import os
import logging

from RPA.Robocorp.WorkItems import WorkItems

from bot.gothamist_article import Gothamist

OUTPUT_DIR = os.path.join(os.getcwd(), f"output/")

try:
    os.mkdir(OUTPUT_DIR)
except FileExistsError:
    pass

if os.getenv("ROBOCORP_WORKER_ALIAS"):
    work_items = WorkItems()
    work_items.get_input_work_item()
    variables = work_items.get_work_item_payload()
    search_phrase = variables.get("PHRASE")
    category = variables.get("CATEGORY")
else:
    search_phrase = "Pakistan"
    category = "World & Nation"


def task():
    try:
        logging.info("Initializing LA Times automation task.")
        gothamist_article = Gothamist()
        gothamist_article.open_browser('https://gothamist.com/')
        logging.info("Opened browser successfully.")
        gothamist_article.search_phrase(search_phrase)
        gothamist_article.download_news_data_excel()
        logging.info("Search phrase entered successfully.")
        # la_times.sort_by_latest()
        # logging.info("Results sorted by latest.")
        # la_times.select_category(category)
        # logging.info(f"Category '{category}' selected.")
        # la_times.download_news_data_excel()
        # logging.info("News data downloaded and saved to Excel.")
        # la_times.browser.close_all_browsers()
        # logging.info("Closed all browser windows.")
        # logging.info("LA Times automation task completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during LA Times automation task: {e}", exc_info=True)


if __name__ == "__main__":
    task()
