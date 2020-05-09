import argparse
import logging
from urllib.parse import urlparse
import pandas as pd
import hashlib
import nltk # nltk: Ayuda a trabjar con lenguage natural
from nltk.corpus import stopwords
# stopwords : son palabras que no añaden ningún tipo de analisis posterior, por ejemplo "el, la",
# palabras que se utilizan mucho en el lenguage pero no ayudan a determinar que está sucedienendo
# dentro de nuestro análisis de texto

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
    df = _tokenize_column(df, "title", "spanish")
    df = _tokenize_column(df, "body", "spanish")
    df = _remove_duplicate_entries(df, "title")
    df = _drop_rows_with_missing_values(df)

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


def _tokenize_column(df, column_name, language):
    # una función que nos va a generar las transformaciones en la columna deseada (primero título y luego enn el body)
    logger.info("Tokenizing column {}".format(column_name))
    # si nunca hemos corrido nltk, nos va a pedir que bajemos los archivos adicionales, instalarla no
    # es suficiente porque es una librería enorme, entonces la primera vez que corremos esta librería,
    # nos pide que ajemos las librerías adicionales, se debe colocar el siguiente código
    try:
        nltk.data.find("tokenizers/punkt")
        # punkt: librería para poder tokenizar, es decir dividir en palabras
    except LookupError:
        nltk.download("punkt")

    try:
        nltk.data.find("stopwords")
    except LookupError:
        nltk.download("stopwords")
    finally:
        stop_words = set(stopwords.words(language))
        # los stop_words: vienen en minúsuculas

    tokenize_column = (df
                       .dropna() # Eliminamos las que no tienen datos, de lo contrario nltk existirá un error.
                       .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
                       .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens))) # Eliminar palabras que no sean alfanuméricas
                       .apply(lambda tokens: list(map(lambda token: token.lower(), tokens))) # convertir todos los tokesns a lowerCase
                       .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list))) # Eliminar las palabras que sean stop_words
                       .apply(lambda valid_word_list: len(valid_word_list)) # obtener la longitud que tiene cada una de estas listas
                       )

    df["n_tokens_{}".format(column_name)] = tokenize_column

    return df


def _remove_duplicate_entries(df, column_name):
    logger.info("Removing duplicate entries")
    # keep: que tome los valores del primer duplicado o el último (last).
    # inplace = realizamos la modificación directamente.
    df.drop_duplicates(subset=[column_name], keep="first", inplace=True)

    return df


def _drop_rows_with_missing_values(df):
    logger.info("Dropping rows with missing values")

    return df.dropna()


def _save_df(df, filename):
    filename = "{}_cleaned.csv".format(filename[:-4])
    logger.info("Saving new file at location {}".format(filename))
    df.to_csv(filename, encoding="utf-8-sig")


if __name__ == "__main__":
    # Para llamar al archivo:
    #   (python newspaper.py elpais_2020_05_08_articles.csv) --> Aclarando que debo correr el ambiente de conda

    # Le preguntamos al usuario cuál va a ser el archivo con el que quiere trabajar
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        help="The path to the dirty data",
                        type=str)

    arg = parser.parse_args()
    df = main(arg.filename)

    print(df)

    _save_df(df, arg.filename)
