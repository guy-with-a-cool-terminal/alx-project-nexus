# E-Commerce API Development Environment

## Services
- **Web**: Django app on port 8000
- **Database**: PostgreSQL on port 5432
- **Cache**: Redis on port 6379

## Project Structure
```
ecommerce-backend/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── myenv/                    # Local development
└── app/                     # Django project
    ├── manage.py
    └── ecommerce_api/
```

## Daily Commands

### Start Development
```bash
docker-compose up
```

### Django Management Commands
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py startapp <name>
```

### Stop Services
```bash
docker-compose down
```

### Rebuild (after requirements.txt changes)
```bash
docker-compose up --build
```

## Database Access
- **Host**: localhost (from your machine) or `db` (from containers)
- **Port**: 5432
- **Database**: ecommerce_db
- **User/Password**: postgres/postgres

## Redis Access
- **URL**: redis://localhost:6379/1 (from your machine)
- **URL**: redis://redis:6379/1 (from containers)

## Local Development
Virtual environment in `venv/` for IDE support and running django-admin commands locally.

## Troubleshooting

### View Logs
```bash
docker-compose logs web
docker-compose logs db
```

### Container Issues
```bash
docker-compose down
docker-compose up --build
```

### Database Reset
```bash
docker-compose down -v  # Deletes all data
docker-compose up
```

## URLs
- Django App: http://localhost:8000
- Django Admin: http://localhost:8000/admin