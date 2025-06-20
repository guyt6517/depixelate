from app import app  # replace 'app' with your actual Flask app filename (without .py)

# Expose the WSGI callable as 'application' for Gunicorn
application = app
