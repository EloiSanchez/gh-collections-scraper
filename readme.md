# GitHub Collections Scraper

## Setup

Create virtual environment and activate.

Install Scrapy (pip, conda...).

## How to use

```shell
scrapy runspider source/gh_collections_scraper/spiders/gh_collections.py -O results/collection.json
```

This will start the scraping and save the results in `results/collections.json`.
