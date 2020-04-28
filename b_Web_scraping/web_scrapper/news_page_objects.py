import requests
import bs4
import validators
from common import config


class HomePage:
    # va a representar la página principal de nuestra web
    def __init__(self, news_site_uid, url):
        self._config = config()["news_sites"][news_site_uid]
        self._queries = self._config["queries"]
        self._html = None

        self._visit(url)

    @property
    def article_links(self):
        link_list = []
        for link in self._select(self._queries["homepage_article_links"]):
            if link and link.has_attr("href"):
                if not validators.url(link["href"]):
                    link_list.append(self._config["url"]+link["href"])

        return set(link for link in link_list)

    def _select(self, query_string):
        return self._html.select(query_string)

    def _visit(self, url):
        response = requests.get(url)
        response.encoding = "utf-8"

        # nos permite lanzar un error si la solicitud no fue concluida correctamente
        response.raise_for_status()
        self._html = bs4.BeautifulSoup(response.text, "html.parser")
