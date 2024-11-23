from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date, datetime, timedelta

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Allow origins (change to your frontend URL)
origins = [
    "https://gamenight-fastapi.vercel.app",
    "https://andyland-gamenight.vercel.app"
    "http://localhost:5173" 
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

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Gamer(BaseModel):
    name: str
    email: str

class Vote(BaseModel):
    gamer_id: int
    vote_date: date

    def to_dict(self):
        return {
            "gamer_id": self.gamer_id,
            "vote_date": self.vote_date.isoformat()  # Convert date to ISO format string
        }

class Votes(BaseModel):
    votes: list[Vote]

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

# Endpoint to fetch all data from the Gamers table
@app.get("/gamers/")
async def get_all_gamers():
    try:
        response = supabase_client.table("gamers").select("*").execute()
        return response.data
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

# Endpoint to make gamer vote for multiple game dates
@app.post("/gamers/vote/")
async def vote_for_dates(votes: Votes):
    try:
        # Remove all previous votes for current gamer 
        gamer_ids = [vote.gamer_id for vote in votes.votes]
        response = supabase_client.table("votes_session").delete().in_("gamer_id", gamer_ids).execute()

        # Cast votes
        vote_data = [vote.to_dict() for vote in votes.votes]
        response = supabase_client.table("votes_session").insert(vote_data).execute()

        return response.data
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error casting votes: {str(error)}")


# Endpoint to get all votes for the current week
@app.get("/gamers/votes/results")
async def all_gamers_agreed():
    try:
        # Get the current week's start and end date
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # Get the total number of gamers
        gamers_response = supabase_client.table("gamers").select("*").execute()
        total_gamers = len(gamers_response.data)

        # Query the votes within the current week
        votes_response = (
            supabase_client.table("votes_session")
            .select("*")
            .gte("vote_date", start_of_week)
            .lte("vote_date", end_of_week)
            .execute()
        )

        votes = votes_response.data

        if not votes:
            # No votes within the current week
            return {"agreed": False, "message": "No votes cast within the current week."}

        # Count votes per date
        vote_counts = {}
        for vote in votes:
            vote_date = vote["vote_date"]
            vote_counts[vote_date] = vote_counts.get(vote_date, 0) + 1

        # Check if any date has votes equal to the total number of gamers
        unanimous_agreed_date = next((v_date for v_date, count in vote_counts.items() if count == total_gamers), None)

        if unanimous_agreed_date:
            return {"agreed": True, "agreed_date": unanimous_agreed_date}
        else:
            return {"agreed": False, "message": "Gamers have not unanimously agreed on a date."}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

