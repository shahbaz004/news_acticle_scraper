"""A module to define the NewsArticle dataclass."""
from dataclasses import dataclass


@dataclass
class NewsArticle:
    """
    Represents a news article.

    Attributes:
        title (str): The title of the news article.
        date (str): The date when the news article was published.
        description (str): The description or summary of the news article.
        profile_picture (str): The URL or path to the profile picture associated with the news article.
        search_phrase_count (int): The count of occurrences of the search phrase in the news article.
        contains_money (bool): Indicates whether the news article contains mentions of money.
    """
    title: str
    date: str
    description: str
    profile_picture: str
    search_phrase_count: int
    contains_money: bool

    def to_row(self):
        """
        Convert NewsArticle object to a tuple representing a row in a spreadsheet.

        Returns:
            tuple: A tuple containing the attributes of the NewsArticle object.
        """
        return (
            self.title,
            self.date,
            self.description,
            self.profile_picture,
            self.search_phrase_count,
            self.contains_money
        )