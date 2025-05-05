class DevelopmentConfig:
  SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Cam.110196@localhost/mechanic_db'
  DEBUG = True
  
class TestingConfig:
  pass

class ProductionConfig:
  pass
