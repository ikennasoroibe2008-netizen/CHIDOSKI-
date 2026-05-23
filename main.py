from fastapi import FastAPI, Depends, HTTPException, WebSocket, status
from fastapi.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
import json

from config import CORS_ORIGINS, API_HOST, API_PORT, DEBUG
from database import get_db, init_db
from models import User, Conversation, Message, Friendship, VideoCall, GameSession, ConversationParticipant, FriendshipStatus
from auth import hash_password, verify_password, create_access_token, decode_access_token
from connection_manager import manager

# Initialize app
app = FastAPI(title="CHIDOSKI API", version="1.0.0", debug=DEBUG)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# ======================== Pydantic Models ========================

class UserRegister(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    is_online: bool
    last_seen: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class MessageCreate(BaseModel):
    content: str
    media_url: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    content: str
    sender_id: str
    created_at: datetime
    is_read: bool

class ConversationCreate(BaseModel):
    name: Optional[str]
    is_group: bool
    participant_ids: List[str]

class ConversationResponse(BaseModel):
    id: str
    name: Optional[str]
    is_group: bool
    created_at: datetime
    messages: List[MessageResponse] = []

class FriendshipResponse(BaseModel):
    id: str
    friend_id: str
    username: str
    status: str
    created_at: datetime

class VideoCallStart(BaseModel):
    receiver_id: str

class GameSessionCreate(BaseModel):
    game_type: str  # chess, cards, dice
    opponent_id: Optional[str] = None

# ======================== Helper Functions ========================

def get_current_user(token: Optional[str] = None, db: Session = Depends(get_db)) -> User:
    """Get current authenticated user."""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

# ======================== Authentication Endpoints ========================

@app.post("/auth/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user.__dict__)
    )

@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user."""
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user.__dict__)
    )

# ======================== User Endpoints ========================

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(token: Optional[str] = None, db: Session = Depends(get_db)):
    """Get current user info."""
    user = get_current_user(token, db)
    return UserResponse(**user.__dict__)

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user.__dict__)

@app.put("/users/me")
def update_user(bio: Optional[str] = None, avatar_url: Optional[str] = None, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Update user profile."""
    user = get_current_user(token, db)
    if bio is not None:
        user.bio = bio
    if avatar_url is not None:
        user.avatar_url = avatar_url
    db.commit()
    return {"message": "Profile updated"}

# ======================== Conversation Endpoints ========================

@app.post("/conversations", response_model=ConversationResponse)
def create_conversation(conv_data: ConversationCreate, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Create a new conversation."""
    user = get_current_user(token, db)
    
    conversation = Conversation(
        id=str(uuid.uuid4()),
        name=conv_data.name,
        is_group=conv_data.is_group,
        creator_id=user.id
    )
    
    db.add(conversation)
    db.flush()
    
    # Add participants
    for participant_id in conv_data.participant_ids:
        participant = ConversationParticipant(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            user_id=participant_id
        )
        db.add(participant)
    
    # Add creator
    creator_participant = ConversationParticipant(
        id=str(uuid.uuid4()),
        conversation_id=conversation.id,
        user_id=user.id
    )
    db.add(creator_participant)
    
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse(**conversation.__dict__)

@app.get("/conversations")
def get_conversations(token: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all conversations for current user."""
    user = get_current_user(token, db)
    
    participants = db.query(ConversationParticipant).filter(ConversationParticipant.user_id == user.id).all()
    conversation_ids = [p.conversation_id for p in participants]
    
    conversations = db.query(Conversation).filter(Conversation.id.in_(conversation_ids)).all()
    return [{"id": c.id, "name": c.name, "is_group": c.is_group, "created_at": c.created_at} for c in conversations]

@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Get messages in a conversation."""
    user = get_current_user(token, db)
    
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    return [{"id": m.id, "content": m.content, "sender_id": m.sender_id, "created_at": m.created_at, "is_read": m.is_read} for m in messages]

@app.post("/conversations/{conversation_id}/messages")
def send_message(conversation_id: str, msg_data: MessageCreate, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Send a message to a conversation."""
    user = get_current_user(token, db)
    
    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        sender_id=user.id,
        content=msg_data.content,
        media_url=msg_data.media_url
    )
    
    db.add(message)
    db.commit()
    
    return {"id": message.id, "content": message.content, "created_at": message.created_at}

# ======================== Friends Endpoints ========================

@app.post("/friends/add/{friend_id}")
def add_friend(friend_id: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Send friend request."""
    user = get_current_user(token, db)
    
    if user.id == friend_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself")
    
    existing = db.query(Friendship).filter(
        (Friendship.user_id == user.id) & (Friendship.friend_id == friend_id)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Request already sent")
    
    friendship = Friendship(
        id=str(uuid.uuid4()),
        user_id=user.id,
        friend_id=friend_id,
        status=FriendshipStatus.PENDING
    )
    
    db.add(friendship)
    db.commit()
    
    return {"message": "Friend request sent"}

@app.post("/friends/accept/{friendship_id}")
def accept_friend_request(friendship_id: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Accept friend request."""
    user = get_current_user(token, db)
    
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
    
    friendship.status = FriendshipStatus.ACCEPTED
    db.commit()
    
    return {"message": "Friend request accepted"}

@app.get("/friends")
def get_friends(token: Optional[str] = None, db: Session = Depends(get_db)):
    """Get user's friends."""
    user = get_current_user(token, db)
    
    friendships = db.query(Friendship).filter(
        (Friendship.user_id == user.id) & (Friendship.status == FriendshipStatus.ACCEPTED)
    ).all()
    
    return [{"id": f.id, "friend_id": f.friend_id, "status": f.status.value, "created_at": f.created_at} for f in friendships]

# ======================== Video Call Endpoints ========================

@app.post("/video-calls/start")
def start_video_call(call_data: VideoCallStart, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Initiate a video call."""
    user = get_current_user(token, db)
    
    video_call = VideoCall(
        id=str(uuid.uuid4()),
        caller_id=user.id,
        receiver_id=call_data.receiver_id,
        status="initiated"
    )
    
    db.add(video_call)
    db.commit()
    
    return {"call_id": video_call.id, "status": video_call.status}

@app.post("/video-calls/{call_id}/answer")
def answer_video_call(call_id: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Answer a video call."""
    user = get_current_user(token, db)
    
    call = db.query(VideoCall).filter(VideoCall.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call.status = "connected"
    call.started_at = datetime.utcnow()
    db.commit()
    
    return {"call_id": call.id, "status": call.status}

@app.post("/video-calls/{call_id}/end")
def end_video_call(call_id: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    """End a video call."""
    user = get_current_user(token, db)
    
    call = db.query(VideoCall).filter(VideoCall.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call.status = "ended"
    call.ended_at = datetime.utcnow()
    if call.started_at:
        call.duration = int((call.ended_at - call.started_at).total_seconds())
    db.commit()
    
    return {"call_id": call.id, "status": call.status, "duration": call.duration}

# ======================== Game Endpoints ========================

@app.post("/games/create")
def create_game_session(game_data: GameSessionCreate, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Create a new game session."""
    user = get_current_user(token, db)
    
    game = GameSession(
        id=str(uuid.uuid4()),
        creator_id=user.id,
        opponent_id=game_data.opponent_id,
        game_type=game_data.game_type,
        status="waiting" if game_data.opponent_id is None else "playing"
    )
    
    db.add(game)
    db.commit()
    
    return {"game_id": game.id, "status": game.status, "game_type": game.game_type}

@app.post("/games/{game_id}/move")
def make_game_move(game_id: str, move_data: dict, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Make a move in a game."""
    user = get_current_user(token, db)
    
    game = db.query(GameSession).filter(GameSession.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Update game state
    game.game_state = json.dumps(move_data)
    db.commit()
    
    return {"game_id": game.id, "status": game.status}

@app.post("/games/{game_id}/finish")
def finish_game(game_id: str, winner_id: Optional[str] = None, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Finish a game session."""
    user = get_current_user(token, db)
    
    game = db.query(GameSession).filter(GameSession.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game.status = "finished"
    game.winner_id = winner_id
    game.ended_at = datetime.utcnow()
    db.commit()
    
    return {"game_id": game.id, "status": game.status, "winner_id": game.winner_id}

@app.get("/games/user")
def get_user_games(token: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all games for current user."""
    user = get_current_user(token, db)
    
    games = db.query(GameSession).filter(
        (GameSession.creator_id == user.id) | (GameSession.opponent_id == user.id)
    ).all()
    
    return [{"id": g.id, "game_type": g.game_type, "status": g.status, "winner_id": g.winner_id} for g in games]

# ======================== WebSocket Endpoints ========================

@app.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(conversation_id: str, websocket: WebSocket, token: Optional[str] = None):
    """WebSocket endpoint for real-time chat."""
    # Note: Token should be passed in query params
    await manager.connect(conversation_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_to_conversation(data, conversation_id)
    except Exception as e:
        manager.disconnect(conversation_id)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
