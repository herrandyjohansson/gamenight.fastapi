# Navigate to your project directory

cd path/to/your/project

# Create a virtual environment

python3 -m venv venv

# Activate the virtual environment

source venv/bin/activate

# Run server

uvicorn api.main:app --reload

# Install dependencies

pip install databases sqlalchemy asyncpg psycopg2-binary python-dotenv supabase

# Generate requirements

pip freeze > requirements.txt
