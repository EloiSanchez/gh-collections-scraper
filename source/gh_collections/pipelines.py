from itemadapter.adapter import ItemAdapter
from scrapy.exporters import CsvItemExporter

from gh_collections.items import CollectionItem, RepositoryItem


class GHCollectionPipeline(object):

    def open_spider(self, spider):
        self.exporters = {}

        collection_file = open("../results/collections.csv", "wb")
        collection_exporter = CsvItemExporter(collection_file)
        collection_exporter.start_exporting()
        self.exporters["collections"] = [collection_exporter, collection_file]

        repository_file = open("../results/repositories.csv", "wb")
        repository_exporter = CsvItemExporter(repository_file)
        repository_exporter.start_exporting()
        self.exporters["repositories"] = [repository_exporter, repository_file]

    def process_item(self, item, spider):
        if isinstance(item, RepositoryItem):
            self.exporters["repositories"][0].export_item(item)

        if isinstance(item, CollectionItem):
            self.exporters["collections"][0].export_item(item)

        return item

    def close_spider(self, spider):
        for exporter, csv_file in self.exporters.values():
            exporter.finish_exporting()
            csv_file.close()