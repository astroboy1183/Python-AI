# weather agent — chain of thought + landmark support + streaming

from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a weather assistant that reasons out loud, step by step, before every answer.

ALWAYS output every step explicitly, even if the answer seems obvious.

─────────────────────────────────────────────────
[Step 1 — Analyze the query]
  • Read the user's query carefully.
  • Is it a city name, or something else — a railway station, airport, monument, neighbourhood, landmark?
  • State clearly what type of place it is.

[Step 2 — Identify the city/region]
  • If it is a CITY → use the city name directly in the search.
  • If it is a LANDMARK (station, airport, temple, monument, market, etc.) → use your knowledge to name the exact city/town/district it is located in. State this city out loud before searching.
    Example: "Pandit Deen Dayal Upadhyay Junction is a railway station located in Mughalsarai, Uttar Pradesh, India. I will search for 'Mughalsarai'."
  • Never search for the landmark name directly — geocoding APIs only know about populated places.

[Step 3 — Search for the location]
  • Call search_locations with the city/town name you identified.
  • Look at all results returned.

[Step 4 — Resolve ambiguity]
  • If results are from different countries or regions → ask the user which one they mean. List the options clearly.
  • If only one relevant result → confirm it out loud and proceed.
  • If user already specified the country/state → pick the matching result directly.

[Step 5 — Fetch the weather]
  • Call get_weather with the exact latitude, longitude, and a full display name (city + country).
  • State that you are now fetching live weather data.

[Step 6 — Present the result]
  • Always state the full location name (e.g. "Mughalsarai, Uttar Pradesh, India") so the user knows exactly where the data is from.
  • If the original query was a landmark, remind the user that the weather is for the city the landmark is in.
  • Show: condition, temperature (°C), feels like (°C), humidity (%), wind speed (km/h).
─────────────────────────────────────────────────

Never skip or merge steps. Transparency helps the user catch mistakes."""

# ── Tool implementations ──────────────────────────────────────────────────────

def search_locations(query: str) -> str:
    resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": query, "count": 5, "language": "en"},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])

    if not results:
        return json.dumps({"error": f"No locations found for '{query}'. Try a nearby city or district name."})

    return json.dumps({
        "locations": [
            {
                "name": r.get("name"),
                "region": r.get("admin1", ""),
                "country": r.get("country"),
                "country_code": r.get("country_code"),
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "population": r.get("population", 0),
            }
            for r in results
        ]
    })


def get_weather(latitude: float, longitude: float, location_name: str) -> str:
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "wind_speed_10m",
                "weather_code",
                "precipitation",
            ],
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()["current"]

    wmo_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
        80: "Light rain showers", 81: "Moderate rain showers", 82: "Heavy rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
    }

    return json.dumps({
        "location": location_name,
        "condition": wmo_codes.get(data["weather_code"], "Unknown"),
        "temperature_c": data["temperature_2m"],
        "feels_like_c": data["apparent_temperature"],
        "humidity_percent": data["relative_humidity_2m"],
        "wind_speed_kmh": data["wind_speed_10m"],
        "precipitation_mm": data["precipitation"],
    })


# ── Tool schemas ──────────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_locations",
            "description": (
                "Search for a city or town by name. Returns up to 5 matches with country, "
                "region, and coordinates. Use city/town names only — not landmark names."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "City or town name, e.g. 'Mughalsarai', 'London', 'Springfield'",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Fetch real-time weather using exact coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "location_name": {
                        "type": "string",
                        "description": "Full display name, e.g. 'Mughalsarai, Uttar Pradesh, India'",
                    },
                },
                "required": ["latitude", "longitude", "location_name"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "search_locations": search_locations,
    "get_weather": get_weather,
}

# ── Streaming agent loop ──────────────────────────────────────────────────────

def agent_turn(messages: list) -> str:
    """Stream one agent turn, printing reasoning live and showing tool calls inline."""
    while True:
        print("  [OpenAI API] Sending request to gpt-4o-mini...\n")
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=True,
        )

        full_content = ""
        tool_calls = []   # accumulated tool calls from stream deltas

        for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta

            # Stream text tokens live
            if delta.content:
                print(delta.content, end="", flush=True)
                full_content += delta.content

            # Accumulate tool call deltas
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    while len(tool_calls) <= idx:
                        tool_calls.append({"id": "", "function": {"name": "", "arguments": ""}})
                    if tc_delta.id:
                        tool_calls[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            tool_calls[idx]["function"]["name"] += tc_delta.function.name
                        if tc_delta.function.arguments:
                            tool_calls[idx]["function"]["arguments"] += tc_delta.function.arguments

        if full_content:
            print()  # newline after streamed text

        # No tool calls → final answer
        if not tool_calls:
            messages.append({"role": "assistant", "content": full_content})
            return full_content

        # Append assistant message (may include intermediate reasoning text + tool calls)
        messages.append({
            "role": "assistant",
            "content": full_content or None,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"],
                    },
                }
                for tc in tool_calls
            ],
        })

        # Execute tools and show progress
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            fn_args = json.loads(tc["function"]["arguments"])

            api_label = {
                "search_locations": "Open-Meteo Geocoding API",
                "get_weather": "Open-Meteo Weather API",
            }.get(fn_name, "External API")
            print(f"\n  [{api_label}] Calling {fn_name}({fn_args})")

            fn = TOOL_FUNCTIONS.get(fn_name)
            result = fn(**fn_args) if fn else json.dumps({"error": "unknown tool"})

            parsed = json.loads(result)
            if fn_name == "search_locations" and "locations" in parsed:
                for loc in parsed["locations"]:
                    region = f", {loc['region']}" if loc["region"] else ""
                    print(f"      Found: {loc['name']}{region}, {loc['country']} ({loc['latitude']}°N, {loc['longitude']}°E)")
            elif fn_name == "get_weather" and "temperature_c" in parsed:
                print(f"      Got weather data for {parsed['location']}")
            elif "error" in parsed:
                print(f"      Error: {parsed['error']}")
            print()

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Weather Agent — Chain of Thought + Landmark Support")
    print("=" * 60)
    print("Type 'quit' to exit\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("quit", "exit"):
            break

        messages.append({"role": "user", "content": user_input})
        print("\nAgent:\n")
        agent_turn(messages)
        print()


if __name__ == "__main__":
    main()
