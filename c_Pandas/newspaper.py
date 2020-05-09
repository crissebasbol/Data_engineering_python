import argparse
import logging
from urllib.parse import urlparse
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(filename):
    logger.info("Starting cleaning process")

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)

    return df


def _read_data(filename):
    logger.info("Reading file {}".format(filename))

    return pd.read_csv(filename, encoding="ISO-8859-1")


def _extract_newspaper_uid(filename):
    logger.info("Extracting newspaper uid")
    newspaper_uid = filename.split("_")[0]
    logger.info("Newspaper uid detected: {}".format(newspaper_uid))

    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info("Filling newspaper_uid column with {}".format(newspaper_uid))
    df["newspaper_uid"] = newspaper_uid

    return df


def _extract_host(df):
    logger.info("Extracting host from urls")
    df["host"] = df["article_links"].apply(lambda article_links: urlparse(article_links).netloc)

    return df


if __name__ == "__main__":
    # Le preguntamos al usuario cuál va a ser el archivo con el que quiere trabajar
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        help="The path to the dirty data",
                        type=str)

    arg = parser.parse_args()
    df = main(arg.filename)

    print(df)
