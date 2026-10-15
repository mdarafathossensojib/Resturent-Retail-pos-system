from pathlib import Path

content = r"""# Retail POS System

A Django REST Framework-based Retail Point of Sale (POS) backend for managing users, products, inventory, purchases, sales, payments, refunds, and business reports.

## Features

- Custom user authentication with role-based access: Admin, Manager, and Cashier.
- Product and category management.
- Customer and supplier management.
- Sales and sale-item APIs.
- Inventory tracking through stock movements.
- Purchase management and supplier returns.
- Payment collection, split payments, and outstanding-due reporting.
- Full sale refund workflow with inventory restoration and refund history.
- Reports API for sales trends, product performance, inventory, payments, purchases, and stock movements.

## Tech Stack

- Python
- Django
- Django REST Framework
- Database configured in Django settings
- JWT/session authentication depending on project configuration

## Project Setup

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd retail-pos-system
```

### 2. Create and activate a virtual environment

Windows:

```bash
py -m venv .retail_env
.retail_env\Scripts\activate
```

### 3. Install dependencies

If the repository contains `requirements.txt`:

```bash
py -m pip install -r requirements.txt
```

If `requirements.txt` does not exist yet, create one from the working environment after confirming all project dependencies:

```bash
py -m pip freeze > requirements.txt
```

### 4. Configure environment variables

Create a `.env` file if the project settings use environment variables. Add the required values, such as the Django secret key, database credentials, and any media-storage credentials.

**Do not commit `.env`, production secrets, or credentials to Git.**

### 5. Apply migrations

```bash
py manage.py migrate
```

### 6. Create an administrator

```bash
py manage.py createsuperuser
```

Follow the prompts. This project uses a custom user model with email login, so follow the project's configured user manager prompts.

### 7. Run checks and start the server

```bash
py manage.py check
py manage.py runserver
```

The development server normally runs at:

`http://127.0.0.1:8000/`

## API Base URL

The API router is configured under:

`/api/v1/`

For local development, an endpoint may look like:

`http://127.0.0.1:8000/api/v1/reports/overview/`

Use the authentication method configured in the project to access protected endpoints.

## Reports API

The `reports` app calculates reports from existing sales, sale-item, product, payment, purchase, supplier-return, and stock-movement data. Reports are computed from existing records; the app does not require a separate report database model for these endpoints.

### Available report endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/reports/overview/` | Summary for today, this week, this month, and this year |
| GET | `/api/v1/reports/sales/?period=daily` | Sales trend grouped by day |
| GET | `/api/v1/reports/sales/?period=weekly` | Sales trend grouped by week |
| GET | `/api/v1/reports/sales/?period=monthly` | Sales trend grouped by month |
| GET | `/api/v1/reports/sales/?period=yearly` | Sales trend grouped by year |
| GET | `/api/v1/reports/products/?period=monthly` | Product-level sales performance |
| GET | `/api/v1/reports/products/top-selling/?period=monthly` | Top 10 products by quantity sold |
| GET | `/api/v1/reports/inventory/` | Current stock and stock status |
| GET | `/api/v1/reports/payments/?period=monthly` | Payment totals grouped by payment method |
| GET | `/api/v1/reports/purchases/?period=monthly` | Purchases and supplier returns |
| GET | `/api/v1/reports/stock-movements/?period=monthly` | Stock movement counts and quantities |

### Period options

The report endpoints that accept `period` support:

- `daily`
- `weekly`
- `monthly`
- `yearly`

Default ranges currently used when dates are not supplied:

- `daily`: last 30 days
- `weekly`: last 12 weeks
- `monthly`: approximately the last 12 months
- `yearly`: current year and the previous 4 years

### Custom date range

Some reports support `start_date` and `end_date`:

```text
/api/v1/reports/products/?start_date=2026-10-01&end_date=2026-10-14
```

Both dates must be supplied together, and `start_date` must not be later than `end_date`.

### Report calculation notes

- Sales reports currently include sales whose status is `completed`; fully refunded sales are excluded.
- Product quantities and sales values are aggregated from `SaleItem` records.
- Payment collection uses `Payment.amount`, which represents the amount applied to the sale, rather than `amount_received`.
- Inventory status is based on current stock and each product's low-stock threshold.
- Profit and loss reporting is not yet included in the current endpoint list. Historical profit should not be calculated from today's product cost if the cost price can change over time.
- Date filtering relies on the model timestamp fields and Django's configured timezone. Confirm the project timezone and timestamp field names before treating the reports as production-ready.

## Main API Areas

The router also exposes the project's main resource APIs. Check `api/urls.py` for the authoritative route list.

Common resource groups include:

- Users
- Customers
- Suppliers
- Categories
- Products
- Inventory
- Purchases and purchase items
- Sales and sale items
- Payments
- Sale refunds
- Reports

## Security Notes

- Keep the Django `SECRET_KEY`, database passwords, API keys, and media-storage credentials out of source control.
- Use environment variables for secrets.
- Use HTTPS in production.
- Review role permissions before deployment, especially for sales, refunds, payments, and reports.
- Do not expose sensitive customer, payment, or business data to unauthorized roles.
- Configure `DEBUG=False`, `ALLOWED_HOSTS`, trusted origins, and production database settings appropriately for deployment.

## Validation and Testing

Before pushing changes, run:

```bash
py manage.py check
py manage.py makemigrations --check --dry-run
```

Run the test suite if tests are configured:

```bash
py manage.py test
```

Manually test protected endpoints with the appropriate user roles. Use development/test data for refund tests because a refund can change a sale's status and restore inventory.

## Current Report App Follow-up

Before considering reports production-ready, verify:

- Actual model field names for `Sale`, `SaleItem`, `Product`, `Purchase`, `Payment`, `SupplierReturn`, and `StockMovement`.
- The configured timezone and date grouping behavior.
- Whether product cost is stored on each sale item for accurate historical profit.
- How partial refunds, if supported later, should affect sales totals and product quantities.
- Whether slow-moving products should mean low sales over a chosen date range or no sales over that range.
- Whether the report APIs should be restricted to Admin and Manager roles only.

## License

Add the project's chosen license here before public distribution.
"""
path = Path("/mnt/data/README.md")
path.write_text(content, encoding="utf-8")
print(f"Created: {path} ({path.stat().st_size} bytes)")
