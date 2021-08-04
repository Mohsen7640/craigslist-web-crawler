import requests

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

from config import BASE_LINK, STORAGE_TYPE
from parser import AdvertisementPageParser
from storage import MongoStore, FileStore


class Crawler(ABC):

    def __init__(self, *args, **kwargs):
        self.storage = self.__set_storage_type()

        super().__init__(*args, **kwargs)

    @staticmethod
    def __set_storage_type():
        """Strategy Pattern"""
        if STORAGE_TYPE == 'mongo':
            return MongoStore()
        return FileStore()

    @staticmethod
    def get_page(link, stream=False):
        try:
            response = requests.get(link, stream=stream)
        except requests.HTTPError:
            return None
        return response

    @abstractmethod
    def store(self, data, **kwargs):
        pass

    @abstractmethod
    def start(self, store=False):
        pass


class LinkCrawler(Crawler):

    def __init__(self, cities, link=BASE_LINK, *args, **kwargs):
        self.cities = cities
        self.link = link

        super().__init__(*args, **kwargs)

    @staticmethod
    def get_links(html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup.find_all('a', attrs={'class': 'hdrlnk'})

    def start_crawl_city(self, url):
        """
        Add pagination to script
        :param url:
        :return:
        """
        start = 0
        crawl = True

        adv_links = list()
        while crawl:
            respond = self.get_page(url + str(start))
            new_links = self.get_links(respond.text)
            adv_links.extend(new_links)
            start += 120

            crawl = bool(len(new_links))

        return adv_links

    def store(self, data, **kwargs):
        self.storage.store(data, **kwargs)

    def start(self, store=False):
        adv_links = list()
        for city in self.cities:
            links = self.start_crawl_city(self.link.format(city))
            print(f'{city} total ads: {len(links)}')
            adv_links.extend(links)
        if store:
            links = [{'url': link.get('href'), 'flag': False} for link in
                     adv_links]
            filename = 'links'
            collection_name = 'advertisement_links'
            self.store(
                data=links,
                filename=filename,
                collection_name=collection_name
            )
        return adv_links


class DataCrawler(Crawler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.links = self.__load_links()
        self.parser = AdvertisementPageParser()

    def __load_links(self):
        filename = 'links'
        collection_name = 'advertisement_links'
        filter_data = {'flag': False}
        return self.storage.load(
            filename=filename,
            collection_name=collection_name,
            filter_data=filter_data
        )

    def store(self, data, **kwargs):
        self.storage.store(data, **kwargs)

    def start(self, store=False):
        for link in self.links:
            response = self.get_page(link['url'])
            data = self.parser.parse(response.text)

            if store:
                filename = f'adv/{data.get("post_id", "sample")}'
                collection_name = 'advertisement_data'
                self.store(
                    data=data,
                    filename=filename,
                    collection_name=collection_name
                )
                print(data['post_id'])

            collection_name = 'advertisement_links'
            self.storage.update_status(
                key='_id',
                data=link,
                collection_name=collection_name
            )


class ImageDownloader(Crawler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.advertisements = self.__load_advertisements()

    def __load_advertisements(self):
        collection_name = 'advertisement_data'
        filter_data = None
        return self.storage.load(
            collection_name=collection_name,
            filter_data=filter_data
        )

    @staticmethod
    def save_to_disk(response, filename):
        with open(f'fixtures/images/{filename}.jpg', mode='wb') as file_handler:
            for chunk in response.iter_content(chunk_size=1024):
                file_handler.write(chunk)

        print(f'Download image {filename} completed...')
        return filename

    def store(self, data, **kwargs):
        post_id = kwargs['post_id']
        img_number = kwargs['img_number']

        filename = f'{post_id}-{img_number}'
        return self.save_to_disk(data, filename)

    def start(self, store=True):
        for advertisement in self.advertisements:
            counter = 1
            for image in advertisement['images']:
                response = self.get_page(link=image['url'])

                if store:
                    self.store(
                        data=response,
                        post_id=advertisement['post_id'],
                        img_number=counter
                    )
                counter += 1
