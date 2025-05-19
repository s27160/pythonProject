from celery import shared_task
import asyncio
import logging
from .services.scraper_service import fetch_tenders, process_tender

logger = logging.getLogger(__name__)

@shared_task
def run_periodic_scraper() -> None:
    logger.info("Starting periodic tender scraper")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        tenders = loop.run_until_complete(fetch_tenders(days_back=30, max_pages=10))

        if not tenders:
            logger.warning("No tenders fetched from the API")
            return

        logger.info(f"Processing {len(tenders)} tenders")

        processed_count = 0
        for tender_data in tenders:
            result = loop.run_until_complete(process_tender(tender_data))
            if result:
                processed_count += 1

        logger.info(f"Successfully processed {processed_count} out of {len(tenders)} tenders")

    except Exception as e:
        logger.error(f"Error in periodic scraper: {str(e)}")

    finally:
        loop.close()
        logger.info("Periodic tender scraper completed")
