from flask import Flask, request
from flask_smorest import Api, Blueprint
from scrape import AgencyServiceCounter
import json
import asyncio

app = Flask(__name__)

app.config["API_TITLE"] = "Simple API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

blp = Blueprint(
    "simple", __name__, url_prefix="/api", description="A simple blueprint."
)

@blp.route("/list-agencies")
async def list_agencies():
    """Get list of agencies with optional filters."""
    # Retrieve query parameters
    params = request.args.to_dict()

    # Parse specific parameters as lists
    regions = json.loads(
        params.get("regions", '["AU", "GB", "US", "OTHERS"]')
    )  # Default value if no regions specified
    service_groups = json.loads(
        params.get(
            "service_groups",
            '["Advertising, Brand & Creative", "Media, PR & Events", "others"]',
        )
    )  # Default value if no service_groups specified
    retry_limit = int(params.get("skip", 12))  # Default to 12 retries if not specified

    # Ensure "OTHERS" is in regions and service_groups, add it if missing
    if "OTHERS" not in regions:
        regions.append("OTHERS")
    if "others" not in service_groups:
        service_groups.append("others")

    # Initialize AgencyServiceCounter with parameters
    counter = AgencyServiceCounter(
        regions=regions,
        service_groups=service_groups,
        api_endpoint="https://api.app.studiospace.com/listings/list-agencies",
    )

    # Generate the output asynchronously
    target_output = await counter.generate_output(retry=retry_limit)

    return {
        "message": "Data fetched successfully",
        "data": target_output,
        "code": 200
    }

api.register_blueprint(blp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
