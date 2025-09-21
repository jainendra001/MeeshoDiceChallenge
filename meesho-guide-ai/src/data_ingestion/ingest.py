import json
from typing import List, Dict, Any
from ..vector_store.store import VectorStore

def load_sample_data() -> List[Dict[str, Any]]:
    """Load sample product data"""
    return [
        {
            "name": "Floral Print Saree",
            "description": "Beautiful blue floral print saree with blouse piece. Perfect for weddings and festivals.",
            "price": 999,
            "url": "/products/floral-print-saree",
            "category": "Sarees",
            "tags": ["wedding", "floral", "blue", "festival"]
        },
        {
            "name": "Men's Cotton Kurta",
            "description": "Comfortable cotton kurta for men in white color. Ideal for casual and festive wear.",
            "price": 599,
            "url": "/products/mens-cotton-kurta",
            "category": "Mens",
            "tags": ["casual", "cotton", "white", "kurta"]
        }
    ]

def ingest_data():
    """Ingest sample data into vector store"""
    data = load_sample_data()
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Prepare texts and metadata
    texts = [
        f"{product['name']}\n{product['description']}\n{' '.join(product['tags'])}"
        for product in data
    ]
    metadata = data
    
    # Add to vector store
    vector_store.add_texts(texts, metadata)

if __name__ == "__main__":
    ingest_data()
