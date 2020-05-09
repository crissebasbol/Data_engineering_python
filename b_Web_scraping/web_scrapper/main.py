import argparse
import datetime
import csv
import logging
import news_page_objects as news
import re  # for regular expressions
from common import config

from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

logging.basicConfig(level=logging.INFO)

# r --> indica a python que es un string raw
# ^ --> nos da el inicio de la palabra
# ? --> opcional la s
# .+ --> por lo menos una o más letras
# $ terminamos el patrón

is_well_formed_link = re.compile(r"^https?://.+/.+$")  # https://example.com/some-text
is_root_path = re.compile(r"^/.+$")  # /some-text
logger = logging.getLogger(__name__)


def _news_scraper(news_site_uid):
    host = config()["news_sites"][news_site_uid]["url"]

    logging.info("Beginning scraper for {}".format(host))
    home_page = news.HomePage(news_site_uid, host)

    articles = []
    for link in home_page.article_links:
        article = _fetch_article(news_site_uid, link)

        if article:
            logger.info("Article fetched!!")
            articles.append(article)
            print(article.title)

    print(len(articles))
    _save_articles(news_site_uid, articles)


def _save_articles(news_site_uid, articles):
    now = datetime.datetime.now().strftime("%Y_%m_%d")
    out_file_name = "{news_site_uid}_{datetime}_articles.csv".format(
        news_site_uid=news_site_uid,
        datetime=now
    )
    csv_headers = list(filter(lambda property: not property.startswith("_"), dir(articles[0])))
    with open(out_file_name, mode="w+", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, prop))for prop in csv_headers]
            writer.writerow(row)


def _fetch_article(news_site_uid, link):
    logger.info("Start fetching article at {}".format(link))

    article = None

    try:
        article = news.ArticlePage(news_site_uid, _build_link(link))
    # except (HTTPError, MaxRetryError) as e:
    except:
        # HTTPErrorr --> cuando no se ha encontrado la página
        # MaxRetryError --> estoy eliminadno la posibildad de que se vaya al infinito tratando de seguir la URL
        logger.warning("Error while fetching the article", exc_info=False)
        # exc_info=False --> para que no me muestre el error

    if article and not article.body and not article.title:
        logger.warning("Invalid article. There is no body")
        return None

    return article


def _build_link(link):
    if is_well_formed_link.match(link):
        return link


if __name__ == "__main__":
    # parecido a ClI, solo que un poco más fácil
    parser = argparse.ArgumentParser()

    news_site_choices = list(config()["news_sites"].keys())
    # Le añadimos opciones
    parser.add_argument("news_site",
                        help="The new site that you want to scrape",
                        type=str,
                        choices=news_site_choices)

    # parsear
    args = parser.parse_args()
    _news_scraper(args.news_site)
