rm res/test/last-seen.json
rm -rf res/test/local.qdrant
SIDEKICK_CONFIG=res/test/config.ini python utils/qdrant-init.py
SIDEKICK_CONFIG=res/test/config.ini SIDEKICK_SOURCES_CONFIG=res/test/sources.json python sidekick/sources/local.py
