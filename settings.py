from pathlib import Path, os


BASE_DIR = Path(__file__).parent


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE') or \
                              f"sqlite:///{BASE_DIR}/database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
