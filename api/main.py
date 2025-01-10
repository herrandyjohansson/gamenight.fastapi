from typing import List
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from pydantic import BaseModel, EmailStr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import date

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Allow origins (change to your frontend URL)
origins = [
    "https://gamenight-fastapi.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",  # Next.js server
    "https://gamenight-v3.vercel.app"
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

class SingleVote(BaseModel):
    gamer_id: int
    vote_date: date

    def to_serializable_dict(self):
        return {
            "gamer_id": self.gamer_id,
            "vote_date": self.vote_date.isoformat(),  # Convert date to string
            "vote": self.vote,
        }

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
async def toggle_vote(single_vote: SingleVote):
    try:
        # Check if a vote exists for the gamer and date
        existing_vote_response = (
            supabase_client.table("votes_session")
            .select("*")
            .eq("gamer_id", single_vote.gamer_id)
            .eq("vote_date", single_vote.vote_date)
            .execute()
        )
        existing_votes = existing_vote_response.data

        if existing_votes:
            # If a vote exists, delete it
            delete_response = (
                supabase_client.table("votes_session")
                .delete()
                .eq("id", existing_votes[0]["id"])
                .execute()
            )
            if hasattr(delete_response, "error") and delete_response.error:
                raise HTTPException(
                    status_code=500, detail=str(delete_response.error.message)
                )
        else:
            # If no vote exists, insert it
            insert_response = (
                supabase_client.table("votes_session")
                .insert(
                    {
                        "gamer_id": single_vote.gamer_id,
                        "vote_date": single_vote.vote_date.isoformat(),
                    }
                )
                .execute()
            )
            if hasattr(insert_response, "error") and insert_response.error:
                raise HTTPException(
                    status_code=500, detail=str(insert_response.error.message)
                )

        return {"message": "Vote toggled successfully."}

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

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
            send_confirmation_email(unanimous_agreed_date)
            return {"agreed": True, "agreed_date": unanimous_agreed_date}
        else:
            return {"agreed": False, "message": "Gamers have not unanimously agreed on a date."}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/test/sendemail")
async def test_send_email():
    try:
        response = send_confirmation_email("2021-09-30")
        return {"message": str(response)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/weekly/reminder")
async def test_send_email():
    try:
        send_weekly_reminder_email()
        # Activate email service
        email_service_toggle(True)
        return {"message": "Weekly reminder email sent."}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

# Load Gmail credentials from environment variables
GMAIL_USER = "herrandyjohansson@gmail.com"
GMAIL_PASSWORD = "evlrxazgqxwnmemb"

if not GMAIL_USER or not GMAIL_PASSWORD:
    raise RuntimeError("Gmail credentials must be set in environment variables.")

# Pydantic model for email request
class EmailRequest(BaseModel):
    recipient: EmailStr
    subject: str
    message: str

def email_service_toggle(status: bool): 
    try:
        supabase_client.table("services").update({"active": status}).eq("name", "email").execute()
        return {"message": "Email service set to: " + str(status)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

def email_service_active():
    try:
        response = supabase_client.table("services").select("active").eq("name", "email").execute()

        return response.data[0].get("active") is True
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    
    
def email_subject():
    try:
        response = supabase_client.table("email").select("subject").execute()
        return response.data[0].get("subject")
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    
def email_message():
    try:
        response = supabase_client.table("email").select("message").execute()
        return response.data[0].get("message")
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


def get_email_list():
    try:
        # Fetch data from the "gamers" table selecting only the "email" field
        response = supabase_client.table("gamers").select("email").execute()

        # Extract emails and filter out None (null) values
        email_list = [record['email'] for record in response.data if record['email'] is not None]

        # Return the list of non-null emails
        return email_list
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

def send_confirmation_email(date: date): 
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        formatted_date = parsed_date.strftime("%Y-%m-%d")  
        day_of_week = parsed_date.strftime("%A")  

        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['Subject'] = f"GameNight locked - {day_of_week}, {formatted_date}"

        email_message = f"The GameNight has been locked for the week!\n\nDay: {day_of_week} \n\nDate: {formatted_date}"
        # Attach the email body
        msg.attach(MIMEText(email_message, 'plain'))

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Upgrade the connection to secure

        # Log in to the Gmail account
        server.login(GMAIL_USER, GMAIL_PASSWORD)

        should_send_email = email_service_active()

        if not should_send_email:
            print("Email service is not activated.")
            return "Email service is not activated."
        
        send_emails_to_recipients_list = get_email_list()

        # loop through the list of emails and send the email
        for gamer in send_emails_to_recipients_list:
            server.sendmail(GMAIL_USER, gamer, msg.as_string())
            print(f"Email successfully sent to {gamer}")
        
        # inactive email service
        email_service_toggle(False)

        # Disconnect from the server
        server.quit()

        print(f"Email successfully all mails")
        return "Email successfully all mails"
    except Exception as error:
        print(f"Failed to send email mails.  {str(error)}")
        return f"Failed to send email mails.  {str(error)}"
        
# Make send_email function synchronous
def send_weekly_reminder_email():
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['Subject'] = email_subject()

        # Attach the email body
        msg.attach(MIMEText(email_message(), 'plain'))

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Upgrade the connection to secure

        # Log in to the Gmail account
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        send_emails_to_recipients_list = get_email_list()

        # loop through the list of emails and send the email
        for gamer in send_emails_to_recipients_list:
            server.sendmail(GMAIL_USER, gamer, msg.as_string())
            print(f"Email successfully sent to {gamer}")
        
        # Disconnect from the server
        server.quit()

        print(f"Email successfully all mails")
    except Exception as error:
        print(f"Failed to send email mails.  {str(error)}")

