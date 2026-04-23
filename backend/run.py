"""
Entry point for the Weni Public Roadmap API.

Run with:
    flask run --port 5000

Or in production:
    gunicorn -w 4 -b 0.0.0.0:5000 run:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
