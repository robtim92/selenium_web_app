class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'your_default_secret_key'
    # Add other general configurations here (e.g., database URLs)

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'dev_secret_key'

class ProductionConfig(Config):
    SECRET_KEY = 'prod_secret_key'
    # Add production-specific configurations here

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'test_secret_key'
