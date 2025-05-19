import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from scraper.operations import PlaywrightScraper
from web.modules.tenders.models import PublicTender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

AGENTS: List[str] = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.3',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.3',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.153 Mobile/15E148 Safari/604.1'
]

semaphore = asyncio.Semaphore(8)

BASE_API_URL = "https://ezamowienia.gov.pl/mo-board/api/v1/Board/Search"

LEGAL_SERVICES_CPV = "79100000-5"


async def get_random_agent() -> str:
    return random.choice(AGENTS)


async def build_api_url(
    cpv_code: str = LEGAL_SERVICES_CPV,
    days_back: int = 7,
    page_number: int = 1,
    page_size: int = 100
) -> str:
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00.000Z")

    url = (
        f"{BASE_API_URL}?"
        f"publicationDateFrom={from_date}&"
        f"cpvCode={cpv_code}&"
        f"SortingColumnName=PublicationDate&"
        f"SortingDirection=DESC&"
        f"PageNumber={page_number}&"
        f"PageSize={page_size}"
    )

    return url


async def fetch_tenders(
    cpv_code: str = LEGAL_SERVICES_CPV,
    days_back: int = 7,
    max_pages: int = 5
) -> List[Dict[str, Any]]:
    all_tenders: List[Dict[str, Any]] = []

    async with PlaywrightScraper() as scraper:
        page_number = 1
        total_pages = 1  # Will be updated after the first request

        while page_number <= total_pages and page_number <= max_pages:
            url = await build_api_url(
                cpv_code=cpv_code,
                days_back=days_back,
                page_number=page_number,
                page_size=100
            )

            async with semaphore:
                agent = await get_random_agent()
                logger.info(f"Fetching page {page_number} of tenders...")

                data = await scraper.fetch_json(url, agent)

                if not data:
                    logger.error(f"Failed to fetch page {page_number}")
                    break

                # Update total pages from the response
                total_pages = data.get('totalPages', 1)

                # Extract the items
                items = data.get('items', [])
                all_tenders.extend(items)

                logger.info(f"Fetched {len(items)} tenders from page {page_number}")

                # Move to the next page
                page_number += 1

                # Add a small delay to avoid rate limiting
                await asyncio.sleep(1)

    logger.info(f"Fetched a total of {len(all_tenders)} tenders")
    return all_tenders


async def process_tender(tender_data: Dict[str, Any]) -> Optional[PublicTender]:
    try:
        tender_id = tender_data.get('tenderId')
        announcement_number = tender_data.get('noticeNumber', '')
        announcement_type = tender_data.get('noticeType', '')
        order_name = tender_data.get('orderObject', '')
        contracting_authority = tender_data.get('organizationName', '')
        description = tender_data.get('orderObject', '')
        authority_city = tender_data.get('organizationCity', '')
        authority_region = tender_data.get('organizationProvince', '')

        publication_date_str = tender_data.get('publicationDate', '')
        submission_deadline_str = tender_data.get('submittingOffersDate', '')

        publication_date = datetime.fromisoformat(publication_date_str.replace('Z', '+00:00')).date() if publication_date_str else datetime.now().date()
        submission_deadline = datetime.fromisoformat(submission_deadline_str.replace('Z', '+00:00')).date() if submission_deadline_str else None

        mo_identifier = tender_data.get('moIdentifier', '')
        details_url = f"https://ezamowienia.gov.pl/mo-client-board/bzp/notice-details/{mo_identifier or tender_id}"

        client_type = tender_data.get('clientType')
        order_type = tender_data.get('orderType')
        tender_type = tender_data.get('tenderType')
        notice_type_ted = tender_data.get('noticeTypeTed')
        notice_type_display_name = tender_data.get('noticeTypeDisplayName')
        bzp_number = tender_data.get('bzpNumber')
        is_tender_amount_below_eu = tender_data.get('isTenderAmountBelowEU')
        cpv_code = tender_data.get('cpvCode')
        procedure_result = tender_data.get('procedureResult')
        authority_country = tender_data.get('organizationCountry')
        authority_national_id = tender_data.get('organizationNationalId')
        user_id = tender_data.get('userId')
        organization_id = tender_data.get('organizationId')
        is_manually_linked_with_tender = tender_data.get('isManuallyLinkedWithTender')
        html_body = tender_data.get('htmlBody')
        contractors = tender_data.get('contractors')
        bzp_tender_plan_number = tender_data.get('bzpTenderPlanNumber')
        base_notice_mo_identifier = tender_data.get('baseNoticeMOIdentifier')
        technical_notice_mo_identifier = tender_data.get('technicalNoticeMOIdentifier')
        outdated = tender_data.get('outdated')
        object_id = tender_data.get('objectId')
        pdf_url = tender_data.get('pdfUrl')

        if not tender_id and mo_identifier:
            tender_id = mo_identifier

        if not tender_id:
            logger.error("Both tenderId and moIdentifier are missing, cannot create tender")
            return None

        tender, created = PublicTender.objects.update_or_create(
            tender_id=tender_id,
            defaults={
                'announcement_number': announcement_number,
                'announcement_type': announcement_type,
                'order_name': order_name,
                'contracting_authority': contracting_authority,
                'description': description,
                'authority_city': authority_city,
                'authority_region': authority_region,
                'publication_date': publication_date,
                'submission_deadline': submission_deadline,
                'details_url': details_url,
                # New fields
                'client_type': client_type,
                'order_type': order_type,
                'tender_type': tender_type,
                'notice_type_ted': notice_type_ted,
                'notice_type_display_name': notice_type_display_name,
                'bzp_number': bzp_number,
                'is_tender_amount_below_eu': is_tender_amount_below_eu,
                'cpv_code': cpv_code,
                'procedure_result': procedure_result,
                'authority_country': authority_country,
                'authority_national_id': authority_national_id,
                'user_id': user_id,
                'organization_id': organization_id,
                'mo_identifier': mo_identifier,
                'is_manually_linked_with_tender': is_manually_linked_with_tender,
                'html_body': html_body,
                'contractors': contractors,
                'bzp_tender_plan_number': bzp_tender_plan_number,
                'base_notice_mo_identifier': base_notice_mo_identifier,
                'technical_notice_mo_identifier': technical_notice_mo_identifier,
                'outdated': outdated,
                'object_id': object_id,
                'pdf_url': pdf_url
            }
        )

        if created:
            logger.info(f"Created new tender: {tender_id}")
        else:
            logger.info(f"Updated existing tender: {tender_id}")

        return tender

    except Exception as e:
        logger.error(f"Error processing tender: {str(e)}")
        return None


async def scrape_url(url: str, agent_type: int) -> str:
    agent = AGENTS[int(agent_type) % len(AGENTS)]

    async with semaphore:
        async with PlaywrightScraper() as scraper:
            html = await scraper.fetch_html(url, agent)
            if html:
                return html
            return "empty site"
