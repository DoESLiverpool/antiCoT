import os

DEBUG = os.getenv('ACOT_DEBUG', 'TRUE').upper() == 'TRUE'
TESTING = False
LOG_LEVEL = os.getenv('ACOT_LOG', 'INFO').upper()
SECRET_KEY = '\x83\xb4hY\xe2=\xf2|\xfd\x92\x97?y\xd4\xe9\xde\xf5g\xdc\xfbeR\x95\xf3'
JSON_AS_ASCII = False
SQLALCHEMY_DATABASE_URI = os.getenv('ACOT_DATABASE_URI', 'sqlite:///antiCoT.db')