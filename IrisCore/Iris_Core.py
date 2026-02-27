from config import Config
from app import create_app, start_app

print("DO: https://youtube.com/shorts/SUOEgaPL6xM")

if __name__ == "__main__":
    app = create_app(Config)
    start_app(app)
