from pydantic_settings import BaseSettings 

class Settings(BaseSettings):
    ODOO_URL: str = "http://localhost:8069"
    ODOO_DB: str = "PFA_DB"
    ODOO_USERNAME: str = "ismo8gmr@gmail.com"
    ODOO_PASSWORD: str # required - set via env

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
