from celery import shared_task
import asyncio

@shared_task
def run_periodic_scraper():
    from .services.scraper_service import fetch_tenders, process_tender

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_scraper():
        print("Rozpoczynam okresowe pobieranie ofert...")

        return await fetch_tenders()

    return asyncio.run(run_scraper())


