#create pool object with info from config
from core.config import POSTGRES_CONFIG
from psycopg2.pool import ThreadedConnectionPool
from storage.postgres_db import PostgresRepository
from core.models import Candle
from datetime import datetime,timezone,timedelta


def main():
    

    postgres_repo = PostgresRepository()
    
    
if __name__ == "__main__":
    main()


