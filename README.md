# Proactive AI Quality & Authenticity Engine

This document outlines the design and implementation of the Proactive AI Quality & Authenticity Engine, a critical component for ensuring high-quality and authentic product listings on the Meesho platform.

## 1. Application Design Overview

This component addresses the need for upfront quality control by using AI to vet products before they are published. An automated AI/ML pipeline will analyze every new product listing. It will use computer vision to assess image quality (detecting blurry, stock, or scraped photos) and NLP to parse descriptions for misleading claims or keyword stuffing. Each listing will be assigned a "Quality Score." Listings below a certain threshold will be flagged for mandatory seller improvement or manual review, preventing low-quality products from ever reaching the customer.

## 2. High-Level Design (HLD)

The system employs an event-driven, microservices architecture to ensure scalability, responsiveness, and decoupling of concerns.

### Architecture Diagram (Conceptual)

```
+---------------------+      listing_created event      +-------------------------+
| Product Catalog     | ------------------------------> | Kafka Message Queue     |
| Service (Producer)  |                                 | (listing_created topic) |
+---------------------+      (Publishes Event)          +-------------------------+
                                                                    |
                                                                    | (Consumes Event)
                                                                    v
+-------------------------+                           +-------------------------+
| Listing Quality Service | <------------------------ | Image Analysis Service  |
| (Node.js Microservice)  | (API Call: POST /image/analyze) | (Python/TensorFlow/PyTorch) |
+-------------------------+                           +-------------------------+
      |       ^                                                   ^
      |       | (Aggregates Results)                              | (API Call: POST /text/analyze)
      |       |                                                   |
      |       +---------------------------------------------------+
      |                                                           |
      | (Updates Quality Score/Status)                            |
      v                                                           v
+-------------------------+                           +-------------------------+
| Product Catalog         |                           | Text Analysis Service   |
| Database (Augmented)    |                           | (Python/Transformers)   |
+-------------------------+                           +-------------------------+
```

### Key Components:

- **Product Catalog Service:** The existing Meesho service responsible for managing product listings. When a seller submits a new product, this service publishes a `listing_created` event to a Kafka message queue. This ensures a responsive seller experience by decoupling the quality check from the upload process.
- **Kafka Message Queue:** A distributed streaming platform (e.g., Apache Kafka) acts as the central nervous system for event communication. The `listing_created` topic holds events for new product submissions.
- **Listing Quality Service:** A dedicated microservice (implemented in Node.js and deployed on Kubernetes) that consumes `listing_created` events from Kafka. It orchestrates calls to specialized AI model services, aggregates their results, calculates a final "Quality Score," and updates the Product Catalog database.
- **Image Analysis Service:** A specialized, containerized AI model service (implemented in Python with TensorFlow/PyTorch, hosted on a scalable platform like AWS SageMaker). It receives image URLs and assesses image quality.
- **Text Analysis Service:** A specialized, containerized AI model service (implemented in Python with Hugging Face Transformers, hosted on a scalable platform like AWS SageMaker). It receives product titles and descriptions and analyzes text quality.
- **Product Catalog Database:** The existing Meesho database, augmented with new columns to store the `quality_score` and `quality_status` for each product.

### Data Flow:

1.  A seller submits a new product via the **Product Catalog Service**.
2.  The **Product Catalog Service** publishes a `listing_created` event to the **Kafka Message Queue**.
3.  The **Listing Quality Service** consumes this `listing_created` event.
4.  It then makes asynchronous API calls to the **Image Analysis Service** (with the image URL) and the **Text Analysis Service** (with the product title and description).
5.  The **Image Analysis Service** and **Text Analysis Service** perform their respective analyses and return results (e.g., blurriness score, flagged phrases).
6.  The **Listing Quality Service** aggregates these results, calculates a weighted "Quality Score," and determines a `quality_status`.
7.  Finally, the **Listing Quality Service** makes an API call back to the **Product Catalog Service** (or directly to the database API) to update the product's `quality_score` and `quality_status` in the **Product Catalog Database**.
8.  The core search and discovery algorithms on the Meesho platform will use this `quality_score` as a key ranking signal, heavily penalizing or completely hiding listings with a `REJECTED` status.

## 3. Low-Level Design (LLD)

### 3.1. Image Analysis Service

