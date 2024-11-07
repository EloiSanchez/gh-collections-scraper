import scrapy

from gh_collections.items import CollectionItem, RepositoryItem, FileItem


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
        # for article in response.css("article a::attr(href)")[4:5]:
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
        # for article in response.css("article h1 a::attr(href)")[6:7]:
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
                "description": response.css("div.f3::text").get(),
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

        # Numeric info from the sidebar on the right
        info = response.css("a.Link.Link--muted strong::text")

        # Commit information
        commits = response.css("tbdoy tr td span.fgColor-default::text").get()
        commits = commits.strip()[0] if commits is not None else None

        # Parse each of the files/directories available
        for element in self.get_element_list(response):
            element_name = element.css("::text").get()
            element_description = element.attrib["aria-label"].split(", ")[-1].strip()
            element_url = self.base_url + element.attrib["href"]

            if element_description == "(Directory)":
                yield scrapy.Request(
                    element_url,
                    callback=self.parse_directory,
                    meta={
                        "repository_url": response.url,
                    },
                )

            elif element_description == "(File)":
                yield FileItem(
                    {
                        "url": element_url,
                        "repository_url": response.url,
                        "parent_url": response.url,
                        "name": element_name,
                    }
                )

        # Return RepositoryItem information
        yield RepositoryItem(
            {
                "collection_url": response.meta["collection_url"],
                "url": response.url,
                "name": response.css("div strong a::text").get(),
                "description": response.css("p.f4.my-3::text").get(default="").strip(),
                "stargazers": info[0].get(),
                "watchers": info[1].get(),
                "forks": info[2].get(),
                "commits": commits,
            }
        )

    def parse_directory(self, response):
        for element in self.get_element_list(response):
            element_name = element.css("::text").get()
            element_description = element.attrib["aria-label"].split(", ")[-1].strip()
            element_url = self.base_url + element.attrib["href"]

            if element_description == "(Directory)":
                yield scrapy.Request(
                    element_url,
                    callback=self.parse_directory,
                    meta={
                        "repository_url": response.meta["repository_url"],
                    },
                )

            elif element_description == "(File)":
                yield FileItem(
                    {
                        "url": element_url,
                        "repository_url": response.meta["repository_url"],
                        "parent_url": response.url,
                        "name": element_name,
                    }
                )

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

    def get_element_list(self, response):
        """
        Returns list of files/directories available in the response page.

        Args:
        - response: A Scrapy response object.

        Returns
        - list: List of selectors of the elements
        """
        return response.css(
            "table div.react-directory-filename-column a.Link--primary"
        )[::2]
