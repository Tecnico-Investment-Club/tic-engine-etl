#create pool object with info from config
from core.config import POSTGRES_CONFIG
from psycopg2.pool import ThreadedConnectionPool



def main():
    connection_pool = ThreadedConnectionPool(
                            host=POSTGRES_CONFIG.host,
                            port=POSTGRES_CONFIG.port ,
                            database=POSTGRES_CONFIG.database,
                            user=POSTGRES_CONFIG.user,
                            password=POSTGRES_CONFIG.password,
                            minconn=POSTGRES_CONFIG.minimum_connections,
                            maxconn=POSTGRES_CONFIG.maximum_connections,
    )

if __name__ == "__main__":
    main()


