from fastapi import FastAPI
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = "https://jruhpgosggdbugenttzp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpydWhwZ29zZ2dkYnVnZW50dHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MDE4MTEsImV4cCI6MjA0NjM3NzgxMX0.4kAs-bySYcXksPtLRdVYxRK9Oyr2WZe2Q6gchXyRg0I"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

# Endpoint to fetch all data from the Gamers table
@app.get("/gamers/")
async def get_all_gamers():
    try:
        response = supabase.table("Gamers").select("*").execute()
        return response.data  # Return the data directly
    except Exception as e:
        return {"error": str(e)}  # Return the error message
