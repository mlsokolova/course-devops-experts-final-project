"""Flask application factory for QuakeWatch."""
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, request

from dashboard import dashboard_blueprint
from utils import timestamp_to_str


def create_app():
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)

    log_path = os.getenv('QUAKEWATCH__LOG_PATH')
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    error_handler = RotatingFileHandler(f'{log_path}/error.log', maxBytes=1000000, backupCount=3)
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    flask_app.logger.addHandler(error_handler)

    usage_handler = RotatingFileHandler(f'{log_path}/access.log', maxBytes=1000000, backupCount=3)
    usage_handler.setLevel(logging.INFO)
    usage_formatter = logging.Formatter('%(asctime)s - %(message)s')
    usage_handler.setFormatter(usage_formatter)
    usage_logger = logging.getLogger('usage')
    usage_logger.addHandler(usage_handler)
    usage_logger.setLevel(logging.INFO)

    @flask_app.before_request
    def log_request_info():
        usage_logger.info("%s - %s %s", request.remote_addr, request.method, request.url)

    flask_app.register_blueprint(dashboard_blueprint)
    flask_app.jinja_env.filters['timestamp_to_str'] = timestamp_to_str

    return flask_app


if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', debug=True)
