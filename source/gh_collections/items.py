from scrapy import Item, Field


class RepositoryItem(Item):
    collection_url = Field()
    url = Field()
    name = Field()
    description = Field()
    stargazers = Field()
    watchers = Field()
    forks = Field()
    commits = Field()


class CollectionItem(Item):
    url = Field()
    name = Field()
    description = Field()


class FileItem(Item):
    url = Field()
    name = Field()
    repository_url = Field()
    parent_url = Field()
