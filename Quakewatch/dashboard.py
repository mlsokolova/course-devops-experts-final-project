"""Dashboard blueprint and earthquake route handlers."""
from datetime import datetime, timedelta

import requests
from flask import Blueprint, current_app, jsonify, render_template, request, send_file

from quakestats import QuakeStats
from utils import COUNTRIES, generate_graph, get_last_earthquake, get_top_earthquakes

REQUEST_TIMEOUT = 30
dashboard_blueprint = Blueprint('dashboard', __name__)


class EarthquakeDashboard:
    """Flask routes for earthquake dashboard pages and APIs."""

    @staticmethod
    @dashboard_blueprint.route('/')
    def main_page():
        """Render the main dashboard landing page."""
        return render_template('main_page.html')

    @staticmethod
    @dashboard_blueprint.route('/ping')
    def ping():
        """Health ping endpoint."""
        return 'pong', 200

    @staticmethod
    @dashboard_blueprint.route('/health')
    def health():
        """Return application health status."""
        return jsonify(status='ok', message='Application is healthy'), 200

    @staticmethod
    @dashboard_blueprint.route('/status')
    def status():
        """Return basic service status information."""
        status_info = {
            'service': 'Flask Application',
            'status': 'running',
            'uptime': '72 hours'
        }
        return jsonify(status_info), 200

    @staticmethod
    @dashboard_blueprint.route('/info')
    def info():
        """Return application metadata."""
        app_info = {
            'name': 'Sample Flask App',
            'version': '1.0',
            'author': 'Your Name',
            'description': 'A sample Flask application demonstrating multiple routes'
        }
        return jsonify(app_info), 200

    @staticmethod
    @dashboard_blueprint.route('/telaviv-earthquakes')
    def telaviv_earthquakes():
        """Return raw Tel Aviv earthquake data for the last 30 days."""
        start_time = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
        params = {
            'format': 'geojson',
            'latitude': 32.0853,
            'longitude': 34.7818,
            'maxradiuskm': 100,
            'starttime': start_time
        }
        usgs_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        response = requests.get(usgs_url, params=params, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            current_app.logger.error("Error fetching data from USGS API")
            return jsonify(error="Error fetching data from USGS API"), response.status_code

        data = response.json()
        processed_events = []
        for feature in data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            coordinates = geometry.get('coordinates', [])
            event_data = {
                'magnitude': properties.get('mag'),
                'place': properties.get('place'),
                'time': properties.get('time'),
                'coordinates': {
                    'longitude': coordinates[0] if len(coordinates) > 0 else None,
                    'latitude': coordinates[1] if len(coordinates) > 1 else None,
                    'depth': coordinates[2] if len(coordinates) > 2 else None,
                },
                'type': properties.get('type')
            }
            processed_events.append(event_data)
        result = {
            'count': len(processed_events),
            'events': processed_events
        }
        return jsonify(result), 200

    @staticmethod
    @dashboard_blueprint.route('/graph-earthquakes.png')
    def graph_earthquakes_image():
        """Return a PNG graph of recent earthquakes for a location."""
        days = int(request.args.get('days', 30))
        loc_name = request.args.get('location', "Tel Aviv, Israel")
        location = COUNTRIES.get(loc_name, COUNTRIES["Tel Aviv, Israel"])
        img = generate_graph(days, location["lat"], location["lon"], location["radius"])
        return send_file(img, mimetype='image/png')

    @staticmethod
    @dashboard_blueprint.route('/graph-earthquakes-5years.png')
    def graph_earthquakes_5years_image():
        """Return a PNG graph of earthquakes over the last five years."""
        days = 5 * 365
        loc_name = request.args.get('location', "Tel Aviv, Israel")
        location = COUNTRIES.get(loc_name, COUNTRIES["Tel Aviv, Israel"])
        img = generate_graph(
            days,
            location["lat"],
            location["lon"],
            location["radius"],
            title_suffix="(5 Years)",
        )
        return send_file(img, mimetype='image/png')

    @staticmethod
    def get_quake_stats(loc_name):
        """Build QuakeStats for the given location name."""
        location = COUNTRIES.get(loc_name)
        latitude = location["lat"]
        longitude = location["lon"]
        radius = location["radius"]
        return QuakeStats(latitude, longitude, radius)

    @staticmethod
    @dashboard_blueprint.route('/graph-earthquakes')
    def graph_earthquakes_page():
        """Render the interactive earthquake graph dashboard."""
        days = int(request.args.get('days', 30))
        loc_name = request.args.get('location', "Tel Aviv, Israel")
        top_events = get_top_earthquakes(limit=5)
        last_event = get_last_earthquake()
        stats = EarthquakeDashboard.get_quake_stats(loc_name)
        return render_template(
            'graph_dashboard.html',
            days=days,
            current_location=loc_name,
            countries=list(COUNTRIES.keys()),
            top_events=top_events,
            last_event=last_event,
            stats=stats.stats,
            max_earthquake=stats.max_earthquake,
            earthquakes_stats=stats.stats,
        )
