# Django E-Commerce

A Django-based e-commerce application developed as a **portfolio project** to demonstrate practical experience with Django, modular application architecture, and common e-commerce workflows.

The project covers product catalog management, dynamic product lists and collections, shopping carts, wishlists, orders, inventory, customer addresses, shipping, coupons, offers, comments and reviews, dashboards, and Stripe-based payment processing.

Django REST Framework is used selectively for payment-related API functionality, while the main application is built with Django views, forms, templates, and standard URL routing.

## Features

### Product Catalog

* Product and product-class management
* Hierarchical product categories
* Product pricing and availability
* Stock records and inventory management
* Product browsing and catalog views
* Reusable product lists
* Product collections

### Product Lists and Collections

The catalog provides a reusable system for grouping products through **Product Lists** and **Collections**.

A `ProductList` can determine its products through:

* Explicitly selected stock records
* Product categories
* Product classes

This allows product lists to represent both explicitly selected products and groups of products derived from catalog attributes.

A `CollectionList` can contain multiple product lists, allowing larger collections to be composed from reusable product groups.

For example:

```text
Summer Collection
├── Summer Clothing
├── Summer Accessories
└── Summer Footwear
```

Each product list resolves its applicable stock records based on its configured stock records, categories, and product classes.

This structure allows product groups to be reused across different collections without manually selecting every product for each collection.

### Shopping

* Shopping cart and cart items
* Wishlist functionality
* Coupons
* Offers and discounts
* Customer addresses
* Shipping functionality

### Orders

* Order creation and management
* Order items
* Order-related services
* Checkout and order flow
* Historical order data

### Payments

* Stripe integration
* Stripe Checkout
* Payment records
* Multiple payment attempts
* Payment processing services
* Stripe webhook handling
* Payment-related API endpoints

### Accounts

* User account functionality
* Account-related views and forms
* Customer account management

### Comments and Reviews

* Product comments and reviews
* Comment-related functionality
* Supporting comment services and functionality

### Dashboard

* Dashboard views
* Dashboard forms
* Dashboard widgets
* Seller-related functionality
* Dashboard-specific template tags and utilities

## Architecture

The project is organized into separate Django applications according to business domains rather than placing all functionality into a single application.

```text
accounts/       User account functionality
address/        Customer addresses
cart/           Shopping cart
catalog/        Products, catalog, product lists
collection/     Product collections
comment/        Comments and reviews
coupon/         Coupons
dashboard/      Dashboard functionality
offer/          Offers and discounts
order/          Orders and order services
payment/        Payment processing and Stripe integration
shipping/       Shipping functionality
stock/          Stock and inventory
wishlist/       Wishlist functionality
config/         Django project configuration
```

This structure keeps related models, views, forms, services, and other components grouped by their respective business domains.

## URL Structure

The main application areas are exposed through separate URL namespaces:

```text
/                       Catalog
/account/               Accounts
/cart/                  Shopping cart
/coupon/                Coupons
/wishlist/              Wishlist
/address/               Customer addresses
/order/                 Orders
/payment/               Payments
/comment/               Comments
/dashboard/             Dashboard
/api/v1/payment/        Payment API
/admin/                 Django administration
```

## REST API

Django REST Framework is used selectively rather than as the primary interface for the entire application.

The currently exposed API namespace is:

```text
/api/v1/payment/
```

The API is focused on payment-related functionality.

The rest of the application primarily uses Django's standard views, forms, templates, and URL routing.

## Payment Flow

The payment system integrates with Stripe and is separated into payment-related models, services, views, and API components.

The payment application includes:

* Payment records
* Payment attempts
* Stripe Checkout integration
* Payment processing services
* Stripe webhook handling
* Payment-related API endpoints

Stripe configuration is provided through environment variables rather than being stored directly in the source code.

## Technology Stack

| Technology                 | Purpose                         |
| -------------------------- | ------------------------------- |
| Python                     | Application development         |
| Django 5.2                 | Web framework                   |
| Django REST Framework 3.18 | Selected API endpoints          |
| django-treebeard 7.0.2     | Hierarchical data structures    |
| Stripe 15.6.1              | Payment integration             |
| Pillow 11.1.0              | Image processing                |
| python-decouple 3.8        | Environment-based configuration |
| SQLite                     | Current database                |
| Ruff 0.16.9                | Code quality and linting        |
| pre-commit 4.6.2           | Automated development checks    |

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create the required environment configuration for the Django project.

Sensitive values such as the Django secret key and Stripe credentials should be provided through environment variables and should not be committed to the repository.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an administrator

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The application will be available through the Django development server.

## Configuration

The project uses `python-decouple` for environment-based configuration.

Configuration includes values such as:

```text
SECRET_KEY
DEBUG
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
```

The exact configuration depends on the project's Django settings.

Sensitive configuration should remain outside version control.

## Code Quality

The project uses **Ruff** for code quality checks and **pre-commit** for automated development checks.

Run Ruff:

```bash
ruff check .
```

Run all pre-commit checks:

```bash
pre-commit run --all-files
```

## Deployment

The project is intended to be deployed on **PythonAnywhere**.

The deployment does not require:

* Docker
* Redis
* Celery
* PostgreSQL
* Nginx

The Django project provides both WSGI and ASGI configuration:

```text
config/wsgi.py
config/asgi.py
```

The deployment uses the hosting infrastructure provided by PythonAnywhere rather than introducing a separate container, task queue, cache server, or reverse-proxy stack.

## Project Status

This project is developed as a **portfolio project** to demonstrate practical experience with Django, modular application architecture, and e-commerce application development.

The current focus is on implementing the application's core functionality, domain-oriented architecture, and common e-commerce workflows.

The implemented areas include:

* Product catalog management
* Dynamic product lists
* Product collections
* Shopping cart functionality
* Wishlist functionality
* Order management
* Stock and inventory management
* Checkout and payment processing
* Customer addresses
* Shipping
* Coupons and offers
* Comments and reviews
* Dashboard functionality
* Selected REST API functionality

**Automated testing is not currently implemented.** Testing may be added as the project evolves.

The project is structured as multiple Django applications to keep individual business domains separated and maintainable.

## License

No open-source license has been specified for this repository.
