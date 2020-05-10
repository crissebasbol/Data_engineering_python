import argparse
import logging
import pandas as pd
from article import Article
from base import Base, Engine, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(filename):
    # configurar sql
    Base.metadata.create_all(Engine)  # permite generar nuestro scheme en nuestra base de datos
    session = Session()  # Inicializar la sesión
    articles = pd.read_csv(filename)  # Leemos nuestros artículos con pandas

    # iterrows : es un método de pandas que permite generar un loop adentro de cada una de nuestras
    # filas de nuestro DataFrame
    for index, row in articles.iterrows():
        logger.info("Loading article uid {} into DB".format(row["uid"]))
        article = Article(row["uid"],
                          row["body"],
                          row["host"],
                          row["newspaper_uid"],
                          row["n_tokens_body"],
                          row["n_tokens_title"],
                          row["title"],
                          row["article_links"])

        session.add(article)  # esto nos mete nuestro artículo dentro de la base de datos

    session.commit()
    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        help="The file you want to load into the db",
                        type=str)

    args = parser.parse_args()

    main(args.filename)
