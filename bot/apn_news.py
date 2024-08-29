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

from bot.locators import NytimesLocators
from bot.models import NewsArticle
from selenium.webdriver.chrome.options import Options


class GothamistArticle:
    """A class to interact with the LA Times website."""

    def __init__(self):
        """Initialize LATimes instance."""
        self.browser = Selenium()
        self.http = HTTP()

    def open_browser(self, url: str, headless: bool = False, maximized: bool = True) -> None:
        """
        Open a browser window and navigate to the given URL.

        Args:
            url (str): The URL to navigate to.
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
            maximized (bool, optional): Whether to maximize the browser window. Defaults to True.
        """
        self.browser.open_available_browser(url, headless=headless, maximized=maximized)
        print("here")
        self.browser.wait_until_page_contains_element(ReutersLocators.Search.search_button)
        self.browser.click_element_if_visible(ReutersLocators.Search.add_close_button)

    def search_phrase(self, phrase: str) -> None:
        """
        Search for a given phrase on the LA Times website.

        Args:
            phrase (str): The phrase to search for.

        Raises:
            NoResultsException: If no results are found for the given phrase.
        """
        self.browser.click_button(ReutersLocators.Search.search_button)
        self.browser.input_text_when_element_is_visible(ReutersLocators.Search.INPUT, phrase)
        self.browser.click_button(ReutersLocators.Search.SUBMIT)
        # self.browser.wait_until_page_contains_element(XPaths.Search.RESULTS_FOR_TEXT)
        #
        # if self.browser.does_page_contain_element(XPaths.Search.NO_RESULTS.format(phrase=phrase)):
        #     raise NoResultsException
        #
        # self.__phrase = phrase

    def select_category(self, category: str) -> None:
        """
        Select a category from the LA Times website.

        Args:
            category (str): The category to select.
        """
        topics_section = self.browser.find_element(XPaths.Category.TOPICS_SECTION)
        topics_section.find_element(By.XPATH, value=XPaths.Category.SEE_ALL_TOPICS).click()
        topics_section.find_element(By.XPATH, value=XPaths.Category.TOPIC.format(name=category)).click()
        self.browser.wait_until_page_contains_element(XPaths.Search.RESULTS)

    def sort_by_latest(self) -> None:
        """Sort search results by latest."""
        self.browser.select_from_list_by_value(XPaths.Sort.SELECT_INPUT, '1')
        self.browser.wait_until_page_contains_element(XPaths.Search.RESULTS)

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
            img = element.find_element(by=By.XPATH, value=XPaths.NewsArticle.PROF_PIC)
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

    # def get_news_data(self) -> List[NewsArticle]:
    #     """
    #     Get news article data from the search results.
    #
    #     Returns:
    #         List[NewsArticle]: A list of NewsArticle objects representing the search results.
    #     """
    #     time.sleep(5)
    #     article_elements = self.browser.find_elements(XPaths.Search.RESULTS)
    #
    #     articles: List[NewsArticle] = []
    #     idx = 1
    #     for element in article_elements:
    #         img_name = PROFILE_PIC_NAME.format(name=f'article_{idx}')
    #         article_datSa_map = {
    #             "title": self.get_field_data(element, XPaths.NewsArticle.TITLE),
    #             "date": self.get_field_data(element, XPaths.NewsArticle.DATE),
    #             "description": self.get_field_data(element, XPaths.NewsArticle.DESCRIPTION),
    #             "profile_picture": self.download_profile_picture(element, img_name)
    #         }
    #         self.set_phrase_count_and_money_check(article_data_map)
    #         articles.append(NewsArticle(**article_data_map))
    #         idx += 1
    #     return articles

    def download_news_data_excel(self) -> None:
        """Download news article data into an Excel file."""
        workbook = Workbook()
        exception_sheet = workbook.active

        exception_sheet.title = "Articles"
        exception_sheet.append(
            ["Title", "Date", "Description", "ProfilePicture", "Search Phrase Count", "Contains Money"])
        for item in self.get_news_data():
            exception_sheet.append(item.to_row())

        workbook.save(NEWS_DATA)
