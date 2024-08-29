"""A module to interact with the LA Times website."""
import re
import time
from typing import List

from openpyxl import Workbook

from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement

# from la_times.constants import NEWS_DATA, PROFILE_PIC_NAME
# from la_times.exceptions import NoResultsException
# from la_times.x_paths import LATimesXPaths as XPaths
from bot.locators import Locators
from bot.models import NewsArticle
from selenium.webdriver.chrome.options import Options
from bot.exceptions import NoRecordFoundException


class Gothamist:
    """A class to interact with the LA Times website."""

    def __init__(self):
        """Initialize LATimes instance."""
        self.browser = Selenium()
        self.http = HTTP()
        self.__phrase = None

    def open_browser(self, url: str, headless: bool = False, maximized: bool = True) -> None:
        """
        Open a browser window and navigate to the given URL.

        Args:
            url (str): The URL to navigate to.
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
            maximized (bool, optional): Whether to maximize the browser window. Defaults to True.
        """
        self.browser.open_available_browser(url, headless=headless, maximized=maximized)
        self.browser.wait_until_page_contains_element(Locators.Search.search_button)
        self.browser.click_element_if_visible(Locators.Search.add_close_button)

    def search_phrase(self, phrase: str) -> None:
        """
        Search for a given phrase on the LA Times website.

        Args:
            phrase (str): The phrase to search for.

        Raises:
            NoResultsException: If no results are found for the given phrase.
        """
        self.browser.click_element_when_visible(Locators.Search.search_button)
        self.browser.input_text_when_element_is_visible(Locators.Search.INPUT, phrase)
        self.browser.click_element_when_visible(Locators.Search.SUBMIT)
        self.__phrase = phrase

    def get_news_data(self) -> List[NewsArticle]:
        """
        Get news article data from the search results.

        Returns:
            List[NewsArticle]: A list of NewsArticle objects representing the search results.
        """
        self.browser.wait_until_page_contains_element(Locators.Search.RESULTS, timeout=30)
        article_elements = self.browser.find_elements(Locators.Search.RESULTS)
        result_count = int(self.browser.find_element(Locators.Search.RESULTS_COUNT).text)
        articles: List[NewsArticle] = []
        article_elements = self.load_all_articles(article_elements, result_count)
        for idx, element in enumerate(article_elements):
            img_name = f'output/img{idx}.png'
            title = self.get_field_data(element, Locators.Search.TITLE)
            description = self.get_field_data(element, Locators.Search.DESCRIPTION)
            profile = self.download_profile_picture(element, img_name)
            url = element.find_element(By.XPATH, value='.//a[@class="flexible-link internal card-title-link card-title-link"]').get_attribute('href')
            self.browser.driver.execute_script("window.open('');")
            tabs = self.browser.driver.window_handles
            self.browser.driver.switch_to.window(tabs[1])
            self.browser.go_to(url)
            self.browser.wait_until_page_contains_element(Locators.Search.DATE)
            date = self.extract_date(self.browser.find_element(Locators.Search.DATE).text)
            self.browser.driver.close()
            self.browser.driver.switch_to.window(tabs[0])
            article_data_map = {
                "title": title,
                "date": date,
                "description": description,
                "profile_picture": profile
            }
            self.set_phrase_count_and_money_check(article_data_map)
            articles.append(NewsArticle(**article_data_map))
        return articles

    @staticmethod
    def extract_date(date: str) -> str:
        import re
        from datetime import datetime
        match = re.search(r"\b\w+ \d{1,2}, \d{4}\b", date)
        if match:
            date_str = match.group(0)
            date_obj = datetime.strptime(date_str, "%b %d, %Y")
            formatted_date = date_obj.strftime("%m/%d/%y")
            return formatted_date
        else:
            return ""

    def load_all_articles(self, article_elements, result_count):
        while len(article_elements) != result_count:
            self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.browser.find_element('//button[@aria-label="Load More"]').click()
            article_elements = self.browser.find_elements(Locators.Search.RESULTS)
        return article_elements

    @staticmethod
    def get_field_data(element: WebElement, locator) -> str:
        """
        Get text data from a WebElement based on a locator.

        Args:
            element (WebElement): The WebElement to extract data from.
            locator: Locator to find the desired element.

        Returns:
            str: The text data found.
        """
        try:
            return element.find_element(by=By.XPATH, value=locator).text
        except NoSuchElementException:
            return ''

    def download_profile_picture(self, element: WebElement, file_path) -> str:
        """
        Download the profile picture associated with a news article.

        Args:
            element (WebElement): The WebElement representing the news article.
            file_path (str): The path to save the downloaded profile picture.

        Returns:
            str: The file path where the profile picture is saved.
        """
        try:
            img = element.find_element(by=By.XPATH, value=Locators.Search.PROFILE)
            self.http.download(img.get_attribute('src'), file_path)
            return file_path
        except NoSuchElementException:
            return ''

    def set_phrase_count_and_money_check(self, item: dict) -> None:
        """
        Set the search phrase count and check if the article contains mentions of money.

        Args:
            item (dict): Dictionary containing news article data.
        """
        title_description = f'{item["title"]} {item["description"]}' if item["description"] else item['title']
        item["search_phrase_count"] = re.findall(self.__phrase, title_description, flags=re.IGNORECASE).__len__()

        amount_pattern = r'\$[0-9,]+(\.[0-9]+)?|\b[0-9]+ dollars\b|\b[0-9]+ USD\b'
        item["contains_money"] = 'Yes' if re.search(amount_pattern, title_description) else 'No'

    def download_news_data_excel(self) -> None:
        """Download news article data into an Excel file."""
        workbook = Workbook()
        exception_sheet = workbook.active

        exception_sheet.title = "Articles"
        exception_sheet.append(
            ["Title", "Date", "Description", "ProfilePicture", "Search Phrase Count", "Contains Money"])
        for item in self.get_news_data():
            exception_sheet.append(item.to_row())

        workbook.save('output/news_data.xlsx')
