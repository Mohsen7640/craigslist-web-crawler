import json

from abc import ABC, abstractmethod

from mongo import MongoDatabase


class Storage(ABC):

    @abstractmethod
    def store(self, data, **kwargs):
        pass

    @abstractmethod
    def load(self, **kwargs):
        pass


class MongoStore(Storage):

    def __init__(self):
        self.mongo = MongoDatabase()

    def store(self, data, **kwargs):
        collection_name = kwargs['collection_name']
        # return or create and return collection
        collection = getattr(self.mongo.database, collection_name)
        if isinstance(data, list) and len(data) > 1:
            collection.insert_many(data)
        else:
            collection.insert_one(data)

    def load(self, **kwargs):
        filter_data = kwargs['filter_data']
        collection_name = kwargs['collection_name']
        collection = getattr(self.mongo.database, collection_name)
        if filter_data is None:
            return collection.find()
        return collection.find(filter_data)

    def update_status(self, **kwargs):
        key = kwargs['key']
        data = kwargs['data']
        collection_name = kwargs['collection_name']
        collection = getattr(self.mongo.database, collection_name)
        collection.find_one_and_update(
            {key: data[key]},
            {'$set': {'flag': True}}
        )


class FileStore(Storage):

    def store(self, data, **kwargs):
        filename = kwargs['filename']
        with open(file=f'fixtures/{filename}.json',
                  mode='w') as file_handler:
            file_handler.write(json.dumps(data))
        print(f'Saved fixtures/{filename}.json')

    def load(self, **kwargs):
        filename = kwargs['filename']
        with open(file=f'fixtures/{filename}.json', mode='r') as file_handler:
            links = json.loads(file_handler.read())

        return links

    def update_status(self, **kwargs):
        pass
