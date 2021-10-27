from typing import Dict, Protocol, Optional, Any, List, Union
from collections.abc import MutableMapping

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from app.core.config import Settings

import mmap
import os
import json
import re

from app.core.config import Settings, StorageMode

__all__ = [
    "IStorage",
    "DataCollection",
    "LocalStorage",
    "get_storage",
]


DOCUMENT_VALUE_TYPE = Union[MutableMapping, List[MutableMapping]]

settings = Settings()

firebase_credentials = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
firebase_app = firebase_admin.initialize_app(firebase_credentials)


class DataCollection:
    render_task = "render_task"
    gsheets_tokens = "gsheets_tokens"
    chainlink_tokens = "chainlink_tokens"
    recipes = "recipes"
    ingredients = "ingredients"
    order_responses = "order_responses"
    kitchen_orders = "kitchen_orders"
    metadata = "metadata"
    oven_params = "oven_params"


class IStorage(Protocol):
    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def find(self, filter: MutableMapping, skip: int = 0, limit: int = 0) -> Any:
        """
        Find items matching the filter. This interface is extremely flexible
        but in most cases it only expects the primary key field id and name
        """

    def get(self, filter: MutableMapping) -> Any:
        """
        Get an item from the container. This interface is extremely flexible
        but in most cases it only expects the primary key field id and name
        """

    def set(self, value: DOCUMENT_VALUE_TYPE, filename: Optional[str] = None) -> Any:
        """
        Set and item in the container
        """

    def update(self, filter: MutableMapping, value: DOCUMENT_VALUE_TYPE) -> Any:
        """
        Update an item
        """


class LocalStorage(IStorage):
    """A simple local storage interface.  For testing only."""

    def __init__(
        self,
        collection: str,
    ):
        super().__init__()
        self._id = 0
        self._collection = collection
        self._storage = os.path.join(os.getcwd(), ".cache", self._collection)

    def __enter__(self) -> Any:
        if not os.path.exists(self._storage):
            os.makedirs(self._storage)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def find(self, filter: MutableMapping, skip: int = 0, limit: int = 0) -> Any:
        # TODO: implement a find function
        pass

    def get(self, filter: MutableMapping) -> Any:
        """An inefficient search through all files in the directory."""
        # query_string = json.dumps(dict(filter))
        query_string = re.sub(r"\{|\}", r"", json.dumps(dict(filter)))
        print(query_string)

        search_files = [
            file
            for file in os.listdir(self._storage)
            if os.path.isfile(os.path.join(self._storage, file))
            and not file.startswith(".")  # filter out annoying .DS_store files
        ]

        # Sort the filenames in ascending order
        search_files = sorted(search_files)

        for filename in search_files:
            try:
                with open(os.path.join(self._storage, filename)) as file, mmap.mmap(
                    file.fileno(), 0, access=mmap.ACCESS_READ
                ) as search:
                    if search.find(bytes(query_string, "utf-8")) != -1:
                        json_string = file.read()
                        return json.loads(json_string)
            except FileNotFoundError:
                # swallow errors
                print("not found")
                pass
        return None

    def set(self, value: DOCUMENT_VALUE_TYPE, filename: Optional[str] = None) -> Any:
        """A naive set function that hashes the data and writes the file."""
        # just ignore lists for now
        if isinstance(value, List):
            raise Exception("Not Implemented")
        json_string = json.dumps(dict(value), default=str)
        if filename is None:
            # if we didnt get a filename just pick the first value
            filename = f"{self._collection}-{list(value.values())[0]}"
        with open(f"{os.path.join(self._storage, filename)}.json", "w") as file:
            file.write(json_string)
        return filename

    def update(self, filter: MutableMapping, value: DOCUMENT_VALUE_TYPE) -> Any:
        # TODO: implement an update function
        pass


class FirebaseStorage(IStorage):
    def __init__(self, collection: str):
        super().__init__()
        self._id = 0
        self._collection = collection

        self._client: Any
        self._database: Any

    def __enter__(self) -> Any:
        self._client = firestore.client(app=firebase_app)
        self._database = self._client.collection(self._collection)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def find(self, filter: MutableMapping, skip: int = 0, limit: int = 0) -> Any:
        """
        Find items matching the filter
        """
        # this is a simple example that only considers the first value in the filter
        query = self._database.where(
            list(filter.keys())[0], "==", list(filter.values())[0]
        )
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def get(self, filter: MutableMapping) -> Any:
        """
        Get an item from the container
        """
        # this is a simple example that only considers the value of the first filter key
        document_id = f"{self._collection}-{list(filter.values())[0]}"
        doc = self._database.document(document_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def set(self, value: DOCUMENT_VALUE_TYPE, filename: Optional[str] = None) -> Any:
        """
        Set and item in the container
        """
        if isinstance(value, List):
            # TODO: insert lists
            pass
        else:
            document_id = f"{self._collection}-{list(value.values())[0]}"
            print(f"set: {document_id}")
            self._database.document(document_id).set(value, merge=True)

    def update(self, filter: MutableMapping, value: DOCUMENT_VALUE_TYPE) -> Any:
        """
        Update an item
        """
        if isinstance(value, List):
            # TODO: insert lists
            pass
        else:
            doc = self._database.document(list(filter.values())[0])
            doc.update(value)


def get_storage(collection: str, settings: Settings = Settings()) -> IStorage:
    """Get a storage repository by settings strage mode."""
    if settings.STORAGE_MODE == StorageMode.firebase:
        return FirebaseStorage(collection)

    return LocalStorage(collection)
