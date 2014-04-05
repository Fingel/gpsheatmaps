import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['zip', 'gpx'])

try:
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
except KeyError:
    pass

try:
    from local_settings import *
except ImportError:
    pass
