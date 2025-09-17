# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from zoneinfo import ZoneInfo
import requests
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY environment variable is not set. "
        "Please set it to your Google Gemini API key for AI Studio usage. "
        "You can get one from https://aistudio.google.com/app/apikey"
    )


def get_weather(query: str) -> str:
    """Fetches current weather information for a location using OpenWeatherMap API (free tier).

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the current weather information.
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "OpenWeatherMap API key not set. Please set OPENWEATHER_API_KEY in your .env file."

        url = f"http://api.openweathermap.org/data/2.5/weather?q={query}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            city = data["name"]
            return f"The current weather in {city} is {temp}°C with {description}."
        elif response.status_code == 401:
            return "Invalid OpenWeatherMap API key."
        elif response.status_code == 404:
            return f"Location '{query}' not found."
        else:
            return f"Could not fetch weather for {query} (status: {response.status_code})."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"


def get_current_time(query: str) -> str:
    """Gets the current time for a city using timezone mapping and datetime.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    # Mapping of common cities to timezones
    city_timezones = {
        "san francisco": "America/Los_Angeles",
        "sf": "America/Los_Angeles",
        "new york": "America/New_York",
        "ny": "America/New_York",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "tokyo": "Asia/Tokyo",
        "berlin": "Europe/Berlin",
        "moscow": "Europe/Moscow",
        "sydney": "Australia/Sydney",
        "los angeles": "America/Los_Angeles",
        "chicago": "America/Chicago",
        "miami": "America/New_York",  # Same as NY
        "seattle": "America/Los_Angeles",
        "vancouver": "America/Vancouver",
        "toronto": "America/Toronto",
        "mexico city": "America/Mexico_City",
        "rio de janeiro": "America/Sao_Paulo",
        "buenos aires": "America/Argentina/Buenos_Aires",
        "cairo": "Africa/Cairo",
        "mumbai": "Asia/Kolkata",
        "beijing": "Asia/Shanghai",
        "shanghai": "Asia/Shanghai",
        "hong kong": "Asia/Hong_Kong",
        "singapore": "Asia/Singapore",
        "bangkok": "Asia/Bangkok",
        "dubai": "Asia/Dubai",
        "istanbul": "Europe/Istanbul",
        "rome": "Europe/Rome",
        "madrid": "Europe/Madrid",
        "amsterdam": "Europe/Amsterdam",
        "zurich": "Europe/Zurich",
        "vienna": "Europe/Vienna",
        "prague": "Europe/Prague",
        "warsaw": "Europe/Warsaw",
        "stockholm": "Europe/Stockholm",
        "oslo": "Europe/Oslo",
        "copenhagen": "Europe/Copenhagen",
        "helsinki": "Europe/Helsinki",
        "athens": "Europe/Athens",
        "jerusalem": "Asia/Jerusalem",
        "cape town": "Africa/Johannesburg",
        "johannesburg": "Africa/Johannesburg",
        "nairobi": "Africa/Nairobi",
        "lagos": "Africa/Lagos",
        "accra": "Africa/Accra",
        "dakar": "Africa/Dakar",
    }

    tz_identifier = city_timezones.get(query.lower())
    if tz_identifier:
        try:
            tz = ZoneInfo(tz_identifier)
            now = datetime.datetime.now(tz)
            return f"The current time in {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}."
        except Exception as e:
            return f"Error retrieving time for {query}: {str(e)}"
    else:
        return f"Sorry, I don't have timezone information for {query}. Try a major city name."


def get_travel_guide(city: str) -> str:
    """Fetches a brief travel guide for a city using Wikipedia API.

    Args:
        city: The name of the city to get travel guide for.

    Returns:
        A string with a brief travel guide.
    """
    try:
        headers = {"User-Agent": "event-planner/1.0"}
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city.replace(' ', '_')}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract")
            if extract:
                return extract
            else:
                return f"No detailed travel guide found for {city}. It may be a disambiguation page."
        else:
            return f"Could not fetch travel guide for {city} (status: {response.status_code})."
    except Exception as e:
        return f"Error fetching travel guide: {str(e)}"


def get_events(city: str, date: str = "") -> str:
    """Fetches upcoming events for a city using Eventbrite API (free tier).

    Args:
        city: The name of the city to get events for.
        date: Optional date filter in YYYY-MM-DD format.

    Returns:
        A string listing upcoming events.
    """
    try:
        token = os.getenv("EVENTBRITE_API_TOKEN")
        if not token:
            return "Eventbrite API token not set."

        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "location.address": city,
            "start_date.range_start": f"{date}T00:00:00Z" if date else "",
            "start_date.range_end": f"{date}T23:59:59Z" if date else "",
            "sort_by": "date",
            "page": 1,
        }
        url = "https://www.eventbriteapi.com/v3/events/search/"
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            if not events:
                return f"No upcoming events found for {city} on {date or 'any date'}."
            event_list = [f"{event['name']['text']} on {event['start']['local']}" for event in events[:5]]
            return "Upcoming events:\n" + "\n".join(event_list)
        else:
            return f"Could not fetch events for {city}."
    except Exception as e:
        return f"Error fetching events: {str(e)}"


def get_attractions(city: str) -> str:
    """Fetches popular attractions for a city using Foursquare Places API (free tier).

    Args:
        city: The name of the city to get attractions for.

    Returns:
        A string listing popular attractions.
    """
    try:
        client_id = os.getenv("FOURSQUARE_CLIENT_ID")
        client_secret = os.getenv("FOURSQUARE_CLIENT_SECRET")
        if not client_id or not client_secret:
            return "Foursquare API credentials not set."

        # Get city coordinates using Nominatim (OpenStreetMap)
        geo_url = f"https://nominatim.openstreetmap.org/search"
        geo_params = {"q": city, "format": "json", "limit": 1}
        geo_resp = requests.get(geo_url, params=geo_params, timeout=5)
        if geo_resp.status_code != 200 or not geo_resp.json():
            return f"Could not get coordinates for {city}."
        coords = geo_resp.json()[0]
        lat, lon = coords["lat"], coords["lon"]

        # Search for attractions
        places_url = "https://api.foursquare.com/v2/venues/explore"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "v": "20230101",
            "ll": f"{lat},{lon}",
            "section": "sights",
            "limit": 5,
        }
        places_resp = requests.get(places_url, params=params, timeout=5)
        if places_resp.status_code == 200:
            data = places_resp.json()
            items = data.get("response", {}).get("groups", [])[0].get("items", [])
            if not items:
                return f"No attractions found for {city}."
            attractions = [item["venue"]["name"] for item in items]
            return "Popular attractions:\n" + "\n".join(attractions)
        else:
            return f"Could not fetch attractions for {city}."
    except Exception as e:
        return f"Error fetching attractions: {str(e)}"


root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="""
You are a helpful AI assistant designed to provide accurate and useful travel planning information.
You can provide weather, current time, travel guides, upcoming events, and popular attractions for cities.
Use the appropriate tool for each user query.
""",
    tools=[get_weather, get_current_time, get_travel_guide, get_events, get_attractions],
)
