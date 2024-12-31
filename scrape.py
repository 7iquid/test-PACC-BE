import requests
import json
from collections import defaultdict
from typing import List, Dict

# Constants
API_ENDPOINT = "https://api.app.studiospace.com/listings/list-agencies"
SERVICE_GROUPS = ["Advertising, Brand & Creative", "Media, PR & Events", "others"]
REGIONS = ["AU", "GB", "US", "OTHERS"]
TARGETOUTPUT = [
    {
        "locations": "AU",
        "services": [
            {"name": "Advertising, Brand & Creative", "counts": 0},
            {"name": "Media, PR & Events", "counts": 0},
            {"name": "others", "counts": 0},
        ],
    },
    {
        "locations": "GB",
        "services": [
            {"name": "Advertising, Brand & Creative", "counts": 0},
            {"name": "Media, PR & Events", "counts": 0},
            {"name": "others", "counts": 0},
        ],
    },
    {
        "locations": "US",
        "services": [
            {"name": "Advertising, Brand & Creative", "counts": 0},
            {"name": "Media, PR & Events", "counts": 0},
            {"name": "others", "counts": 0},
        ],
    },
    {
        "locations": "OTHERS",
        "services": [
            {"name": "Advertising, Brand & Creative", "counts": 0},
            {"name": "Media, PR & Events", "counts": 0},
            {"name": "others", "counts": 0},
        ],
    },
]


def fetch_agencies(skip: int = 0) -> List[Dict]:
    """Fetch agencies from the API with pagination."""
    response = requests.get(f"{API_ENDPOINT}?skip={skip}")
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()[0]  # Extract 'data' portion


def check_for_region(locations: List[Dict[str, Dict[str, str]]]) -> str:
    """Determine the region based on location country codes."""
    for location in locations:
        country_code = location.get("country", {}).get("code")
        if country_code in REGIONS:
            return country_code
    return "OTHERS"


def count_agency_service(agencyService: List[Dict]) -> List[Dict[str, int]]:
    """Count services by category."""
    services = [
        {"name": "Advertising, Brand & Creative", "counts": 0},
        {"name": "Media, PR & Events", "counts": 0},
        {"name": "others", "counts": 0},
    ]

    for service in agencyService:
        group_name = service.get("service", {}).get("serviceGroup", {}).get("name", "")
        matched = False
        for entry in services:
            if entry["name"] == group_name:
                entry["counts"] += 1
                matched = True
                break
        if not matched:
            services[-1]["counts"] += 1  # Increment "others" count

    return services


def generate_target_output(
    data: List[Dict], existing_output=None
) -> Dict[str, List[Dict[str, int]]]:
    """Generate the target output dynamically."""
    if existing_output is None:
        existing_output = {
            region: [
                {"name": "Advertising, Brand & Creative", "counts": 0},
                {"name": "Media, PR & Events", "counts": 0},
                {"name": "others", "counts": 0},
            ]
            for region in REGIONS
        }

    for company in data:
        locations = company.get("locations", [])
        agencyService = company.get("agencyService", [])

        region = check_for_region(locations)
        services_count = count_agency_service(agencyService)

        for service in services_count:
            for target_service in existing_output[region]:
                if target_service["name"] == service["name"]:
                    target_service["counts"] += service["counts"]

    return existing_output


def categorize_agencies():
    retry = 0
    max_retry = 12
    data = []
    output = None

    while retry <= max_retry:
        print(f"Fetching data for skip={retry}...")
        try:
            fetched_data = fetch_agencies(skip=retry * 12)
            data.extend(fetched_data)
            output = generate_target_output(fetched_data, existing_output=output)
            retry += 1
        except requests.RequestException as e:
            print(f"Failed to fetch data: {e}")
            break

    return [
        {"locations": region, "services": services}
        for region, services in output.items()
    ]


def main():
    """Main function to run the report generation."""
    target_output = categorize_agencies()
    print(json.dumps(target_output, indent=4))


if __name__ == "__main__":
    main()
