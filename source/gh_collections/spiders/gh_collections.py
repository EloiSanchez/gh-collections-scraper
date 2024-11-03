from typing import Generator

import scrapy

from gh_collections.items import CollectionItem, RepositoryItem


class GHCollectionsSpider(scrapy.Spider):
    name = "gh-collections"
    base_url = "https://github.com"
    collections_url = base_url + "/collections"

    def start_requests(self):
        """
        Initial method called by the spider. Initiates the web scraping from the main
        initial collections page.
        """
        urls = [self.collections_url]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        """
        Parses page of type https://github/collections[?page=X].

        Args:
        - response: A Scrapy response object.

        Returns
        - Generator that produces Scrapy Requests and yields their output.
        """
        page = self.get_response_page(response)

        # If there is a "Load more" button, get the next page of collections and parse
        # it, using this method again
        if self.has_more_pages(response):
            yield scrapy.Request(
                self.collections_url + f"?page={page+1}", callback=self.parse_main_page
            )

        # Parse each of the collection pages using parse_collection method

        # Change line for debugging
        # for article in response.css("article a::attr(href)")[0:1]:
        for article in response.css("article a::attr(href)"):
            yield scrapy.Request(
                self.base_url + article.get(), callback=self.parse_collection
            )

    def parse_collection(self, response):
        """
        Parse collection pages, which are basically collections of repositories.

        Args:
        - response: A Scrapy response object.

        Returns
        - Generator that either:
            produces Scrapy Requests for other collection pages and yields their output.
            or
            returns a collection item with information of the current collection.

        """
        page = self.get_response_page(response)
        collection_url = response.url.split("?")[0]

        # If page has "Load more" button, get next page link and call this method to
        # parse it again
        if self.has_more_pages(response):
            yield scrapy.Request(
                collection_url + f"?page={page+1}", callback=self.parse_collection
            )

        # For each repository listed in collection, retrieve it and send it to the
        # parse_repository method
        for article in response.css("article h1 a::attr(href)"):
            yield scrapy.Request(
                self.base_url + article.get(),
                callback=self.parse_repository,
                meta={"collection_url": collection_url},
            )

        # Generate collection item with data from the collection page and send it to
        # item pipeline
        collection = CollectionItem(
            {
                "url": collection_url,
                "name": response.css("h1.lh-condensed.mb-3::text").get(),
                "description": response.css(
                    "f3.color-fg-muted.lh-condensed.mb-3::text"
                ).get(),
            }
        )
        yield collection

    def parse_repository(self, response):
        """
        Parse repository pages.

        Args:
        - response: A Scrapy response object.

        Returns
        - Generator that yields RepositoryItems to be processed by the item pipeline
        """
        yield RepositoryItem(
            {
                "collection_url": response.meta["collection_url"],
                "url": response.url,
                "name": response.css("div strong a::text").get(),
                "description": response.css("p.f4.my-3::text").get(default="").strip(),
            }
        )

    def parse_directory(self):
        # Iterate over directories/files
        #     If file -> Send to parse_file
        #     If directory -> Send to parse_directory (RECURSIVE)
        pass

    def parse_file(self):
        # Get all data from file page
        # - Language (Crec que necessitem la extensio del arxiu)
        # - Length
        # - Size
        # - Last commit
        # - Last commit user
        pass

    def get_response_page(self, response) -> int:
        """
        Get the current page number of the inputted response. If page is not found in
        url, then it is page number 1

        Args:
        - response: A Scrapy response object.

        Returns
        - int: Numeric value of current page
        """
        page: str = response.url.split("=")[-1]

        if page.isdigit():
            return int(page)
        else:
            return 1

    def has_more_pages(self, response) -> bool:
        """
        Return wether page has a "Load more" pagination button.

        Args:
        - response: A Scrapy response object.

        Returns
        - bool: Whether the current page has or not a "Load more" button for pagination
        """
        # Change line for debugging
        return True if len(response.css("button.ajax-pagination-btn")) else False
        # return False
