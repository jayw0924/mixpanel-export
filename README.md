# Mixpanel Export Tool

A simple CLI tool for exporting raw event data from Mixpanel's Export API.

## Features

- **Flexible Date Ranges**: Specify absolute dates or relative ranges (e.g., "last 7 days")
- **Event Filtering**: Filter by specific event types at the API level
- **Simple CLI**: Easy-to-use command-line interface with Click
- **JSONL Output**: Standard format for streaming JSON data
- **Credential Management**: Secure credential loading from .env file

## Installation

1. Clone this repository or download the files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up credentials:
```bash
cp .env.example .env
# Edit .env with your Mixpanel credentials
```

## Configuration

Create a `.env` file in the project root with your Mixpanel credentials:

```bash
MIXPANEL_USERNAME=your_service_account_username
MIXPANEL_SECRET=your_service_account_secret
MIXPANEL_PROJECT_ID=your_project_id
```

**Finding Your Credentials:**
- Go to Mixpanel Project Settings → Service Accounts
- Create a service account with "Export" permissions
- Copy the username and secret
- Find your Project ID in Project Settings

## Usage

### Basic Examples

Export yesterday's events (default behavior):
```bash
python mixpanel_export.py
```

Export the last 7 days:
```bash
python mixpanel_export.py --days 7
```

Export a specific date range:
```bash
python mixpanel_export.py --from-date 2025-01-01 --to-date 2025-01-31
```

Export with a limit:
```bash
python mixpanel_export.py --days 1 --limit 1000
```

Specify custom output file:
```bash
python mixpanel_export.py --days 7 --output data/events.jsonl
```

### Event Filtering

Filter by event type:
```bash
python mixpanel_export.py --days 7 --event-type "Page View"
```

Combine filters:
```bash
python mixpanel_export.py \
  --days 7 \
  --event-type "Button Click" \
  --limit 5000 \
  --output clicks.jsonl
```

### CLI Options

```
Options:
  --from-date TEXT     Start date in YYYY-MM-DD format
  --to-date TEXT       End date in YYYY-MM-DD format
  --days INTEGER       Fetch last N days (alternative to date range)
  --limit INTEGER      Maximum number of events to fetch
  --output TEXT        Output file path (default: mixpanel_export.jsonl)
  --event-type TEXT    Filter by specific event type/name
  --help               Show this message and exit
```

## Output Format

The tool outputs data in JSONL (JSON Lines) format, where each line is a valid JSON object representing one event:

```json
{"event":"Page View","properties":{"time":1704067200,"distinct_id":"user123","page":"/home"}}
{"event":"Button Click","properties":{"time":1704067300,"distinct_id":"user456","button":"signup"}}
```

This format is:
- **Streamable**: Process large files line-by-line without loading everything into memory
- **Standard**: Widely supported by data tools (Pandas, jq, BigQuery, etc.)
- **Efficient**: No need for commas between records or wrapping arrays

### Working with JSONL

Count events:
```bash
wc -l mixpanel_export.jsonl
```

Pretty-print first event:
```bash
head -n 1 mixpanel_export.jsonl | jq
```

Filter with jq:
```bash
cat mixpanel_export.jsonl | jq 'select(.event == "Page View")'
```

Load in Python:
```python
import json

events = []
with open("mixpanel_export.jsonl", "r") as f:
    for line in f:
        events.append(json.loads(line))
```

Load in Pandas:
```python
import pandas as pd

df = pd.read_json("mixpanel_export.jsonl", lines=True)
```

## Error Handling

The tool includes basic error handling:

- **Authentication errors (401/403)**: Clear error message with credential check reminder
- **Invalid inputs**: Clear error messages for date format issues
- **Network errors**: Displays error message and exits gracefully

## Project Structure

```
mixpanel-export/
├── mixpanel_export.py      # Main CLI application
├── app.py                   # Legacy script (archived)
├── requirements.txt         # Core dependencies
├── requirements-dev.txt     # Development dependencies
├── README.md               # This file
├── .env.example            # Credential template
└── .gitignore             # Git ignore rules
```

## Migration from Legacy Script

If you're migrating from the old `app.py` script:

### Old Way
```python
# Edit app.py source code
FROM_DATE = "2025-01-01"
TO_DATE = "2025-01-31"
LIMIT = 1000

# Run script
python app.py
```

### New Way
```bash
# Use command-line arguments
python mixpanel_export.py \
  --from-date 2025-01-01 \
  --to-date 2025-01-31 \
  --limit 1000
```

### Key Improvements

| Feature | Old Script | New Tool |
|---------|------------|----------|
| Configuration | Hardcoded in source | CLI arguments |
| Error handling | Basic | Clear error messages |
| Date ranges | Manual editing | Absolute or relative |
| Output format | JSONL | JSONL (identical) |

## Troubleshooting

### "Missing credentials in .env file"
- Ensure `.env` file exists in the project root
- Check all three variables are set: `MIXPANEL_USERNAME`, `MIXPANEL_SECRET`, `MIXPANEL_PROJECT_ID`
- No quotes needed around values in `.env`

### "Authentication error (401/403)"
- Verify your service account credentials are correct
- Ensure the service account has "Export" permissions
- Check if the secret has expired (regenerate if needed)

### "No events found"
- Verify the date range contains data
- Check if event type filter is too restrictive
- Try without filters first to confirm data exists

## API Reference

### Mixpanel Export API

This tool uses the Mixpanel Raw Data Export API:
- **Endpoint**: `https://data.mixpanel.com/api/2.0/export`
- **Authentication**: HTTP Basic Auth
- **Documentation**: [Mixpanel Export API Docs](https://developer.mixpanel.com/reference/raw-event-export)

### Parameters

The tool sends these parameters to the API:
- `from_date` (YYYY-MM-DD): Start date
- `to_date` (YYYY-MM-DD): End date
- `project_id`: Your Mixpanel project ID
- `limit` (optional): Max events to return
- `event` (optional): JSON array of event names to filter

## Dependencies

- **click**: Command-line interface framework
- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variable management

## License

MIT License - feel free to use and modify as needed.

---

**Built with**: Python 3.10+, Click, requests, python-dotenv
