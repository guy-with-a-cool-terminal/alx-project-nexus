# E-Commerce API - Project Nexus

A robust multi-role e-commerce backend API built with Django REST Framework, featuring advanced analytics, email automation, and comprehensive product management.

## Features

- Multi-role system with Sellers, Consumers, and Admins
- Advanced product management with filtering and search
- Hierarchical categories with nested support
- Sales analytics and performance insights
- Automated email notifications and reports
- JWT authentication with refresh tokens
- Cloudinary image storage integration
- Performance optimized with database indexing

## Tech Stack

- Django 4.2+ & Django REST Framework
- PostgreSQL database
- Redis caching
- JWT authentication
- Cloudinary image storage
- Docker containerization
- Swagger API documentation

## Quick Start

1. Clone the repository
2. Run `docker-compose up --build` to start all services
3. Execute `docker-compose exec web python manage.py migrate` for database setup
4. Create superuser with `docker-compose exec web python manage.py createsuperuser`
5. Access the API at http://localhost:8000

## API Documentation

Interactive API documentation available at `/api/docs/` when running locally.

## Development

The project uses Docker Compose for development environment with PostgreSQL and Redis services. All Django management commands should be run through docker-compose exec.

## Project Structure

Standard Django project structure with Docker configuration files and virtual environment support for local development.