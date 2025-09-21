# Meesho Guide AI - Conversational Shopping Assistant

A conversational AI assistant that helps users find products, answer questions, and provide personalized shopping recommendations.

## Architecture

### High-Level Design (HLD)

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│  Web/Mobile │     │ FastAPI Server │     │  Vector DB   │
│  Interface  │<--->│  WebSocket    │<--->│  (Pinecone)  │
└─────────────┘     └───────────────┘     └──────────────┘
                           ↕                      ↕
                    ┌───────────────┐     ┌──────────────┐
                    │   RAG Engine  │<--->│    LLM API   │
                    └───────────────┘     └──────────────┘
```

#### Components

1. **Chat Interface**

   - WebSocket-based real-time communication
   - Responsive web interface
   - Product suggestion sidebar

2. **FastAPI Server**

   - WebSocket endpoint for real-time chat
   - Session management
   - Request handling and routing

3. **RAG (Retrieval-Augmented Generation) Engine**

   - Query understanding
   - Context retrieval from Vector DB
   - Response generation with LLM

4. **Vector Database (Pinecone)**
   - Stores product embeddings
   - Enables semantic search
   - Fast similarity matching

### Low-Level Design (LLD)

#### Technology Stack

- Backend: Python with FastAPI
- Embeddings: Sentence-Transformers (all-MiniLM-L6-v2)
- Vector DB: Pinecone
- LLM: ChatOpenAI
- Frontend: HTML/CSS/JS with WebSocket

#### Data Flow

1. **Data Ingestion**

   ```
   Product Data → Text Chunking → Embedding Generation → Vector DB Storage
   ```

2. **Query Processing**

   ```
   User Query → Query Embedding → Vector Search → Context Retrieval → LLM Response
   ```

3. **Response Generation**
   ```
   Context + Query + History → Prompt Construction → LLM → Structured Response
   ```

## Setup and Installation

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. Run data ingestion:

   ```bash
   python -m src.data_ingestion.ingest
   ```

5. Start the server:

   ```bash
   uvicorn src.api.main:app --reload
   ```

6. Open the chat interface:
   ```bash
   python -m http.server 5000 --directory src/chat_interface/static
   ```

## API Documentation

### WebSocket Endpoint

```
ws://localhost:8000/ws/chat/{user_id}
```

#### Message Format

```json
// Client to Server
{
    "message": "Find me blue floral sarees for a wedding"
}

// Server to Client
{
    "response": "I found some beautiful blue floral sarees...",
    "suggested_products": [
        {
            "name": "Product Name",
            "price": 999,
            "url": "/product/123"
        }
    ]
}
```

## Future Improvements

1. **Enhanced Context Understanding**

   - User preference learning
   - Shopping history integration
   - Category-specific handling

2. **Performance Optimization**

   - Caching frequent queries
   - Batch processing for embeddings
   - Response streaming

3. **Features**

   - Multi-language support
   - Voice interface
   - Image-based search
   - Personalized recommendations

4. **Security**
   - Authentication
   - Rate limiting
   - Input validation
   - Data encryption

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
