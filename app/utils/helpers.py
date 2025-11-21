# Helper functions
from flask import jsonify

def success_response(message, data=None, status=200):
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status

def error_response(message, status=400):
    return jsonify({'error': message}), status
