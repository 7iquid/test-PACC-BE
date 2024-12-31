import asyncio
import aiohttp
import json
from typing import List, Dict


class AgencyServiceCounter:
    def __init__(
        self, regions: List[str], service_groups: List[str], api_endpoint: str
    ):
        # Initialize the class with regions, service groups, and the API endpoint
        self.REGIONS = regions
        self.SERVICE_GROUPS = service_groups
        self.API_ENDPOINT = api_endpoint
        # Set up the initial output structure
        self.output = {
            region: [{"name": group, "counts": 0} for group in service_groups]
            for region in regions
        }

    async def fetch_agencies(self, skip: int) -> List[Dict]:
        """Fetch agencies from the API asynchronously."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.API_ENDPOINT}?skip={skip}") as response:
                response.raise_for_status()  # Raise an error for bad status codes
                # Await the response and return it
                return (await response.json())[0]

    def check_for_region(self, locations: List[Dict[str, Dict[str, str]]]) -> str:
        """Determine the region based on location country codes."""
        for location in locations:
            country_code = location.get("country", {}).get("code")
            if country_code in self.REGIONS:
                return country_code
        return "OTHERS"

    def count_agency_service(self, agencyService: List[Dict]) -> List[Dict[str, int]]:
        """Count services by category."""
        services = [{"name": group, "counts": 0} for group in self.SERVICE_GROUPS]
        for service in agencyService:
            group_name = (
                service.get("service", {}).get("serviceGroup", {}).get("name", "")
            )
            for entry in services:
                if entry["name"] == group_name:
                    entry["counts"] += 1
                    break
            else:
                services[-1]["counts"] += 1  # Increment "others" count
        return services

    async def generate_output(self, retry: int) -> List[Dict]:
        """Generate the final target output asynchronously."""
        skip_count = 0
        tasks = []

        while skip_count <= retry:
            # Pass skip as a keyword argument to avoid multiple values being passed
            tasks.append(
                self.fetch_agencies(skip=skip_count)
            )  # Add the coroutine task to the list
            skip_count += 1

        # Run all tasks asynchronously and collect the results
        fetched_data_list = await asyncio.gather(*tasks)

        # Process each of the fetched data
        for fetched_data in fetched_data_list:
            for company in fetched_data:
                locations = company.get("locations", [])
                agencyService = company.get("agencyService", [])
                region = self.check_for_region(locations)
                services_count = self.count_agency_service(agencyService)
                for service in services_count:
                    for target_service in self.output[region]:
                        if target_service["name"] == service["name"]:
                            target_service["counts"] += service["counts"]

        return [
            {"locations": region, "services": services}
            for region, services in self.output.items()
        ]


async def main():
    """Main function to run the report generation asynchronously."""
    regions = ["AU", "GB", "US", "OTHERS"]
    service_groups = ["Advertising, Brand & Creative", "Media, PR & Events", "others"]
    api_endpoint = "https://api.app.studiospace.com/listings/list-agencies"
    retry_limit = 12

    # Create an instance of AgencyServiceCounter
    counter = AgencyServiceCounter(
        regions=regions, service_groups=service_groups, api_endpoint=api_endpoint
    )

    # Generate the output asynchronously
    target_output = await counter.generate_output(retry=retry_limit)

    # Print the result
    print(json.dumps(target_output, indent=4))


if __name__ == "__main__":
    asyncio.run(main())  # Run the async main function
