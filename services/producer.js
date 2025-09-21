const { Kafka } = require('kafkajs');

const KAFKA_BROKER = process.env.KAFKA_BROKER || 'localhost:9092';

const kafka = new Kafka({
    clientId: 'product-catalog-service', // Simulating Product Catalog Service
    brokers: [KAFKA_BROKER]
});

const producer = kafka.producer();

const run = async () => {
    await producer.connect();
    console.log("Kafka Producer connected.");

    const sendListingCreatedEvent = async (productId, imageUrl, title, description) => {
        const event = {
            productId,
            imageUrl,
            title,
            description,
            timestamp: new Date().toISOString()
        };

        try {
            await producer.send({
                topic: 'listing_created',
                messages: [
                    { value: JSON.stringify(event) },
                ],
            });
            console.log(`Sent listing_created event for productId: ${productId}`);
        } catch (error) {
            console.error(`Error sending listing_created event for productId ${productId}:`, error.message);
        }
    };

    // Simulate a new product listing
    await sendListingCreatedEvent(
        'product-123',
        'http://example.com/images/product-123.jpg',
        'Amazing New T-Shirt',
        'This is an amazing new t-shirt made from 100% original cotton. Best quality guaranteed!'
    );

    await sendListingCreatedEvent(
        'product-456',
        'http://example.com/images/blurry-product-456.jpg',
        'Blurry Old Jeans',
        'These are old jeans, not very good quality.'
    );

    await sendListingCreatedEvent(
        'product-789',
        'http://example.com/images/stock-photo-789.jpg',
        'Generic Item',
        'A generic item with no special features.'
    );

    await producer.disconnect();
    console.log("Kafka Producer disconnected.");
};

run().catch(console.error);
