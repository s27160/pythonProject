# Tenders Management System

A Django-based system for managing public and private tenders, with automatic scraping of public tenders from the ezamowienia.gov.pl portal.

## Features

- **Automatic Tender Scraping**: Periodically fetches public tenders from the ezamowienia.gov.pl portal
- **RESTful API**: Provides endpoints for managing tenders and notes
- **Authentication**: JWT-based authentication for secure access
- **Private Tenders**: Users can create and share private tenders
- **Tender Notes**: Users can add notes to tenders
- **Tender Following**: Users can follow public tenders to track them

## API Endpoints

- `GET /api/tenders/` - List all tenders (public and private)
- `GET /api/tenders/{id}/` - Get details of a specific tender
- `POST /api/tenders/{id}/observe/` - Follow a public tender
- `POST /api/tenders/{id}/notes/` - Add a note to a tender
- `POST /api/private-tenders/` - Create a new private tender
- `GET /api/private-tenders/` - List all private tenders the user has access to
- `GET /api/private-tenders/{id}/` - Get details of a specific private tender
- `PUT /api/private-tenders/{id}/` - Update a private tender
- `DELETE /api/private-tenders/{id}/` - Delete a private tender
- `GET /api/tender-notes/` - List all notes created by the user
- `GET /api/tender-notes/{id}/` - Get details of a specific note
- `PUT /api/tender-notes/{id}/` - Update a note
- `DELETE /api/tender-notes/{id}/` - Delete a note
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

## Technology Stack

- **Backend**: Django 5.1+, Django REST Framework
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens)
- **Task Queue**: Celery with Redis
- **Web Scraping**: Playwright
- **API Documentation**: drf-spectacular (Swagger)

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Git

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd tenders
   ```

2. Create a `.env` file in the project root with the following content:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

3. Build and start the Docker containers:
   ```bash
   docker-compose up -d
   ```

4. Apply migrations:
   ```bash
   docker-compose exec app python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker-compose exec app python manage.py createsuperuser
   ```

6. Uncomment the Celery worker command in docker-compose.yml:
   ```yaml
   celery:
     build: Docker/Python
     command: celery -A tenders_service worker --beat --loglevel=info
     volumes:
       - .:/app
     depends_on:
       - redis
       - db
   ```

7. Restart the Celery container:
   ```bash
   docker-compose restart celery
   ```

## Usage

1. Access the API documentation at http://127.0.0.1:8000/api/doc/
2. Obtain a JWT token by sending a POST request to `/api/token/` with your username and password
3. Use the token in the Authorization header for subsequent requests:
   ```
   Authorization: Bearer <your-token>
   ```

## Development

### Running Tests

```bash
docker-compose exec app python manage.py test
```

### Code Style

This project follows PEP 8 and PEP 257 style guidelines. It uses type hints throughout the codebase.

## License

This project is licensed under the MIT License - see the LICENSE file for details.