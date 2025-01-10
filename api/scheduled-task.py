from supabase import create_client
import requests

# Supabase credentials
SUPABASE_URL = "https://jruhpgosggdbugenttzp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpydWhwZ29zZ2dkYnVnZW50dHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MDE4MTEsImV4cCI6MjA0NjM3NzgxMX0.4kAs-bySYcXksPtLRdVYxRK9Oyr2WZe2Q6gchXyRg0I"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def handler(request):
    try:
        # Replace with your actual Vercel deployment URL
        response = requests.get("https://gamenight-fastapi.vercel.app/test/sendemail")
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except requests.exceptions.RequestException as error:
        return {"status": "error", "message": str(error)}
