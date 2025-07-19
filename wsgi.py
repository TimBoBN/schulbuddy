"""
WSGI Entry Point für SchulBuddy
Production WSGI application entry point
"""
from app import create_app

# Create the Flask application instance
application = create_app()

if __name__ == "__main__":
    application.run()
