import yaml
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"

def get_settings():
    with open("./config.yml", "r") as file:
        config = yaml.safe_load(file)
    db_config = config['db']
    database_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    return Settings(database_url=database_url)