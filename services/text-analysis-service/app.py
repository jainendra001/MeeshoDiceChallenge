from flask import Flask, request, jsonify
from transformers import pipeline
import numpy as np

app = Flask(__name__)

# Load a pre-trained sentiment analysis model as a placeholder for text classification
# In a real application, you would fine-tune a model like DistilBERT for specific tasks
# like detecting spammy text, superlatives, or misleading claims.
try:
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    print(f"Could not load sentiment-analysis pipeline: {e}")
    print("Proceeding with a dummy classifier for demonstration.")
    classifier = None

@app.route('/api/v1/text/analyze', methods=['POST'])
def analyze_text():
    if 'title' not in request.json or 'description' not in request.json:
        return jsonify({"error": "title and description are required"}), 400

    title = request.json['title']
    description = request.json['description']
    
    print(f"Analyzing text - Title: '{title}', Description: '{description}'")

    # Mock analysis results
    clarity_score = np.random.uniform(0.0, 1.0)
    flagged_phrases = []

    # Simulate text analysis using the loaded model or dummy logic
    if classifier:
        text_to_analyze = title + " " + description
        try:
            # Dummy classification for demonstration
            # In a real app, you'd have specific labels for spam, misleading, etc.
            results = classifier(text_to_analyze)
            if results and results[0]['label'] == 'NEGATIVE' and results[0]['score'] > 0.7:
                flagged_phrases.append("Potentially negative sentiment detected")
            
            # Simulate detection of specific keywords/phrases
            if "100% original" in description.lower():
                flagged_phrases.append("'100% original' claim detected")
            if "best quality guaranteed" in description.lower():
                flagged_phrases.append("'best quality guaranteed' claim detected")

        except Exception as e:
            print(f"Error during dummy model prediction: {e}")
            flagged_phrases.append("Error during text analysis simulation")
    else:
        # Fallback dummy logic if model failed to load
        if "100% original" in description.lower():
            flagged_phrases.append("'100% original' claim detected (dummy)")
        if "best quality guaranteed" in description.lower():
            flagged_phrases.append("'best quality guaranteed' claim detected (dummy)")
        clarity_score = np.random.uniform(0.3, 0.7) # Slightly lower score for dummy

    return jsonify({
        "clarity_score": float(clarity_score),
        "flagged_phrases": flagged_phrases
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
