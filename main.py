from storage.postgres_db import PostgresRepository
import os
from core.config import load_jobs
from extractors.alpaca_broker import AlpacaBroker
from orchestrator.etl_engine import etlEngine
from datetime import datetime,timedelta,timezone
import logging


logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(), logging.FileHandler("etl-engine-logs.log"),],
        )
    logger.info("starting, attempting to connect to postgres server")
    postgres_repo = PostgresRepository()
    logger.info("connected to postgres, attempting to load jobs")


    jobs = load_jobs()
    logger.info("jobs loaded, attempting to connect to alpaca ")


    alpaca_client = AlpacaBroker(
        api_key=os.environ["ALPACA_API_KEY"],
        secret_key=os.environ["ALPACA_API_SECRET"],
        symbols=jobs[0].symbols
    )
    logger.info("alpaca connected, attempting to create engine")

    engine = etlEngine(alpaca_client, postgres_repo)
    logger.info("engine created sucefully, starting run")

    engine.run()
    
    
if __name__ == "__main__":
    
    main()


