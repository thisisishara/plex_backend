from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from plex.core.constants import SOURCE_COLLECTION
from plex.core.types import SourceFile
from plex.shared.exceptions.source import SourceFileExistsError
from plex.shared.exceptions.source import SourceFileNotFoundError


class SourceCollection:
    @classmethod
    async def retrieve_all(cls, app: Sanic) -> list[SourceFile]:
        collection: AsyncIOMotorCollection = app.ctx.motor_db[SOURCE_COLLECTION]
        res = collection.find()
        if not res:
            return []

        sources = [source async for source in res]
        return [
            {
                "file_name": source["file_name"],
                "file_size": source["file_size"],
                "content": source["content"],
                "content_hash": source["content_hash"],
                "timestamp": source["timestamp"],
            }
            for source in sources
        ]

    @classmethod
    async def retrieve_all_names(cls, app: Sanic) -> list[SourceFile]:
        collection: AsyncIOMotorCollection = app.ctx.motor_db[SOURCE_COLLECTION]
        res = collection.find()
        if not res:
            return []

        sources = [source async for source in res]
        return [source["file_name"] for source in sources]

    @classmethod
    async def retrieve_one(cls, file_name: str, app: Sanic) -> SourceFile:
        collection: AsyncIOMotorCollection = app.ctx.motor_db[SOURCE_COLLECTION]
        res = await collection.find_one({"file_name": file_name})
        if not res:
            raise SourceFileNotFoundError(f"There is no source file named '{file_name}'")

        source = dict(res)
        return {
            "file_name": source["file_name"],
            "file_size": source["file_size"],
            "content": source["content"],
            "content_hash": source["content_hash"],
            "timestamp": source["timestamp"],
        }

    @classmethod
    async def add_one(cls, source_data: SourceFile, app: Sanic) -> SourceFile:
        collection: AsyncIOMotorCollection = app.ctx.motor_db[SOURCE_COLLECTION]

        try:
            existing_source = await SourceCollection.retrieve_one(file_name=source_data["file_name"], app=app)

        except SourceFileNotFoundError:
            existing_source = None

        if existing_source:
            if existing_source["content_hash"] == source_data["content_hash"]:
                raise SourceFileExistsError(
                    f"The source file '{source_data['file_name']}' already exists with identical content",
                )

        await collection.update_one(
            filter={"file_name": source_data["file_name"]},
            update={"$set": source_data},
            upsert=True,
        )

        return {
            "file_name": source_data["file_name"],
            "file_size": source_data["file_size"],
            "content": source_data["content"],
            "content_hash": source_data["content_hash"],
            "timestamp": source_data["timestamp"],
        }
