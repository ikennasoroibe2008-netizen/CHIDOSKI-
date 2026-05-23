# CHIDOSKI - Mobile Chat Application

A comprehensive mobile chat application with video calling, multiplayer games, and real-time messaging built with Kivy and FastAPI.

## Features

### 🔐 Authentication
- User registration and login
- JWT-based authentication
- Secure password hashing with PBKDF2

### 💬 Real-time Messaging
- One-on-one and group conversations
- WebSocket support for instant message delivery
- Message history
- Read status tracking

### 📹 Video Calling
- Peer-to-peer video calling using WebRTC
- Real-time signaling
- Call history and duration tracking
- ICE candidate handling

### 🎮 Multiplayer Games
- Chess
- Cards
- Dice
- Real-time game state synchronization
- Winner tracking
- Game history

### 👥 Friends System
- Add friends
- Friend requests (pending/accepted/blocked)
- Online/offline status
- User profiles

## Architecture

### Backend
- **FastAPI**: High-performance web framework
- **SQLAlchemy**: ORM for database management
- **WebSocket**: Real-time messaging
- **WebRTC**: Peer-to-peer video calling
- **SQLite**: Local database

### Frontend
- **Kivy**: Cross-platform mobile framework
- **REST API Client**: HTTP communication
- **WebSocket Client**: Real-time updates

## Installation

### Prerequisites
- Python 3.8+
- pip

### Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "DEBUG=True" > .env
echo "ENVIRONMENT=development" >> .env
echo "DATABASE_URL=sqlite:///./chidoski.db" >> .env
echo "API_HOST=127.0.0.1" >> .env
echo "API_PORT=8000" >> .env
echo "WEBRTC_HOST=127.0.0.1" >> .env
echo "WEBRTC_PORT=8001" >> .env
```

### Running the Application

#### 1. Start FastAPI Backend Server

```bash
python main.py
```

The API will be available at `http://127.0.0.1:8000`

#### 2. Start WebRTC Signaling Server

```bash
python webrtc_server.py
```

The WebRTC server will be available at `ws://127.0.0.1:8001`

#### 3. Run Mobile App

```bash
python app.py
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /users/me` - Get current user
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/me` - Update user profile

### Conversations
- `POST /conversations` - Create conversation
- `GET /conversations` - Get all conversations
- `GET /conversations/{id}/messages` - Get messages
- `POST /conversations/{id}/messages` - Send message

### Friends
- `POST /friends/add/{friend_id}` - Send friend request
- `POST /friends/accept/{friendship_id}` - Accept friend request
- `GET /friends` - Get friends list

### Video Calls
- `POST /video-calls/start` - Start video call
- `POST /video-calls/{id}/answer` - Answer call
- `POST /video-calls/{id}/end` - End call

### Games
- `POST /games/create` - Create game session
- `POST /games/{id}/move` - Make game move
- `POST /games/{id}/finish` - Finish game
- `GET /games/user` - Get user's games

## WebSocket Endpoints

- `ws://127.0.0.1:8000/ws/chat/{conversation_id}` - Real-time chat
- `ws://127.0.0.1:8001/` - WebRTC signaling

## Project Structure

```
CHIDOSKI-/
├── main.py              # FastAPI application
├── webrtc_server.py     # WebRTC signaling server
├── app.py               # Kivy mobile application
├── models.py            # Database models
├── database.py          # Database configuration
├── auth.py              # Authentication utilities
├── connection_manager.py # WebSocket connection management
├── config.py            # Configuration
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

## Configuration

Edit `config.py` to customize:
- Database URL
- API host and port
- WebRTC settings
- CORS origins
- Game configuration
- Video call settings

## Deployment

### Cloud Deployment

1. Update `config.py` with your cloud server URLs
2. Set environment variables on cloud platform
3. Use a production database (PostgreSQL recommended)
4. Deploy FastAPI app using Gunicorn/Uvicorn
5. Deploy WebRTC server separately
6. Build mobile app for iOS/Android

### Example with Docker

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Development

### Database Migrations

The database is automatically initialized on app startup. To reset:

```bash
rm chidoski.db
python -c "from database import init_db; init_db()"
```

### Testing

```bash
# Test API endpoints
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","full_name":"Test User","password":"password123"}'
```

## Security Considerations

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Implement rate limiting
- Add CORS properly for production
- Use strong passwords
- Implement message encryption
- Add user input validation

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Roadmap

- [ ] End-to-end encryption
- [ ] Voice calls
- [ ] File sharing
- [ ] Message reactions
- [ ] User search
- [ ] Typing indicators
- [ ] Message editing/deletion
- [ ] User stories/status
- [ ] Group video calls
- [ ] AI chat bot integration
