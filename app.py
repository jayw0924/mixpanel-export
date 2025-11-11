from dotenv import load_dotenv
import os
import requests
import base64
import json
from datetime import datetime

load_dotenv()

# Credentials
USERNAME = os.getenv("MIXPANEL_USERNAME")
SECRET   = os.getenv("MIXPANEL_SECRET")
PROJECT_ID = os.getenv("MIXPANEL_PROJECT_ID")

if not all([USERNAME, SECRET, PROJECT_ID]):
    raise ValueError("Missing credentials in .ev file!")

# Config
FROM_DATE = "2025-11-09"
TO_DATE   = "2025-11-09"
LIMIT     = 10
OUTPUT_FILE = "mixpanel_raw_nov9.json"

# Auth
auth = base64.b64encode(f"{USERNAME}:{SECRET}".encode()).decode()
url = "https://data.mixpanel.com/api/2.0/export"
headers = {"Authorization": f"Basic {auth}", "Accept": "application/json"}

params = {
    "from_date": FROM_DATE,
    "to_date": TO_DATE,
    "limit": LIMIT,
    "project_id": PROJECT_ID
}

headers = {
    "Accept": "application/json",
    "Authorization": f"Basic {auth}"
}

print(f"Fetching up to {LIMIT} events from {FROM_DATE}...")

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    raw_text = response.text.strip()
    
    # Mixpanel returns JSONL (one JSON per line), not a JSON array
    events = [json.loads(line) for line in raw_text.splitlines() if line.strip()]
    
    print(f"SUCCESS! Got {len(events)} event(s)")
    
    # Save raw JSONL
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"Saved raw data → {OUTPUT_FILE}")
    
    # Print first event
    if events:
        print("\nFirst event:")
        print(json.dumps(events[-1], indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")