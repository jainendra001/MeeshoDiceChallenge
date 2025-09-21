from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from typing import Dict

from .chat_interface.models import ChatSession, Message, ChatResponse
from .llm.rag_service import RAGService

app = FastAPI(title="Meesho Guide AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = RAGService()

# Store active chat sessions
chat_sessions: Dict[str, ChatSession] = {}

@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    # Create or get session
    session_id = str(uuid.uuid4())
    chat_session = ChatSession(
        session_id=session_id,
        user_id=user_id,
        messages=[]
    )
    chat_sessions[session_id] = chat_session
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Add user message to chat history
            user_message = Message(role="user", content=message_data["message"])
            chat_session.messages.append(user_message)
            
            # Generate response using RAG
            response: ChatResponse = rag_service.generate_response(chat_session)
            
            # Add assistant message to chat history
            assistant_message = Message(role="assistant", content=response.response)
            chat_session.messages.append(assistant_message)
            
            # Send response back to client
            await websocket.send_json({
                "response": response.response,
                "suggested_products": response.suggested_products
            })
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up session when connection closes
        if session_id in chat_sessions:
            del chat_sessions[session_id]
