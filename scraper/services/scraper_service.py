import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from scraper.operations import RequestsScraper
from web.modules.tenders.models import PublicTender
from asgiref.sync import sync_to_async
from django.db import transaction

semaphore = asyncio.Semaphore(8)

BASE_API_URL = "https://ezamowienia.gov.pl/mo-board/api/v1/Board/Search"

async def build_api_url(
    days_back: int,
    page_number: int,
    page_size: int
) -> str:
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00.000Z")

    url = (
        f"{BASE_API_URL}?"
        f"publicationDateFrom={from_date}&"
        f"SortingColumnName=PublicationDate&"
        f"SortingDirection=DESC&"
        f"PageNumber={page_number}&"
        f"PageSize={page_size}"
    )

    return url


async def fetch_tenders(
    days_back: int = 7,
    max_pages: int = 10000
):
    async with RequestsScraper() as scraper:
        page_number = 1
        has_more_data = True
        tenders = 0
        processed = 0
        while has_more_data and page_number <= max_pages:
            url = await build_api_url(
                days_back=days_back,
                page_number=page_number,
                page_size=10
            )

            async with semaphore:
                data = await scraper.fetch_json(url)
                if not data:
                    has_more_data = False
                    break
                else:
                    process_tenders: List[Dict[str, Any]] = []
                    process_tenders.extend(data)
                    for tender in process_tenders:
                        tenders += 1
                        result = await process_tender(tender)
                        if result:
                            processed += 1
                        print(f"Zakończono okresowe pobieranie ofert: {tenders} pobrano, {processed} przetworzono")
                page_number += 1
                await asyncio.sleep(1)

    return {
        "fetched": tenders,
        "processed": processed
    }


async def process_tender(tender_data: Dict[str, Any]) -> Optional[Any]:
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
            return None

        defaults = {
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

        return await sync_to_async(create_or_update_tender)(tender_id=tender_id, defaults=defaults)

    except Exception as e:
        print(f"Błąd podczas przetwarzania przetargu: {str(e)}")
        return None

@transaction.atomic
def create_or_update_tender(tender_id, defaults):
    tender, created = PublicTender.objects.update_or_create(tender_id=tender_id, defaults=defaults)
    return tender
