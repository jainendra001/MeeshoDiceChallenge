const express = require('express');
const { Kafka } = require('kafkajs');
const axios = require('axios');

const app = express();
app.use(express.json());

const KAFKA_BROKER = process.env.KAFKA_BROKER || 'localhost:9092';
const IMAGE_ANALYSIS_SERVICE_URL = process.env.IMAGE_ANALYSIS_SERVICE_URL || 'http://localhost:5001/api/v1/image/analyze';
const TEXT_ANALYSIS_SERVICE_URL = process.env.TEXT_ANALYSIS_SERVICE_URL || 'http://localhost:5002/api/v1/text/analyze';
const PRODUCT_CATALOG_API_URL = process.env.PRODUCT_CATALOG_API_URL || 'http://localhost:3000/api/v1/products'; // Mock API

const kafka = new Kafka({
    clientId: 'listing-quality-service',
    brokers: [KAFKA_BROKER]
});

const consumer = kafka.consumer({ groupId: 'listing-quality-group' });

// Mock Product Catalog Database (in-memory for demonstration)
const productCatalog = {};

// Mock Product Catalog API
app.put('/api/v1/products/:productId/quality', (req, res) => {
    const { productId } = req.params;
    const { quality_score, quality_status } = req.body;

    if (!productCatalog[productId]) {
        productCatalog[productId] = {};
    }
    productCatalog[productId].quality_score = quality_score;
    productCatalog[productId].quality_status = quality_status;
    console.log(`Product ${productId} updated:`, productCatalog[productId]);
    res.status(200).json({ message: "Product quality updated successfully", productId, quality_score, quality_status });
});

app.get('/api/v1/products/:productId', (req, res) => {
    const { productId } = req.params;
    if (productCatalog[productId]) {
        res.status(200).json(productCatalog[productId]);
    } else {
        res.status(404).json({ message: "Product not found" });
    }
});


const run = async () => {
    await consumer.connect();
    await consumer.subscribe({ topic: 'listing_created', fromBeginning: true });

    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            console.log({
                value: message.value.toString(),
            });

            const event = JSON.parse(message.value.toString());
            const { productId, imageUrl, title, description } = event;

            console.log(`Processing listing_created event for productId: ${productId}`);

            let imageAnalysisResult = { blurriness_score: 0, is_stock_photo: 0 };
            let textAnalysisResult = { clarity_score: 0, flagged_phrases: [] };

            try {
                const imageResponse = await axios.post(IMAGE_ANALYSIS_SERVICE_URL, { image_url: imageUrl });
                imageAnalysisResult = imageResponse.data;
                console.log(`Image Analysis Result for ${productId}:`, imageAnalysisResult);
            } catch (error) {
                console.error(`Error calling Image Analysis Service for ${productId}:`, error.message);
            }

            try {
                const textResponse = await axios.post(TEXT_ANALYSIS_SERVICE_URL, { title, description });
                textAnalysisResult = textResponse.data;
                console.log(`Text Analysis Result for ${productId}:`, textAnalysisResult);
            } catch (error) {
                console.error(`Error calling Text Analysis Service for ${productId}:`, error.message);
            }

            // Calculate Quality Score
            // This is a simplified weighting. In a real system, weights would be tuned.
            const blurrinessPenalty = imageAnalysisResult.blurriness_score * 0.4; // Higher score means more blurry
            const stockPhotoPenalty = imageAnalysisResult.is_stock_photo * 0.3; // Higher score means more likely stock
            const textClarityBonus = textAnalysisResult.clarity_score * 0.3; // Higher score means more clear

            let quality_score = (1 - blurrinessPenalty - stockPhotoPenalty + textClarityBonus) / 1.6; // Normalize to 0-1
            quality_score = Math.max(0, Math.min(1, quality_score)); // Ensure score is between 0 and 1

            let quality_status = 'APPROVED';
            if (blurrinessPenalty > 0.6 || stockPhotoPenalty > 0.7 || textAnalysisResult.flagged_phrases.length > 0) {
                quality_status = 'PENDING_REVIEW';
            }
            if (quality_score < 0.4) { // Example threshold
                quality_status = 'REJECTED';
            } else if (quality_score < 0.7 && quality_status !== 'REJECTED') {
                quality_status = 'NEEDS_IMPROVEMENT';
            }

            console.log(`Final Quality Score for ${productId}: ${quality_score}, Status: ${quality_status}`);

            // Update Product Catalog Database (mock API call)
            try {
                await axios.put(`${PRODUCT_CATALOG_API_URL}/${productId}/quality`, {
                    quality_score: quality_score,
                    quality_status: quality_status
                });
                console.log(`Product Catalog updated for ${productId}`);
            } catch (error) {
                console.error(`Error updating Product Catalog for ${productId}:`, error.message);
            }
        },
    });
};

run().catch(console.error);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Listing Quality Service (Mock Product Catalog API) running on port ${PORT}`);
});
