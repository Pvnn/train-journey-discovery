from flask import Flask, jsonify, request, g, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import time
import os

# Import the API blueprint (no backend. prefix since we're already in backend/)
from api.routes import api_bp

# Import logger (no backend. prefix)
from utils.logger import (
  api_logger,
  log_request,
  log_response,
  log_error,
  info
)

app = Flask(__name__)
CORS(app)

# Register API blueprint
app.register_blueprint(api_bp)


# ============================================================================
# SWAGGER UI CONFIGURATION
# ============================================================================

# Swagger UI configuration
SWAGGER_URL = '/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.yaml'  # URL to serve OpenAPI spec

# Create swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
  SWAGGER_URL,
  API_URL,
  config={
    'app_name': "Train Journey Discovery API",
    'layout': "BaseLayout",
    'deepLinking': True,
    'displayRequestDuration': True,
    'docExpansion': 'none',
    'filter': True,
    'showExtensions': True,
    'showCommonExtensions': True,
    'defaultModelsExpandDepth': 3,
    'defaultModelExpandDepth': 3
  }
)

# Register swagger UI blueprint
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Serve swagger.yaml file from docs directory
@app.route('/static/swagger.yaml')
def swagger_spec():
  """Serve the OpenAPI specification file from docs directory."""
  try:
    # Since app.py is in backend/, look for docs/swagger.yaml
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')

    if os.path.exists(os.path.join(docs_dir, 'swagger.yaml')):
      return send_from_directory(docs_dir, 'swagger.yaml')
    else:
      api_logger.error(f"swagger.yaml not found in {docs_dir}")
      return jsonify({
        "error": "Swagger spec not found",
        "expected_path": os.path.join(docs_dir, 'swagger.yaml')
      }), 404

  except Exception as e:
    api_logger.error(f"Failed to serve swagger.yaml: {str(e)}")
    return jsonify({"error": f"Failed to serve swagger spec: {str(e)}"}), 500


# ============================================================================
# LOGGING MIDDLEWARE
# ============================================================================

@app.before_request
def before_request_logging():
  """
  Middleware to log incoming requests and start timing.

  Executes before each request to:
  - Record start time for duration calculation
  - Log request details (method, path, query params, body)
  """
  # Skip logging for static files and docs
  if request.path.startswith('/static') or request.path.startswith('/docs'):
    g.start_time = time.time()
    return

  # Record start time
  g.start_time = time.time()

  # Get request details
  method = request.method
  path = request.path
  query_params = dict(request.args) if request.args else None

  # Get request body (only for POST/PUT/PATCH)
  body = None
  if method in ['POST', 'PUT', 'PATCH']:
    try:
      body = request.get_json(silent=True)
    except Exception:
      body = None

  # Log the incoming request
  log_request(method, path, query_params, body)


@app.after_request
def after_request_logging(response):
  """
  Middleware to log outgoing responses with duration and size.

  Executes after each request to:
  - Calculate request duration
  - Log response details (status code, size, duration)

  Args:
    response: Flask response object

  Returns:
    Unmodified response object
  """
  # Skip logging for static files and docs
  if request.path.startswith('/static') or request.path.startswith('/docs'):
    return response

  # Calculate duration
  duration_ms = 0
  if hasattr(g, 'start_time'):
    duration_ms = (time.time() - g.start_time) * 1000

  # Get response details
  method = request.method
  path = request.path
  status_code = response.status_code

  # Calculate response size
  response_size = 0
  if response.data:
    response_size = len(response.data)

  # Log the outgoing response
  log_response(method, path, status_code, response_size, duration_ms)

  return response


@app.errorhandler(Exception)
def handle_exception(error):
  """
  Global exception handler to log unhandled errors.

  Catches any exceptions that weren't handled by route handlers
  and logs them with full traceback.

  Args:
    error: Exception object

  Returns:
    JSON error response with 500 status code
  """
  # Log the error with full traceback
  log_error(request.method, request.path, error, include_traceback=True)

  # Return generic error response
  return jsonify({
    "error": {
      "code": 500,
      "message": "Internal server error",
      "details": {
        "error": str(error),
        "error_type": type(error).__name__
      }
    }
  }), 500


# ============================================================================
# BASIC ROUTES
# ============================================================================

@app.route('/')
def home():
  """Root endpoint - API information."""
  return jsonify({
    "status": "ok",
    "message": "TRAIN JOURNEY DISCOVERY API",
    "version": "1.0.0",
    "documentation": "http://localhost:5000/docs",
    "endpoints": {
      "health": "/api/health",
      "search": "/api/search",
      "stations": "/api/stations",
      "docs": "/docs"
    }
  })


@app.route('/api/health')
def health():
  """Health check endpoint."""
  return jsonify({
    "status": "healthy",
    "service": "Journey Search API",
    "version": "1.0.0"
  })


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
  # Log application startup
  info("="*60)
  info("Starting Train Journey Discovery API")
  info("Version: 1.0.0")
  info("Port: 5000")
  info("Debug Mode: True")
  info("Logging: Enabled (Console + File)")
  info("Log File: logs/api.log")
  info("Swagger UI: http://localhost:5000/docs")
  info("Swagger Spec: docs/swagger.yaml")
  info("="*60)

  # Start Flask application
  app.run(debug=True, port=5000)