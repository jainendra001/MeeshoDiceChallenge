from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from typing import List, Dict, Any

from ..vector_store.store import VectorStore
from ..chat_interface.models import ChatSession, ChatResponse

class RAGService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.template = """You are Meesho Guide, a helpful shopping assistant.
        Answer the question based on the context provided and your knowledge about e-commerce and fashion.
        If you don't know the answer, just say that you don't know. Don't try to make up an answer.
        
        Context: {context}
        
        Chat History: {chat_history}
        
        Question: {question}
        
        Answer: Let me help you with that!"""
        
        self.prompt = ChatPromptTemplate.from_template(self.template)
        self.model = ChatOpenAI()
        self.chain = (
            {"context": self.retrieve, 
             "question": RunnablePassthrough(),
             "chat_history": self.get_chat_history}
            | self.prompt
            | self.model
            | StrOutputParser()
        )
        
    def retrieve(self, query: str) -> str:
        """Retrieve relevant documents from vector store"""
        results = self.vector_store.similarity_search(query)
        # Format the results into a string
        return "\n".join([f"Product: {r['metadata']['name']}\n"
                         f"Description: {r['metadata']['description']}\n"
                         f"Price: {r['metadata']['price']}\n"
                         for r in results])
    
    def get_chat_history(self, chat_session: ChatSession) -> str:
        """Format chat history for the prompt"""
        return "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in chat_session.messages[-5:]  # Only use last 5 messages
        ])
    
    def generate_response(self, chat_session: ChatSession) -> ChatResponse:
        """Generate a response using the RAG pipeline"""
        # Get the last user message
        user_query = chat_session.messages[-1].content
        
        # Get relevant context and generate response
        response = self.chain.invoke(user_query)
        
        # Get product recommendations
        relevant_products = self.vector_store.similarity_search(user_query, k=3)
        
        return ChatResponse(
            response=response,
            context=[r["metadata"] for r in relevant_products],
            suggested_products=[{
                "name": r["metadata"]["name"],
                "price": r["metadata"]["price"],
                "url": r["metadata"]["url"]
            } for r in relevant_products]
        )
