from django.db import models
from django.conf import settings
import uuid
from typing import Optional, Any


class PublicTender(models.Model):
    uuid: models.UUIDField = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4,
        editable=False, 
        unique=True,
        verbose_name="UUID"
    )
    tender_id: models.CharField = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Identyfikator przetargu"
    )
    announcement_number: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Numer ogłoszenia"
    )
    announcement_type: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Typ ogłoszenia"
    )
    order_name: models.TextField = models.TextField(
        verbose_name="Nazwa lub opis zamówienia"
    )
    contracting_authority: models.TextField = models.TextField(
        verbose_name="Zamawiający"
    )
    description: models.TextField = models.TextField(
        verbose_name="Opis"
    )
    authority_city: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="Miasto zamawiającego"
    )
    authority_region: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Region zamawiającego"
    )
    publication_date: models.DateField = models.DateField(
        verbose_name="Data publikacji"
    )
    submission_deadline: models.DateField = models.DateField(
        verbose_name="Termin składania ofert",
        null=True,
        blank=True
    )
    details_url: models.URLField = models.URLField(
        max_length=255, 
        verbose_name="URL ze szczegółami"
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data utworzenia"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True, 
        verbose_name="Data ostatniej aktualizacji"
    )
    client_type: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Typ klienta",
        null=True,
        blank=True
    )
    order_type: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Typ zamówienia",
        null=True,
        blank=True
    )
    tender_type: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Typ przetargu",
        null=True,
        blank=True
    )
    notice_type_ted: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Typ ogłoszenia TED",
        null=True,
        blank=True
    )
    notice_type_display_name: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="Wyświetlana nazwa typu ogłoszenia",
        null=True,
        blank=True
    )
    bzp_number: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Numer BZP",
        null=True,
        blank=True
    )
    is_tender_amount_below_eu: models.BooleanField = models.BooleanField(
        verbose_name="Czy kwota przetargu poniżej progu UE",
        null=True,
        blank=True
    )
    cpv_code: models.CharField = models.CharField(
        max_length=1024,
        verbose_name="Kod CPV",
        null=True,
        blank=True
    )
    procedure_result: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="Wynik procedury",
        null=True,
        blank=True
    )
    authority_country: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Kraj zamawiającego",
        null=True,
        blank=True
    )
    authority_national_id: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Identyfikator krajowy zamawiającego",
        null=True,
        blank=True
    )
    user_id: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="ID użytkownika",
        null=True,
        blank=True
    )
    organization_id: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="ID organizacji",
        null=True,
        blank=True
    )
    mo_identifier: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="Identyfikator MO",
        null=True,
        blank=True
    )
    is_manually_linked_with_tender: models.BooleanField = models.BooleanField(
        verbose_name="Czy ręcznie powiązany z przetargiem",
        null=True,
        blank=True
    )
    html_body: models.TextField = models.TextField(
        verbose_name="Treść HTML",
        null=True,
        blank=True
    )
    contractors: models.JSONField = models.JSONField(
        verbose_name="Wykonawcy",
        null=True,
        blank=True
    )
    bzp_tender_plan_number: models.CharField = models.CharField(
        max_length=50, 
        verbose_name="Numer planu przetargu BZP",
        null=True,
        blank=True
    )
    base_notice_mo_identifier: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="Identyfikator MO ogłoszenia bazowego",
        null=True,
        blank=True
    )
    technical_notice_mo_identifier: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="Identyfikator MO ogłoszenia technicznego",
        null=True,
        blank=True
    )
    outdated: models.BooleanField = models.BooleanField(
        verbose_name="Czy nieaktualny",
        null=True,
        blank=True
    )
    object_id: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="ID obiektu",
        null=True,
        blank=True
    )
    pdf_url: models.URLField = models.URLField(
        max_length=255, 
        verbose_name="URL do PDF",
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'tenders'
        verbose_name = "Tender"
        verbose_name_plural = "Tenders"
        ordering = ['-publication_date']

    def __str__(self) -> str:
        return f"{self.announcement_number} - {self.order_name[:50]}"


class FollowTender(models.Model):
    TENDER_TYPE_CHOICES: tuple = (
        ('private', 'Prywatny'),
        ('public', 'Publiczny'),
    )

    tender_uuid: models.UUIDField = models.UUIDField(
        verbose_name="UUID przetargu"
    )
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Użytkownik",
        related_name="followed_tenders"
    )
    tender_type: models.CharField = models.CharField(
        max_length=10,
        choices=TENDER_TYPE_CHOICES,
        verbose_name="Typ przetargu"
    )
    followed_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data obserwowania"
    )

    class Meta:
        db_table = 'follow_tender'
        verbose_name = "Obserwacja przetargu"
        verbose_name_plural = "Obserwacje przetargów"
        ordering = ['-followed_at']

    def __str__(self) -> str:
        return f"{self.user.username} obserwuje {self.tender}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)

