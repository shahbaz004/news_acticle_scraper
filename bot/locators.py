class Locators:
    """
    Defines XPaths used for interacting with the LA Times website.
    """

    class Search:
        """
        XPaths related to search functionality.
        """
        search_button = '//div[@class="search-button"]'
        INPUT = '//input[@class="search-page-input"]'
        RESULTS_COUNT = '//div[@class="search-page-results pt-2"]//strong'
        RESULTS = '//div[@trackingcomponent="Search Results"]'
        SUBMIT = '//input[@class="search-page-input"]//following-sibling::button'
        RESULTS_FOR_TEXT = "//h1[text()='Search results for']"
        TITLE = './/div[@class="h2"]'
        DESCRIPTION = './/div[@class="card-slot"]//p'
        DATE = '//div[@class="byline mb-3 pt-4"]//p[@class="type-caption"]'
        PROFILE = './/img'

        add_close_button = '//button[@title="Close"]'

    class Category:
        """
        XPaths related to category selection.
        """
        TOPICS_SECTION = "//div[@class='search-filter']//p[contains(text(), 'Topics')]/parent::*"
        SEE_ALL_TOPICS = "//span[@class='see-all-text']"
        TOPIC = "//span[text()='{name}']"

    class Sort:
        """
        XPaths related to sorting.
        """
        SELECT_INPUT = "//select[@class='select-input']"

    # class NewsArticle:
    #     """
    #     XPaths related to news articles.
    #     """
    #     TITLE = ".//h3//a[@class='link']"
    #     DATE = ".//p[@class='promo-timestamp']"
    #     DESCRIPTION = ".//p[@class='promo-description']"
    #     PROF_PIC = ".//img"