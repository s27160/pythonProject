## System Zarządzania Przetargami

### Opis ogólny

Jest to system zarządzania przetargami, który umożliwia użytkownikom przeglądanie publicznych przetargów, tworzenie przetargów prywatnych, obserwowanie interesujących przetargów oraz dodawanie do nich notatek. System składa się z aplikacji webowej z REST API oraz modułu scraper, który cyklicznie pobiera publiczne przetargi z zewnętrznego źródła.

### Kluczowe funkcjonalności

* Przeglądanie publicznych przetargów zebranych ze strony ezamowienia.gov.pl
* Tworzenie i zarządzanie przetargami prywatnymi
* Obserwowanie wybranych przetargów
* Dodawanie notatek do przetargów
* Udostępnianie przetargów prywatnych innym użytkownikom
* REST API z uwierzytelnianiem JWT
* Dokumentacja Swagger

## Konfiguracja i instalacja

### Wymagania wstępne

* Docker i Docker Compose


### Kroki instalacji

1. Uruchom kontenery Docker:

   ```bash
   docker-compose up -d
   ```
2. Wykonaj migracje bazy danych:

   ```bash
   docker-compose exec app python manage.py migrate
   ```

## Uruchamianie aplikacji

### Usługi

* **app**: Główna aplikacja Django (port 8000)
* **db**: Baza danych MySQL (port 3306)
* **redis**: Serwer Redis do cache i Celery
* **celery**: Worker do zadań w tle
* **celery-beat**: Scheduler do zadań cyklicznych

### Dostęp do aplikacji

* Interfejs webowy i API: [http://localhost:8000/](http://localhost:8000/)
* Dokumentacja Swagger: [http://localhost:8000/](http://localhost:8000/)

### Uwierzytelnianie

* Dane administratora:

  * Nazwa użytkownika: `admin`
  * Hasło: `admin`
* Do dostępu do API używane jest JWT:

  * Pobierz token: `/api/token/`
  * Odśwież token: `/api/token/refresh/`

## Dokumentacja API

Dokumentacja API jest dostępna w Swagger UI pod głównym adresem aplikacji lub pod `/api/doc/`.

### Przykładowe zapytania API

**Listowanie publicznych przetargów**
Endpoint: `GET /api/public_tenders/`
Parametry wyszukiwania:

* `search` na polach `order_name`, `description`, `contracting_authority`
  Parametry sortowania:
* `ordering` na polach `publication_date`, `submission_deadline`, `created_at`

**Listowanie prywatnych przetargów**
Endpoint: `GET /api/private_tenders/`
Parametry wyszukiwania:

* `search` na polach `title`, `description`, `company_name`, `shared_with__username`
  Parametry sortowania:
* `ordering` na polach `publication_date`, `submission_deadline`, `created_at`

**Spolszczenia parametrów wyszukiwania i sortowania**

| Endpoint                    | Parametr `search`       | Tłumaczenie                             | Parametr `ordering`   | Tłumaczenie            |
| --------------------------- | ----------------------- |-----------------------------------------| --------------------- | ---------------------- |
| `GET /api/public_tenders/`  | `order_name`            | nazwa zamówienia                        | `publication_date`    | data publikacji        |
|                             | `description`           | opis                                    | `submission_deadline` | termin składania ofert |
|                             | `contracting_authority` | zamawiający                             | `created_at`          | data utworzenia        |
| `GET /api/private_tenders/` | `title`                 | tytuł                                   | `publication_date`    | data publikacji        |
|                             | `description`           | opis                                    | `submission_deadline` | termin składania ofert |
|                             | `company_name`          | nazwa firmy                             | `created_at`          | data utworzenia        |
|                             | `shared_with__username` | nazwy użytkownkiów, którym udostępniono |                       |                        |


### Przykładowe tworzenie przetargu prywatnego

Endpoint: `POST /api/private_tenders/`

Body (JSON):

```json
{
  "title": "Lula",
  "description": "Pula",
  "company_name": "PKHSFWF",
  "city": "Warsaw",
  "region": "Mazowieckie",
  "publication_date": "2025-06-22",
  "submission_deadline": "2025-06-22",
  "details_url": "https://stackoverflow.com/questions/55465859/drf-how-to-create-a-listserializer-from-an-array-of-serializer",
  "shared_with_usernames": []
}
```

Przykład z użytkownikiem udostępnionym:

```json
{
  "title": "Marek",
  "description": "Jarek",
  "company_name": "Sp zoo",
  "city": "Opoczno",
  "region": "Łódzkie",
  "publication_date": "2025-02-22",
  "submission_deadline": "2025-02-22",
  "details_url": "https://stackoverflow.com/questions/55465859/drf-how-to-create-a-listserializer-from-an-array-of-serializer",
  "shared_with_usernames": ["user"]
}
```

## Tworzenie i rozwój

### Struktura projektu

* **web/**: Aplikacja Django

  * **config/**: Ustawienia i konfiguracja Django
  * **modules/**: Moduły aplikacji

    * **tenders/**: Moduł przetargów (modele, widoki, serializery)
    * **users/**: Moduł użytkowników
* **scraper/**: Aplikacja scraper

  * **operations/**: Operacje skryptu
  * **services/**: Serwisy przetwarzające dane
  * **tasks.py**: Zadania Celery
  * **settings.py**: Ustawienia scrappera
* **Docker/**: Konfiguracja Docker
* **docker-compose.yml**: Definicja usług w Docker Compose