- **Technology Stack:** Python, TensorFlow/PyTorch, Flask/FastAPI.
- **Model:** Employs a pre-trained Convolutional Neural Network (CNN) like EfficientNet-B0, fine-tuned on an internal dataset of Meesho images labeled for quality attributes (e.g., blurry, stock_photo, watermarked).
- **API Endpoint:** `POST /api/v1/image/analyze`
  - **Request Body:**
    ```json
    {
      "image_url": "string"
    }
    ```
  - **Response Body:**
    ```json
    {
      "blurriness_score": float,   // Confidence score (0.0 - 1.0)
      "is_stock_photo": float      // Confidence score (0.0 - 1.0)
    }
    ```
- **Implementation Details:**
  - Receives `image_url` from the `Listing Quality Service`.
  - Downloads the image from the provided URL.
  - Preprocesses the image (resizing, normalization) to match the input requirements of the CNN model.
  - Performs inference using the fine-tuned EfficientNet-B0 model.
  - Returns a JSON object containing confidence scores for various image quality attributes.
- **Current Demo Implementation:** Uses a pre-trained EfficientNetB0 (if available) for dummy prediction, but generates random scores for `blurriness_score` and `is_stock_photo` to simulate output.

### 3.2. Text Analysis Service

- **Technology Stack:** Python, Hugging Face Transformers, Flask/FastAPI.
- **Model:** Uses a transformer-based model like DistilBERT, fine-tuned for sequence classification tasks to detect spammy text and flag superlative or potentially misleading claims (e.g., "100% original," "best quality guaranteed").
- **API Endpoint:** `POST /api/v1/text/analyze`
  - **Request Body:**
    ```json
    {
      "title": "string",
      "description": "string"
    }
    ```
  - **Response Body:**
    ```json
    {
      "clarity_score": float,      // Confidence score (0.0 - 1.0)
      "flagged_phrases": ["string"] // List of detected problematic phrases
    }
    ```
- **Implementation Details:**
  - Receives `title` and `description` from the `Listing Quality Service`.
  - Tokenizes and preprocesses the text for the transformer model.
  - Performs inference using the fine-tuned DistilBERT model to classify text quality and identify misleading claims.
  - Returns a JSON object with a clarity score and a list of flagged phrases.
- **Current Demo Implementation:** Uses a pre-trained sentiment analysis DistilBERT model for dummy classification and includes hardcoded keyword checks to simulate flagging. Generates a random `clarity_score`.

### 3.3. Listing Quality Service

- **Technology Stack:** Node.js, Express.js, `kafkajs`, `axios`.
- **Core Responsibilities:**
  - **Kafka Consumer:** Connects to the Kafka broker and subscribes to the `listing_created` topic.
  - **Event Processing:** On receiving a `listing_created` event, it extracts `productId`, `imageUrl`, `title`, and `description`.
  - **Orchestration:** Makes asynchronous HTTP POST requests to the `Image Analysis Service` and `Text Analysis Service`.
  - **Quality Score Calculation:** Aggregates the results from both AI services. A weighted formula is applied to calculate the final `quality_score`.
    - `blurriness_penalty = imageAnalysisResult.blurriness_score * 0.4`
    - `stock_photo_penalty = imageAnalysisResult.is_stock_photo * 0.3`
    - `text_clarity_bonus = textAnalysisResult.clarity_score * 0.3`
    - `quality_score = (1 - blurriness_penalty - stock_photo_penalty + text_clarity_bonus) / 1.6` (Normalized to 0-1)
  - **Status Assignment:** Assigns a `quality_status` based on the calculated `quality_score` and `flagged_phrases`.
    - `REJECTED`: If `quality_score < 0.4` (example threshold) or severe issues detected.
    - `PENDING_REVIEW`: If `blurriness_penalty > 0.6` or `stock_photo_penalty > 0.7` or `flagged_phrases` are present.
    - `NEEDS_IMPROVEMENT`: If `quality_score < 0.7` (example threshold) and not `REJECTED`.
    - `APPROVED`: Otherwise.
  - **Product Catalog Update:** Makes an HTTP PUT request to the Product Catalog Service's API to update the product's `quality_score` and `quality_status`.
- **Environment Variables:** Configured to use environment variables for Kafka broker address and AI service URLs, with `localhost` fallbacks for development.
  - `KAFKA_BROKER`
  - `IMAGE_ANALYSIS_SERVICE_URL`
  - `TEXT_ANALYSIS_SERVICE_URL`
  - `PRODUCT_CATALOG_API_URL`
- **Mock Product Catalog API:** For demonstration, this service also exposes a mock API (`PUT /api/v1/products/:productId/quality` and `GET /api/v1/products/:productId`) to simulate interaction with the actual Product Catalog Service and database.

### 3.4. Product Catalog Database Augmentation

