BOT_NAME = "gh_collections"

SPIDER_MODULES = ["gh_collections.spiders"]
NEWSPIDER_MODULE = "gh_collections.spiders"

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

ITEM_PIPELINES = {
    "gh_collections.pipelines.GHCollectionPipeline": 300,
}
