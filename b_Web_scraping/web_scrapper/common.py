# va a permitir cargar la configuración cuando iniciemos nuestro software
import yaml

# nos va a servir para cachear la información (esto es importante porque queremos leer a disco y si queremos
# instalar nuestra configuración en varias partes de nuestro código, no queremos leer a discocada vez que queramos
# utilizar la configuración)
__config = None


def config():
    global __config
    if not __config:
        with open("config.yaml", mode="r") as file:
            __config = yaml.safe_load(file)

    return __config
