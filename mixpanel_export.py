#!/usr/bin/env python3
"""
Mixpanel Export CLI Tool

A simple CLI tool for exporting raw event data from Mixpanel.
"""

import base64
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import click
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_credentials():
    """Load and validate Mixpanel credentials from environment."""
    username = os.getenv("MIXPANEL_USERNAME")
    secret = os.getenv("MIXPANEL_SECRET")
    project_id = os.getenv("MIXPANEL_PROJECT_ID")

    if not all([username, secret, project_id]):
        print("Error: Missing credentials in .env file!")
        print("Required variables: MIXPANEL_USERNAME, MIXPANEL_SECRET, MIXPANEL_PROJECT_ID")
        print("See .env.example for template")
        sys.exit(1)

    return username, secret, project_id


def parse_date_range(from_date, to_date, days):
    """
    Parse date range from arguments.

    Returns dates in YYYY-MM-DD format.
    """
    if days is not None:
        # Relative date range: last N days
        if days < 1:
            raise ValueError("--days must be at least 1")

        end_date = datetime.now().date() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=days - 1)

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    elif from_date and to_date:
        # Absolute date range
        try:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {e}")

        if start > end:
            raise ValueError("--from-date must be before or equal to --to-date")

        return from_date, to_date

    elif from_date or to_date:
        raise ValueError("Both --from-date and --to-date must be specified together")

    else:
        # Default: yesterday
        yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        return yesterday, yesterday


def fetch_events(username, secret, project_id, from_date, to_date, limit=None, event_type=None, where=None):
    """
    Fetch raw events from Mixpanel Export API.

    Returns raw JSONL response text.
    """
    # Create Basic auth header
    auth_string = base64.b64encode(f"{username}:{secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_string}",
        "Accept": "application/json"
    }

    # Build API parameters
    params = {
        "from_date": from_date,
        "to_date": to_date,
        "project_id": project_id
    }

    if limit is not None:
        params["limit"] = limit

    if event_type:
        params["event"] = json.dumps([event_type])

    if where:
        params["where"] = where

    # Make the request
    url = "https://data.mixpanel.com/api/2.0/export"

    print(f"Fetching events from {from_date} to {to_date}...")
    if limit:
        print(f"Limit: {limit}")
    if event_type:
        print(f"Event type filter: {event_type}")
    if where:
        print(f"Where filter: {where}")

    response = requests.get(url, params=params, headers=headers, timeout=300)

    # Handle errors
    if response.status_code == 401 or response.status_code == 403:
        print(f"Error: Authentication failed ({response.status_code})")
        print("Check your credentials in .env file")
        sys.exit(1)
    elif response.status_code != 200:
        print(f"Error: API request failed with status {response.status_code}")
        print(response.text)
        sys.exit(1)

    return response.text.strip()


def save_events(raw_jsonl, output_file):
    """
    Save events to JSONL file.
    """
    # Create parent directories if needed
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Count events
    if not raw_jsonl:
        event_count = 0
    else:
        event_count = len([line for line in raw_jsonl.splitlines() if line.strip()])

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(raw_jsonl)
        if raw_jsonl and not raw_jsonl.endswith("\n"):
            f.write("\n")

    print(f"Saved {event_count} events to {output_file}")
    return event_count


@click.command()
@click.option(
    "--from-date",
    type=str,
    help="Start date in YYYY-MM-DD format"
)
@click.option(
    "--to-date",
    type=str,
    help="End date in YYYY-MM-DD format"
)
@click.option(
    "--days",
    type=int,
    help="Fetch last N days (alternative to --from-date/--to-date)"
)
@click.option(
    "--limit",
    type=int,
    help="Maximum number of events to fetch"
)
@click.option(
    "--output",
    type=str,
    default="/home/jay/Data/mixpanel-export/mixpanel_export.jsonl",
    help="Output file path (default: mixpanel_export.jsonl)"
)
@click.option(
    "--event-type",
    type=str,
    help="Filter by specific event type/name"
)
@click.option(
    "--where",
    type=str,
    help='Filter expression on event properties (e.g. \'properties["$referring_domain"] == "google.com"\')'
)
def main(from_date, to_date, days, limit, output, event_type, where):
    """
    Export raw event data from Mixpanel.

    Examples:

        # Export yesterday's events
        python mixpanel_export.py

        # Export last 7 days
        python mixpanel_export.py --days 7

        # Export specific date range
        python mixpanel_export.py --from-date 2025-01-01 --to-date 2025-01-31

        # Export with limit
        python mixpanel_export.py --days 1 --limit 1000

        # Filter specific event type
        python mixpanel_export.py --days 7 --event-type "Page View"

        # Filter by referring domain
        python mixpanel_export.py --days 7 --where 'properties["$referring_domain"] == "google.com"'

        # Filter by browser
        python mixpanel_export.py --days 7 --where 'properties["$browser"] == "Chrome"'

        # Combine filters with boolean operators
        python mixpanel_export.py --days 7 --event-type "Page View" --where 'properties["$referring_domain"] != "direct"'

        # Export date range filtered to specific referring domains
        python mixpanel_export.py --from-date 2025-01-01 --to-date 2025-01-31 --where 'properties["$referring_domain"] in ["example.com", "blog.example.com", "shop.example.com"]'
    """
    try:
        # Parse and validate date range
        start_date, end_date = parse_date_range(from_date, to_date, days)

        # Load credentials
        username, secret, project_id = load_credentials()

        # Fetch events
        raw_jsonl = fetch_events(
            username=username,
            secret=secret,
            project_id=project_id,
            from_date=start_date,
            to_date=end_date,
            limit=limit,
            event_type=event_type,
            where=where
        )

        # Save to file
        event_count = save_events(raw_jsonl, output)

        if event_count == 0:
            print("No events found for the specified criteria")
        else:
            print("Export completed successfully!")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExport cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
