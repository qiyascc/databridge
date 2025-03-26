# LC Waikiki Data Bridge

A Django project that integrates Scrapy spiders for scraping LC Waikiki product data.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Usage

The project includes three spiders:

1. Sitemap Spider:
```bash
python manage.py run_spider sitemap
```

2. Location Spider:
```bash
python manage.py run_spider location
```

3. Product Spider:
```bash
python manage.py run_spider product
```

## Project Structure

- `databridge/` - Main Django project directory
- `lcwaikiki/` - Django app containing models and management commands
- `databridge/spiders/` - Scrapy spiders for different data collection tasks

## Data Models

- `ProductSitemap`: Stores sitemap information
- `ProductLocation`: Stores product location data
- `Product`: Stores detailed product information

## Configuration

The project uses both Django and Scrapy settings. Scrapy settings are configured in `databridge/settings.py` under the `SCRAPY_SETTINGS` dictionary.

## Database

The project uses SQLite by default. To use MongoDB, update the `DATABASES` setting in `settings.py`. 