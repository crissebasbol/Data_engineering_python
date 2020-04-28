import argparse
import logging
from common import config

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def _news_scraper(news_sited_uid):
    host = config()["news_sites"][news_sited_uid]["url"]

    logging.info("Beginning scraper for {}".format(host))


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
