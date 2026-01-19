import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-muy-secreta'
    
    _db_name = 'egames.db'
    
    _db_path = os.path.join(BASE_DIR, 'database', _db_name)
    
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + _db_path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{_db_path}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class ProdConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    
class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True