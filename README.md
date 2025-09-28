# E-Commerce API - Project Nexus

This is a robust backend API for an e-commerce platform, built using Django REST Framework. The project supports a multi-role system, including Sellers, Consumers, and Admins. It provides features for efficient product management, secure user authentication, and advanced product discovery with filtering, sorting, and pagination.

## Features

* **Multi-role System:** Sellers, Consumers, and Admins
* **Product Management:** Full CRUD operations with advanced filtering and search capabilities
* **Hierarchical Categories:** Support for nested product categories
* **User Authentication:** JWT-based authentication with refresh tokens
* **Sales Analytics:** Insights and reporting for product performance
* **Automated Email Notifications:** Notify users and admins based on specific events
* **Image Storage:** Integrated with Cloudinary for media management
* **Performance Optimized:** Database indexing for fast queries

## Tech Stack

* **Django 4.2+** & **Django REST Framework** for the backend
* **PostgreSQL** for relational database management
* **Redis** for caching
* **JWT Authentication** for secure login and session management
* **Cloudinary** for image hosting
* **Docker** for containerization
* **Swagger** for interactive API documentation

## Quick Start

1. Clone the repository:

   ```bash
   git clone <repository-url>
   ```

2. Build and start the services using Docker Compose:

   ```bash
   docker-compose up --build
   ```

3. Apply the database migrations:

   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. Create a superuser for administrative access:

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Access the API at [http://localhost:8000](http://localhost:8000/api/v1).

## API Documentation

Interactive API documentation is available at `/swagger` when the application is running locally. The documentation covers:

* Endpoint details for all CRUD operations on products and categories
* JWT authentication and usage
* Request and response formats for each API

## Development

This project uses **Docker Compose** for the development environment. It includes PostgreSQL and Redis services. All Django management commands should be run using `docker-compose exec`.

For example, to run tests:

```bash
docker-compose exec web python manage.py test
```

## Project Structure

The project follows the standard Django structure, with additional Docker configuration files for easy local development.

The key components include:

* **`/app`**: The main Django application, including models, views, serializers, and API endpoints.
* **`/docker`**: Docker-related configuration files.
* **`/migrations`**: Database migration files for schema changes.
* **`/docs`**: API documentation files and related configurations.

---

### Additional Notes:

* **Pagination, Sorting, and Filtering**: These features are implemented for the products API to enable efficient browsing of large datasets.
* **Database Optimization**: Indexing is implemented on key database fields to ensure fast queries, especially for product searches.
* **Authentication**: JWT is used for secure, token-based authentication.

---
