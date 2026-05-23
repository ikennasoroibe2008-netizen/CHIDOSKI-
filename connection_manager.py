from typing import List, Dict
import asyncio
from fastapi import WebSocket

class ConnectionManager:
    """Manage WebSocket connections for real-time messaging and games."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_conversations: Dict[str, List[str]] = {}  # user_id -> [conversation_ids]
        self.conversation_users: Dict[str, List[str]] = {}  # conversation_id -> [user_ids]
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Connect a user."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []
    
    def disconnect(self, user_id: str):
        """Disconnect a user."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
    
    async def broadcast_to_conversation(self, message: str, conversation_id: str):
        """Broadcast a message to all users in a conversation."""
        if conversation_id in self.conversation_users:
            for user_id in self.conversation_users[conversation_id]:
                if user_id in self.active_connections:
                    try:
                        await self.active_connections[user_id].send_text(message)
                    except Exception as e:
                        print(f"Error sending to {user_id}: {e}")
    
    async def broadcast_to_game(self, message: str, game_id: str):
        """Broadcast a message to all players in a game."""
        await self.broadcast_to_conversation(message, f"game_{game_id}")
    
    def join_conversation(self, user_id: str, conversation_id: str):
        """Add user to conversation."""
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []
        if conversation_id not in self.user_conversations[user_id]:
            self.user_conversations[user_id].append(conversation_id)
        
        if conversation_id not in self.conversation_users:
            self.conversation_users[conversation_id] = []
        if user_id not in self.conversation_users[conversation_id]:
            self.conversation_users[conversation_id].append(user_id)
    
    def leave_conversation(self, user_id: str, conversation_id: str):
        """Remove user from conversation."""
        if user_id in self.user_conversations and conversation_id in self.user_conversations[user_id]:
            self.user_conversations[user_id].remove(conversation_id)
        
        if conversation_id in self.conversation_users and user_id in self.conversation_users[conversation_id]:
            self.conversation_users[conversation_id].remove(user_id)

manager = ConnectionManager()
