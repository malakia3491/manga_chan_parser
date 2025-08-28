import configparser
from pathlib import Path

class Config():
    def __init__(self, path_to_config):
        self.path_to_config = path_to_config
        self.config = configparser.ConfigParser()
        self.config.read(self.path_to_config)
        
    def get_db_connection(self, is_async=True):
        try:
            str_connection = self.config["Database"]["ASYNC_SQLALCHEMY_DATABASE_URL"] if is_async else self.config["Database"]["SQLALCHEMY_DATABASE_URL"]
            return str_connection
        except Exception as ex:
            raise ex
        
    
    def get_db_path(self):
        try:
            path = self.config["Database"]["ASYNC_SQLITE_DATABASE"]
            return path
        except Exception as ex:
            raise ex    
    
    def get_ddb_path(self):
        try:
            path = self.config["Database"]["TINY_DB"]
            return path
        except Exception as ex:
            raise ex
        
    def get_db_initial_file(self):
        try:
            path = self.config["Database"]["INIT_FILE"]
            return path
        except Exception as ex:
            raise ex