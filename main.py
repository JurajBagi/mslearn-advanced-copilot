import json
from os.path import dirname, abspath, join
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles


current_dir = dirname(abspath(__file__))
wellknown_path = join(current_dir, ".well-known")
historical_data = join(current_dir, "weather.json")

app = FastAPI()
app.mount("/.well-known", StaticFiles(directory=wellknown_path), name="static")


# load historical json data and serialize it:
with open(historical_data, "r") as f:
    data = json.load(f)

@app.get('/')
def root():
    """
    Allows to open the API documentation in the browser directly instead of
    requiring to open the /docs path.
    """
    return RedirectResponse(url='/docs', status_code=301)


@app.get('/countries')
def countries():
    return list(data.keys())


@app.get('/countries/{country}')
def cities(country: str, month: Optional[str] = None) -> Dict[str, Any]:
    """List cities for a given country.

    When a month is provided, returns historical high/low data for each city
    in that country for the given month.

    Parameters:
        country: Country name as it appears in the dataset.
        month: Optional month name (e.g., "January").

    Returns:
        A JSON object including the country, a list of cities, and optionally
        a per-city mapping of historical high/low for the requested month.
    """
    if country not in data:
        raise HTTPException(status_code=404, detail=f"Unknown country: {country}")

    cities_by_country = data[country]
    city_names = sorted(cities_by_country.keys())

    if month is None:
        return {"country": country, "cities": city_names}

    # Validate month using the first city's record (dataset is expected to be consistent).
    first_city = next(iter(cities_by_country.values()), None)
    if not first_city or month not in first_city:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown month '{month}' for country '{country}'",
        )

    by_city = {city: cities_by_country[city][month] for city in city_names}
    return {"country": country, "month": month, "cities": by_city}


@app.get('/countries/{country}/{city}/{month}')
def monthly_average(country: str, city: str, month: str):
    return data[country][city][month]

# Generate the OpenAPI schema:
openapi_schema = app.openapi()
with open(join(wellknown_path, "openapi.json"), "w") as f:
    json.dump(openapi_schema, f)