import requests

def get_weather(city: str):
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
        timeout=10,
    ).json().get("results")

    if not geo:
        print(f"City '{city}' not found.")
        return

    lat, lon, name = geo[0]["latitude"], geo[0]["longitude"], geo[0]["name"]

    data = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "weather_code"],
        },
        timeout=10,
    ).json()["current"]

    conditions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Rain showers", 95: "Thunderstorm",
    }
    condition = conditions.get(data["weather_code"], "Unknown")

    print(f"\nWeather in {name}:")
    print(f"  Condition : {condition}")
    print(f"  Temp      : {data['temperature_2m']}°C")
    print(f"  Humidity  : {data['relative_humidity_2m']}%")
    print(f"  Wind      : {data['wind_speed_10m']} km/h\n")


city = input("Enter city: ")
get_weather(city)
