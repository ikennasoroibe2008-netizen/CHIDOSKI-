import os
from dotenv import load_dotenv

load_dotenv()

# Environment
DEBUG = os.getenv("DEBUG", "True") == "True"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chidoski.db")

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
API_BASE_URL = os.getenv("API_BASE_URL", f"http://{API_HOST}:{API_PORT}")

# WebRTC Signaling Server
WEBRTC_HOST = os.getenv("WEBRTC_HOST", "127.0.0.1")
WEBRTC_PORT = int(os.getenv("WEBRTC_PORT", 8001))
WEBRTC_URL = os.getenv("WEBRTC_URL", f"ws://{WEBRTC_HOST}:{WEBRTC_PORT}")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS
CORS_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    os.getenv("FRONTEND_URL", "http://localhost:8000"),
]

# Game Configuration
MAX_PLAYERS_PER_GAME = 2
GAME_TIMEOUT = 300  # 5 minutes
GAME_TYPES = ["chess", "cards", "dice"]

# Video Call Configuration
VIDEO_CALL_TIMEOUT = 1800  # 30 minutes
ICE_SERVERS = [
    {"urls": ["stun:stun.l.google.com:19302"]},
    {"urls": ["stun:stun1.l.google.com:19302"]},
]
