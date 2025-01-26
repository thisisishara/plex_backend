from __future__ import annotations

from typing import Any

from pymongo import ASCENDING
from pymongo import MongoClient
from sanic.log import logger

from plex.core.constants import MONGO_DB
from plex.core.constants import MONGO_URI
from plex.core.constants import SOURCE_COLLECTION


class MongoMigrations:
    def __init__(
        self,
        connection_string: str = MONGO_URI,
        database_name: str = MONGO_DB,
    ) -> None:
        self._client = MongoClient(connection_string)
        self._db = self._client[database_name]

    def __enter__(self) -> MongoMigrations:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        if self._client:
            self._client.close()
            logger.debug("MongoDB client connection closed.")

    def _create_collection(self, collection_name: str) -> None:
        if collection_name not in self._db.list_collection_names():
            self._db.create_collection(collection_name)
            logger.debug(f"Collection '{collection_name}' created.")

    def _create_index(
        self,
        collection_name: str,
        index_configs: list[tuple[str, int]],
        unique: bool = False,
    ) -> None:
        collection = self._db[collection_name]
        index_name = "_".join(key for key, _ in index_configs)
        if index_name not in collection.index_information():
            collection.create_index(index_configs, unique=unique, name=index_name)
            logger.debug(
                f"Index '{index_name}' created on collection '{collection_name}'.",
            )

    def run(self) -> None:
        collections_and_indexes = [
            {
                "collection": SOURCE_COLLECTION,
                "index_configs": [
                    ("file_name", ASCENDING),
                ],
                "unique": True,
            },
        ]

        collections = {_["collection"] for _ in collections_and_indexes}
        for collection in collections:
            try:
                self._create_collection(collection_name=collection)

            except Exception as e:
                logger.exception("Database migrations failed due to a collection creation error")
                raise e

        for _ in collections_and_indexes:
            collection_name = _["collection"]
            index_configs = _["index_configs"]
            unique = _.get("unique", False)

            if not index_configs:
                continue

            try:
                self._create_index(
                    collection_name=collection_name,
                    index_configs=index_configs,
                    unique=unique,
                )

            except Exception as e:
                logger.error("Database migrations failed due to an index creation error")
                raise e
