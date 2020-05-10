from sqlalchemy import create_engine
# permite tener acceso a las funcionalidades de orm (object relational mapper: nos permite
# trabajar con objetos de python en lugar de querys de SQL directamente) de sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# le decimos a sqlalchemy que queremos usar sqlite
Engine = create_engine("sqlite:///newspaper.db")

Session = sessionmaker(bind=Engine)

# Generamos la clase base de la cual van a extender todos nuestros modelos
Base = declarative_base()
