"""Error handlers middleware."""

from flask import jsonify
from werkzeug.exceptions import HTTPException


def handle_404(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404


def handle_500(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred'
    }), 500


def handle_validation_error(error):
    """Handle validation errors."""
    return jsonify({
        'error': 'Validation Error',
        'message': str(error)
    }), 400


def handle_http_exception(error):
    """Handle HTTP exceptions."""
    response = {
        'error': error.name,
        'message': error.description
    }
    return jsonify(response), error.code
