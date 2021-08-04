import sys

from crawl import LinkCrawler, DataCrawler, ImageDownloader

if __name__ == '__main__':
    switch = sys.argv[1]

    if switch == 'find_links':
        link_crawler = LinkCrawler(cities=['paris'])
        link_crawler.start(store=True)
    elif switch == 'extract_pages':
        data_crawler = DataCrawler()
        data_crawler.start(store=True)
    elif switch == 'download_images':
        image_downloader = ImageDownloader()
        image_downloader.start(store=True)
