from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from datetime import date  # Import date from datetime

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

SUPABASE_URL = "https://jruhpgosggdbugenttzp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpydWhwZ29zZ2dkYnVnZW50dHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MDE4MTEsImV4cCI6MjA0NjM3NzgxMX0.4kAs-bySYcXksPtLRdVYxRK9Oyr2WZe2Q6gchXyRg0I"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!!"}

# Endpoint to fetch all data from the Gamers table
@app.get("/gamers/")
async def get_all_gamers():
    try:
        response = supabase.table("gamers").select("*").execute()
        return response.data
    except Exception as e:
        return {"error": str(e)}
    
# Endpoint to make gamer vote for a game date 
@app.post("/gamers/vote/")
async def vote_for_date(gamer_id: int, vote_date: date):
    try:
        response = supabase.table("votes").insert({"gamer_id": gamer_id, "vote_date": vote_date.isoformat()}).execute()
        return response.data
    except Exception as e:
        return {"error": str(e)}