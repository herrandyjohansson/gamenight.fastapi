from fastapi import FastAPI
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Allow origins (change to your frontend URL)
origins = [
    "https://gamenight-fastapi.vercel.app",
    "http://localhost:5173"  # Allow localhost for local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!!"}

# Endpoint to fetch all data from the Gamers table
@app.get("/gamers/")
async def get_all_gamers():
    try:
        response = supabase.table("Gamers").select("*").execute()
        return response.data
    except Exception as e:
        return {"error": str(e)}