"""Shared helpers for USGS API access and earthquake graph generation."""
import io
from collections import defaultdict
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import requests

REQUEST_TIMEOUT = 30

COUNTRIES = {
    "Tel Aviv, Israel": {"lat": 32.0853, "lon": 34.7818, "radius": 300},
    "United States (California)": {"lat": 36.7783, "lon": -119.4179, "radius": 300},
    "Japan": {"lat": 36.2048, "lon": 138.2529, "radius": 300},
    "Indonesia": {"lat": -1.5000, "lon": 99.5000, "radius": 300},
    "Chile": {"lat": -35.6751, "lon": -71.5430, "radius": 300}
}

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def _fetch_usgs_geojson(params):
    """Fetch earthquake GeoJSON from the USGS API."""
    return requests.get(USGS_URL, params=params, timeout=REQUEST_TIMEOUT)


def _counts_by_day_from_geojson(data):
    """Aggregate earthquake counts per day from USGS GeoJSON."""
    counts_by_day = defaultdict(int)
    for feature in data.get('features', []):
        timestamp = feature.get('properties', {}).get('time')
        if timestamp:
            event_date = datetime.utcfromtimestamp(timestamp / 1000).date()
            counts_by_day[event_date] += 1
    return counts_by_day


def _render_chart(counts_by_day, days, title_suffix):
    """Draw the earthquake bar chart or an empty/error placeholder."""
    plt.figure(figsize=(10, 5))
    if not counts_by_day:
        plt.text(
            0.5, 0.5, "No earthquake data available",
            horizontalalignment='center', verticalalignment='center', fontsize=14,
        )
        plt.axis('off')
        return

    days_list = sorted(counts_by_day.keys())
    counts = [counts_by_day[day] for day in days_list]
    plt.bar(days_list, counts)
    plt.xlabel('Date')
    plt.ylabel('Number of Earthquakes')
    plt.title(f'Earthquakes in Last {days} Days {title_suffix}')
    plt.xticks(rotation=45)
    plt.tight_layout()


def generate_graph(days, lat, lon, radius, title_suffix=""):
    """Generate a PNG bar chart of earthquakes near the given coordinates."""
    start_time = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
    params = {
        'format': 'geojson',
        'latitude': lat,
        'longitude': lon,
        'maxradiuskm': radius,
        'starttime': start_time
    }
    response = _fetch_usgs_geojson(params)

    if response.status_code != 200:
        plt.figure(figsize=(10, 5))
        plt.text(
            0.5, 0.5, "Error fetching data",
            horizontalalignment='center', verticalalignment='center', fontsize=14,
        )
        plt.axis('off')
    else:
        counts_by_day = _counts_by_day_from_geojson(response.json())
        _render_chart(counts_by_day, days, title_suffix)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return img


def get_top_earthquakes(limit=5):
    """Return the strongest earthquakes worldwide in the last 30 days."""
    start_time = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    params = {
        'format': 'geojson',
        'starttime': start_time,
        'minmagnitude': 1
    }
    response = _fetch_usgs_geojson(params)
    if response.status_code != 200:
        return []

    data = response.json()
    events = sorted(
        data.get('features', []),
        key=lambda feature: feature.get('properties', {}).get('mag', 0),
        reverse=True,
    )
    return events[:limit]


def get_last_earthquake():
    """Return the most recent earthquake worldwide in the last 30 days."""
    start_time = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    params = {
        'format': 'geojson',
        'starttime': start_time,
        'minmagnitude': 1
    }
    response = _fetch_usgs_geojson(params)
    if response.status_code != 200:
        return None

    events = sorted(
        response.json().get('features', []),
        key=lambda feature: feature.get('properties', {}).get('time', 0),
        reverse=True,
    )
    return events[0] if events else None


def timestamp_to_str(ts):
    """Format a USGS millisecond timestamp as a UTC datetime string."""
    return datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
