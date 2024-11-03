from pathlib import Path

import scrapy


class GHCollectionsSpider(scrapy.Spider):
    name = "gh-communities"
    base_url = "https://github.com"
    collections_url = base_url + "/collections"
    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "AUTOTHROTTLE_DEBUG": False,
    }

    def start_requests(self):
        urls = [self.collections_url]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        page = self.get_response_page(response)

        if self.has_more_pages(response):
            yield scrapy.Request(
                self.collections_url + f"?page={page+1}", callback=self.parse_main_page
            )

        for article in response.css("article a::attr(href)"):
            yield scrapy.Request(
                self.base_url + article.get(), callback=self.parse_collection
            )

    def parse_collection(self, response):
        page = self.get_response_page(response)
        collection_url = response.url.split("?")[0]

        if self.has_more_pages(response):
            yield scrapy.Request(
                collection_url + f"?page={page+1}", callback=self.parse_collection
            )

        for article in response.css("article h1 a::attr(href)"):
            yield scrapy.Request(
                self.base_url + article.get(),
                callback=self.parse_repository,
                meta={
                    "collection_title": response.css(
                        "h1.lh-condensed.mb-3::text"
                    ).get(),
                    "collection_description": response.css(
                        "f3.color-fg-muted.lh-condensed.mb-3::text"
                    ).get(),
                },
            )

    def parse_repository(self, response):
        yield {
            "collection_title": response.meta["collection_title"],
            "collection_description": response.meta["collection_description"],
            "repo_description": response.css("p.f4.my-3::text").get().strip(),
            "url": response.url,
        }
        # Get all data from repository page
        # - Name
        # - Stars
        # - Forks
        # - ...

        # Iterate over directories/files
        #     If file -> Send to parse_file
        #     If directory -> Send to parse_directory

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

    def get_response_page(self, response):
        page: str = response.url.split("=")[-1]

        if page.isdigit():
            return int(page)
        else:
            return 1

    def has_more_pages(self, response):
        return False
        # return True if len(response.css("button.ajax-pagination-btn")) else False
