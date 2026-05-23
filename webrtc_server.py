import asyncio
import json
import websockets
from typing import Dict, Set
from config import WEBRTC_HOST, WEBRTC_PORT

class WebRTCSignalingServer:
    def __init__(self):
        self.peers: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.call_sessions: Dict[str, Dict] = {}  # call_id -> {caller_id, receiver_id, offer, answer}
    
    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection."""
        user_id = None
        try:
            # Wait for user identification
            msg = await websocket.recv()
            data = json.loads(msg)
            
            if data['type'] == 'register':
                user_id = data['user_id']
                self.peers[user_id] = websocket
                print(f"User {user_id} connected")
                
                # Send confirmation
                await websocket.send(json.dumps({'type': 'registered', 'user_id': user_id}))
                
                # Listen for messages
                async for message in websocket:
                    await self.handle_message(user_id, json.loads(message))
        
        except websockets.exceptions.ConnectionClosed:
            print(f"User {user_id} disconnected")
        finally:
            if user_id and user_id in self.peers:
                del self.peers[user_id]
    
    async def handle_message(self, user_id: str, data: dict):
        """Handle incoming messages."""
        msg_type = data.get('type')
        
        if msg_type == 'call':
            await self.handle_call(user_id, data)
        elif msg_type == 'offer':
            await self.handle_offer(user_id, data)
        elif msg_type == 'answer':
            await self.handle_answer(user_id, data)
        elif msg_type == 'ice_candidate':
            await self.handle_ice_candidate(user_id, data)
        elif msg_type == 'end_call':
            await self.handle_end_call(user_id, data)
    
    async def handle_call(self, caller_id: str, data: dict):
        """Handle call initiation."""
        receiver_id = data.get('receiver_id')
        call_id = data.get('call_id')
        
        if receiver_id not in self.peers:
            # Receiver not available
            await self.peers[caller_id].send(json.dumps({
                'type': 'call_failed',
                'reason': 'receiver_not_available'
            }))
            return
        
        # Store call session
        self.call_sessions[call_id] = {
            'caller_id': caller_id,
            'receiver_id': receiver_id,
            'status': 'ringing'
        }
        
        # Send ringing to receiver
        await self.peers[receiver_id].send(json.dumps({
            'type': 'incoming_call',
            'call_id': call_id,
            'caller_id': caller_id
        }))
    
    async def handle_offer(self, user_id: str, data: dict):
        """Handle WebRTC offer."""
        call_id = data.get('call_id')
        offer = data.get('offer')
        
        if call_id not in self.call_sessions:
            return
        
        call_session = self.call_sessions[call_id]
        receiver_id = call_session['receiver_id']
        
        # Forward offer to receiver
        if receiver_id in self.peers:
            await self.peers[receiver_id].send(json.dumps({
                'type': 'offer',
                'call_id': call_id,
                'offer': offer
            }))
            call_session['offer'] = offer
            call_session['status'] = 'connecting'
    
    async def handle_answer(self, user_id: str, data: dict):
        """Handle WebRTC answer."""
        call_id = data.get('call_id')
        answer = data.get('answer')
        
        if call_id not in self.call_sessions:
            return
        
        call_session = self.call_sessions[call_id]
        caller_id = call_session['caller_id']
        
        # Forward answer to caller
        if caller_id in self.peers:
            await self.peers[caller_id].send(json.dumps({
                'type': 'answer',
                'call_id': call_id,
                'answer': answer
            }))
            call_session['answer'] = answer
            call_session['status'] = 'connected'
    
    async def handle_ice_candidate(self, user_id: str, data: dict):
        """Handle ICE candidate."""
        call_id = data.get('call_id')
        candidate = data.get('candidate')
        target_user_id = data.get('target_user_id')
        
        if target_user_id in self.peers:
            await self.peers[target_user_id].send(json.dumps({
                'type': 'ice_candidate',
                'call_id': call_id,
                'candidate': candidate
            }))
    
    async def handle_end_call(self, user_id: str, data: dict):
        """Handle call termination."""
        call_id = data.get('call_id')
        
        if call_id in self.call_sessions:
            call_session = self.call_sessions[call_id]
            other_user_id = call_session['caller_id'] if call_session['receiver_id'] == user_id else call_session['receiver_id']
            
            # Notify other user
            if other_user_id in self.peers:
                await self.peers[other_user_id].send(json.dumps({
                    'type': 'call_ended',
                    'call_id': call_id
                }))
            
            del self.call_sessions[call_id]

async def main():
    """Start WebRTC signaling server."""
    server = WebRTCSignalingServer()
    
    async with websockets.serve(server.handle_connection, WEBRTC_HOST, WEBRTC_PORT):
        print(f"WebRTC Signaling Server running on ws://{WEBRTC_HOST}:{WEBRTC_PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
