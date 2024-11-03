from scrapy import Item, Field


class RepositoryItem(Item):
    collection_url = Field()
    url = Field()
    name = Field()
    description = Field()


class CollectionItem(Item):
    url = Field()
    name = Field()
    description = Field()
