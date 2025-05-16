class DevelopmentConfig:
  SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Cam.110196@localhost/mechanic_db'
  DEBUG = True
  CACHE_TYPE = "SimpleCache"
  
class TestingConfig:
  pass

class ProductionConfig:
  pass

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'