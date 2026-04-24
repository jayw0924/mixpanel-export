# Mixpanel Export Tool

A CLI tool for exporting raw event data from Mixpanel's Export API.

## Features

- **Flexible Date Ranges**: Specify absolute dates or relative ranges (e.g., "last 7 days")
- **Event Filtering**: Filter by event type or property expressions
- **Smart Output Naming**: Auto-generates filenames based on the exported date range
- **JSONL Output**: Standard format for streaming JSON data
- **Credential Management**: Secure credential loading from .env file

## Installation

1. Clone this repository
2. Install dependencies:
```bash
/usr/bin/python3 -m pip install -r requirements.txt
```
3. Set up credentials:
```bash
cp .env.example .env
# Edit .env with your Mixpanel credentials
```
4. Make the command available globally:
```bash
chmod +x mixpanel_export.py
ln -sf "$(pwd)/mixpanel_export.py" ~/.local/bin/mixpanel-export
# Ensure ~/.local/bin is on your PATH (add to ~/.zshrc if needed):
# export PATH=$HOME/.local/bin:$PATH
```

## Configuration

Create a `.env` file in the project root:

```bash
MIXPANEL_USERNAME=your_service_account_username
MIXPANEL_SECRET=your_service_account_secret
MIXPANEL_PROJECT_ID=your_project_id
```

**Finding your credentials:**
- Go to **Organization Settings → Service Accounts** → create a service account with **Analyst** role
- Add the service account to your project under **Project Settings → Access Security → Service Accounts**
- Copy the username and secret shown at creation time (secret is only shown once)
- Find your **Project ID** under Project Settings

## Usage

Once installed globally, run from anywhere:

```bash
mixpanel-export [OPTIONS]
```

### Date range

```bash
# Yesterday (default)
mixpanel-export

# Last N days
mixpanel-export --days 30

# Specific range
mixpanel-export --from-date 2026-03-01 --to-date 2026-03-31
```

### Filtering

```bash
# Filter by event type
mixpanel-export --days 7 --event-type "Page View"

# Filter by property
mixpanel-export --days 7 --where 'properties["$referring_domain"] == "google.com"'
mixpanel-export --days 7 --where 'properties["$browser"] == "Chrome"'
mixpanel-export --days 7 --where 'properties["$referring_domain"] != "direct"'
mixpanel-export --from-date 2026-03-01 --to-date 2026-03-31 \
  --where 'properties["$referring_domain"] in ["example.com", "shop.example.com"]'

# Combine event type and property filters
mixpanel-export --days 7 \
  --event-type "Page View" \
  --where 'properties["$referring_domain"] != "direct"'
```

### Other options

```bash
# Limit events returned (useful for testing)
mixpanel-export --days 1 --limit 1000

# Override output path
mixpanel-export --days 30 --output /tmp/test.jsonl
```

### All options

```
--from-date TEXT   Start date in YYYY-MM-DD format
--to-date TEXT     End date in YYYY-MM-DD format
--days INTEGER     Fetch last N days (alternative to --from-date/--to-date)
--limit INTEGER    Maximum number of events to fetch
--output TEXT      Output file path (default: auto-generated in ~/data/datasets/3d-source/mixpanel-events/)
--event-type TEXT  Filter by specific event type/name
--where TEXT       Filter expression on event properties
--help             Show this message and exit
```

## Output

By default, files are saved to `~/data/datasets/3d-source/mixpanel-events/` with a filename based on the exported date range:

```
mixpanel-2026-04-24.jsonl               # single day
mixpanel-2026-04-01-to-2026-04-30.jsonl # date range
```

Output is JSONL format — one JSON object per line:

```json
{"event":"Page View","properties":{"time":1704067200,"distinct_id":"user123","page":"/home"}}
{"event":"Button Click","properties":{"time":1704067300,"distinct_id":"user456","button":"signup"}}
```

### Working with JSONL

```bash
# Count events
wc -l mixpanel-2026-04-24.jsonl

# Pretty-print first event
head -n 1 mixpanel-2026-04-24.jsonl | jq

# Filter with jq
cat mixpanel-2026-04-24.jsonl | jq 'select(.event == "Page View")'
```

```python
# Load in pandas
import pandas as pd
df = pd.read_json("mixpanel-2026-04-24.jsonl", lines=True)
```

## Troubleshooting

**"Missing credentials in .env file"** — ensure `.env` exists with all three variables set. No quotes needed around values.

**"Authentication error (401/403)"** — verify credentials are correct and the service account has been added to the project in Project Settings (creating a service account does not automatically grant project access).

**"No events found"** — try without filters first to confirm data exists for the date range.

## Dependencies

- **click** — CLI framework
- **requests** — HTTP library
- **python-dotenv** — environment variable management

## API Reference

- **Endpoint**: `https://data.mixpanel.com/api/2.0/export`
- **Auth**: HTTP Basic Auth (service account username + secret)
- **Docs**: [Mixpanel Raw Data Export API](https://developer.mixpanel.com/reference/raw-event-export)
