from bs4 import BeautifulSoup


class AdvertisementPageParser:

    def __init__(self):
        self.soup = None

    @property
    def title(self):
        title_tag = self.soup.find('span', attrs={'id': 'titletextonly'})
        if title_tag:
            return title_tag.text
        return None

    @property
    def price(self):
        price_tag = self.soup.find('span', attrs={'class': 'price'})
        if price_tag:
            return price_tag.text
        return None

    @property
    def body(self):
        body_tag = self.soup.find('section', attrs={'id': 'postingbody'})
        if body_tag:
            return body_tag.text.replace('\n\nQR Code Link to This Post\n\n\n', '')
        return None

    @property
    def post_id(self):
        id_selector = 'body > section > section > section > div.postinginfos > p:nth-child(1)'
        id_tag = self.soup.select_one(id_selector)
        if id_tag:
            return id_tag.text.replace('post id: ', '')
        return None

    @property
    def created_time(self):
        time_selector = 'body > section > section > section > div.postinginfos > p:nth-child(2) > time'
        time_created_tag = self.soup.select_one(time_selector)
        if time_created_tag:
            return time_created_tag.attrs['datetime']
        return None

    @property
    def modified_time(self):
        time_selector = 'body > section > section > section > div.postinginfos > p:nth-child(3) > time'
        time_modified_tag = self.soup.select_one(time_selector)
        if time_modified_tag:
            return time_modified_tag.attrs['datetime']
        return None

    @property
    def images(self):
        images_list = self.soup.find_all('img')
        images_sources = set([img.attrs['src'].replace('50x50c', '600x450') for img in images_list])
        return [{'url': src, 'flag': False} for src in images_sources]

    def parse(self, html_doc):
        self.soup = BeautifulSoup(html_doc, 'html.parser')

        data = dict(
            title=self.title, price=self.price,
            body=self.body, post_id=self.post_id,
            created_time=self.created_time, modified_time=self.modified_time,
            images=self.images
        )

        return data