The existing `Products` table in the Meesho database will be augmented with the following new columns:

- `quality_score`: `FLOAT` (Stores the calculated quality score, e.g., 0.0 to 1.0)
- `quality_status`: `ENUM('PENDING', 'APPROVED', 'REJECTED', 'NEEDS_IMPROVEMENT')` (Indicates the current quality status of the listing)

## 4. Integration with Meesho's Current Services

### 4.1. Product Catalog Service (Producer)

- **Integration Point:** The existing Product Catalog Service will be modified to publish a `listing_created` event to the Kafka topic whenever a new product is submitted or an existing product is significantly updated.
- **Event Structure:** The event payload will be a JSON object containing essential product details:
  ```json
  {
    "productId": "string",
    "imageUrl": "string",
    "title": "string",
    "description": "string",
    "timestamp": "ISO 8601 string"
  }
  ```
- **Current Demo Implementation:** The `services/producer.js` script simulates this behavior by connecting to Kafka and sending `listing_created` events with mock product data.

### 4.2. Search and Discovery Algorithms

- **Integration Point:** The core search and discovery algorithms within Meesho's platform will consume the `quality_score` and `quality_status` from the Product Catalog Database.
- **Usage:**
  - **Ranking Signal:** The `quality_score` will be used as a significant factor in product ranking, boosting high-quality listings and demoting lower-quality ones.
  - **Filtering/Hiding:** Listings with a `REJECTED` status will be heavily penalized or completely hidden from search results and recommendations to prevent customers from seeing low-quality products. `PENDING_REVIEW` or `NEEDS_IMPROVEMENT` listings might also have reduced visibility until their status is resolved.

## 5. Setup and Running the Services (Local Development)

This section guides you through setting up and running the Proactive AI Quality & Authenticity Engine locally.

### Prerequisites:

- Docker Desktop (for Kafka and ZooKeeper)
- Python 3.8+
- Node.js 18+
- `npm` (Node Package Manager)

### 5.1. Clone the Repository

```bash
git clone <your-repository-url>
cd Meesho Dice Challenge # Or your project root
```

### 5.2. Start Kafka and ZooKeeper (using Docker Compose)

Navigate to the `services` directory and start the Kafka cluster:

```bash
cd services
docker compose -f kafka-docker-compose.yml up -d
```

Wait for a minute or two for Kafka to fully initialize. You can check the status of your Docker containers with `docker ps`.

### 5.3. Setup and Run Image Analysis Service

```bash
cd services/image-analysis-service
python3 -m venv venv
source venv/bin/activate
pip install tensorflow flask Pillow
python3 app.py &
```

This will start the Image Analysis Service on `http://localhost:5001`.

### 5.4. Setup and Run Text Analysis Service

```bash
cd services/text-analysis-service
python3 -m venv venv
source venv/bin/activate
pip install transformers flask scikit-learn
python3 app.py &
```

This will start the Text Analysis Service on `http://localhost:5002`.

### 5.5. Setup and Run Listing Quality Service

```bash
cd services/listing-quality-service
npm init -y
npm install express kafkajs axios
node index.js &
```

This will start the Listing Quality Service (and its mock Product Catalog API) on `http://localhost:3000`.

### 5.6. Run the Kafka Producer (Simulate Product Listings)

From the project root directory, run the producer script:

```bash
node services/producer.js
```

This will send three `listing_created` events to Kafka. You should see logs in the terminals where the Image Analysis, Text Analysis, and Listing Quality Services are running, indicating event processing.

### 5.7. Verify Results

Query the mock Product Catalog API to see the updated quality scores and statuses:

```bash
curl http://localhost:3000/api/v1/products/product-123
curl http://localhost:3000/api/v1/products/product-456
curl http://localhost:3000/api/v1/products/product-789
```

Expected output will show `quality_score` and `quality_status` for each product.

## 6. Future Enhancements

- **Real Model Training:** Fine-tune AI models on actual Meesho datasets for accurate quality and authenticity detection.
- **Scalable Deployment:** Deploy AI services on platforms like AWS SageMaker or Kubernetes with GPU support for inference.
- **Robust Error Handling:** Implement more comprehensive error handling, retry mechanisms, and dead-letter queues for Kafka events.
- **Observability:** Add logging, monitoring, and alerting for all services.
- **Configuration Management:** Externalize configuration for different environments.
- **Authentication/Authorization:** Secure API endpoints between services.
- **Database Integration:** Replace mock Product Catalog API with actual database interactions.
- **Admin Interface:** Develop an interface for manual review of flagged listings.
