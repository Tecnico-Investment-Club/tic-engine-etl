from storage.postgres_db import PostgresRepository
import os
from core.config import load_jobs
from extractors.alpaca_broker import AlpacaBroker
from orchestrator.etl_engine import etlEngine
from datetime import datetime,timedelta,timezone



def main():
    postgres_repo = PostgresRepository()

    jobs = load_jobs()

    alpaca_client = AlpacaBroker(
        api_key=os.environ["ALPACA_API_KEY"],
        secret_key=os.environ["ALPACA_API_SECRET"],
        symbols=jobs[0].symbols
    )

    engine = etlEngine(alpaca_client, postgres_repo)

    engine.run()
    
    
if __name__ == "__main__":
    main()