class PrivateTender(models.Model):
    uuid: models.UUIDField = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False, 
        unique=True,
        verbose_name="UUID"
    )
    title: models.CharField = models.CharField(
        max_length=255, 
        verbose_name="Tytuł"
    )
    description: models.TextField = models.TextField(
        verbose_name="Opis przetargu"
    )
    company_name: models.CharField = models.CharField(
        max_length=255, 
        verbose_name="Nazwa firmy"
    )
    city: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="Miasto"
    )
    region: models.CharField = models.CharField(
        max_length=100, 
        verbose_name="Region"
    )
    publication_date: models.DateField = models.DateField(
        verbose_name="Data publikacji"
    )
    submission_deadline: models.DateField = models.DateField(
        verbose_name="Termin składania ofert"
    )
    details_url: models.URLField = models.URLField(
        max_length=255, 
        verbose_name="Link do szczegółów",
        blank=True,
        null=True
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Utworzono"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True, 
        verbose_name="Zaktualizowano"
    )
    owner: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Właściciel",
        related_name="owned_tenders"
    )
    shared_with: models.ManyToManyField = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Udostępniono dla",
        related_name="shared_tenders",
        blank=True
    )

    class Meta:
        db_table = 'private_tenders'
        verbose_name = "Przetarg prywatny"
        verbose_name_plural = "Przetargi prywatne"
        ordering = ['-publication_date']

    def __str__(self) -> str:
        return f"{self.tender_id} - {self.title[:50]}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)


class TenderNote(models.Model):
    TENDER_TYPE_CHOICES: tuple = (
        ('private', 'Prywatny'),
        ('public', 'Publiczny'),
    )

    tender_uuid: models.UUIDField = models.UUIDField(
        verbose_name="UUID przetargu"
    )
    tender_type: models.CharField = models.CharField(
        max_length=10, 
        choices=TENDER_TYPE_CHOICES, 
        verbose_name="Typ przetargu"
    )
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Użytkownik",
        related_name="tender_notes"
    )
    note: models.TextField = models.TextField(
        verbose_name="Notatka"
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data utworzenia"
    )

    class Meta:
        db_table = 'tender_notes'
        verbose_name = "Notatka do przetargu"
        verbose_name_plural = "Notatki do przetargów"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Notatka użytkownika {self.user.username} do przetargu {self.tender_uuid} ({self.tender_type})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)

    @property
    def tender(self) -> models.Model:
        if self.tender_type == 'public':
            try:
                return PublicTender.objects.get(uuid=self.tender_uuid)
            except PublicTender.DoesNotExist:
                raise ValueError(f"Public tender with UUID {self.tender_uuid} does not exist")
        elif self.tender_type == 'private':
            try:
                return PrivateTender.objects.get(uuid=self.tender_uuid)
            except PrivateTender.DoesNotExist:
                raise ValueError(f"Private tender with UUID {self.tender_uuid} does not exist")
        else:
            raise ValueError(f"Invalid tender_type: {self.tender_type}")
