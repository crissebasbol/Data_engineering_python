import argparse
import logging
from urllib.parse import urlparse
import pandas as pd
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(filename):
    logger.info("Starting cleaning process")

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _fill_missing_bodies(df)
    df = _generate_uids_for_rows(df)
    df = _remove_new_lines_from_body(df)

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


def _fill_missing_bodies(df):
    logger.info("Filling missing bodies")
    missing_bodies_mask = df["body"].isna()
    # en el body vamos a colocar el texto del último pedazo de la url
    # [^/]-->queremos que haga match hasta que no encuentre una diagonal adicional
    # [^/]+-->que esto puede suceder una o más veces
    # ([^/]+)$ --> vamos ir hasta el final de nuestro string
    # (?P<missing_bodies>[^/]+)$ --> colocar un nombre al grupo

    # applymap nos permite generar un mapa de un valor a otro, es decir una transformación

    missing_bodies = (df[missing_bodies_mask]["article_links"]
                      .str.extract(r"(?P<missing_bodies>[^/]+)$")
                      .applymap(lambda body: body.split("-"))
                      .applymap(lambda body_word_list: " ".join(body_word_list))
                      )
    df.loc[missing_bodies_mask, "body"] = missing_bodies.loc[:, "missing_bodies"]

    return df


def _generate_uids_for_rows(df):
    logger.info("Generating uids for eachs row")
    # hashlib --> normalmente se utiliza para operaciones criptográficas, pero la vamos a utilziar para generar un hash
    #            de la URL, de tal manera que tengamos un número único que mapee siempre a esa URL

    # axis=0 -->columbas
    # axis=1 -->filas

    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row["article_links"].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )
    df["uid"] = uids

    # inplace --> le indica que queremos modificar directamente nuestra tabla
    df.set_index("uid", inplace=True)

    return df


def _remove_new_lines_from_body(df):
    logger.info("Removing new lines from body")
    strippped_body = (df
                      .apply(lambda row: row["body"], axis=1)
                      .apply(lambda body: list(body))
                      .apply(lambda letters: list(map(lambda letter: letter.replace("\n", " "), letters)))
                      .apply(lambda letters: list(map(lambda letter: letter.replace("\r", " "), letters)))
                      .apply(lambda letters: "".join(letters))
                      )
    df["body"] = strippped_body

    return df


def _save_df(df, filename):
    logger.info("Saving new file")
    filename = "{}_cleaned.csv".format(filename[:-4])
    df.to_csv(filename, encoding="utf-8-sig")


if __name__ == "__main__":
    # Le preguntamos al usuario cuál va a ser el archivo con el que quiere trabajar
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        help="The path to the dirty data",
                        type=str)

    arg = parser.parse_args()
    df = main(arg.filename)

    print(df)

    _save_df(df, arg.filename)
