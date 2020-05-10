import datetime
import logging
import subprocess
# subprocess:
#    Permite manipular directamente archivos del terminal (es }como si tuvieramos la terminal directamente en python)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

news_sites_uids = ["eluniversal", "elpais"]


def main():
    _extract()
    _transform()
    _load()


def _extract():
    logger.info("Starting extract process")
    for news_sites_uid in news_sites_uids:
        # cwd--> que ejecute lo que he exrito antes dentro de la dirección que le mando
        subprocess.run(["python", "main.py", news_sites_uid], cwd=".\\extract")
        # ahora vamos a mover los archivos que se generaron
        # "." --> que queremos que comience a partir de este directorio
        # "-name", "{}*" --> queremos que encuentre algo con un cierto patrón (* el asterisco significa con lo que sea)
        # "-exect" --> que ejecute algo por cada uno de los archivos que encuentre
        # "mv" --> que los mueva
        # "{}" --> el nombre del archivo
        # ";" --> porque find nos obliga a terminar con un ;
        # el siguiente comando es para linux o mac
        # subprocess.run(["find", ".", "-name", "{}*".format(news_sites_uid), "-exec", "mv", "{}",
        #                "../transform/{}_.csv".format(news_sites_uid), ";"], cwd="./extract")
        # Para windwos
        subprocess.run(["copy", "{}_{}*".format(news_sites_uid, now),
                        "..\\transform\\{}_{}_.csv".format(news_sites_uid, now)], shell=True,
                       cwd="./extract")
        print("*"*50)


def _transform():
    logger.info("Starting transform process")
    for news_sites_uid in news_sites_uids:
        dirty_data_filename = "{}_{}_.csv".format(news_sites_uid, now)
        clean_data_filename = "{}_cleaned.csv".format(dirty_data_filename[:-4])
        subprocess.run(["python", "main.py", dirty_data_filename], cwd=".\\transform")
        subprocess.run(["rm", dirty_data_filename], shell=True, cwd=".\\transform")
        subprocess.run(["mv", clean_data_filename, "..\\load\\{}.csv".format(news_sites_uid)], shell=True,
                       cwd=".\\transform")
    print("*" * 50)


def _load():
    logger.info("Starting load process")
    for news_sites_uid in news_sites_uids:
        clean_data_filename = "{}.csv".format(news_sites_uid)
        subprocess.run(["python", "main.py", clean_data_filename], cwd=".\\load")
        subprocess.run(["rm", clean_data_filename], shell=True, cwd="./load")
    print("*" * 50)


if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y_%m_%d")
    main()
