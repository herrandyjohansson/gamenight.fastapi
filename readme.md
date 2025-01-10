# Navigate to your project directory

cd path/to/your/project

# Create a virtual environment

python3 -m venv venv

# Activate the virtual environment

source venv/bin/activate

# Install dependencies

pip install databases sqlalchemy asyncpg psycopg2-binary python-dotenv supabase

# Generate requirements

pip freeze > requirements.txt

# Run server

uvicorn api.main:app --reload

# windows

install python

python -m venv venv

venv\Scripts\activate

pip install databases sqlalchemy asyncpg psycopg2-binary python-dotenv supabase

# email

pip install pydantic[email]

uvicorn api.main:app --reload

# cron

cron jobs.org
