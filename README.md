# Meesho Dice Challenge - Service Overview

This repository contains prototypes and design documentation for four key services developed as part of the Meesho Dice Challenge. Each service is designed to enhance different aspects of the Meesho platform, from user experience to backend efficiency and quality control.

## Services and Their GitHub Branches

Each service is developed and maintained on its dedicated feature branch within this repository.

---

### 1. Gift Bundling Module

**Branch:** `giftAndBundling`

This module implements an "Enhanced Gifting & Bundling Module" to provide customers with personalized gifting options and sellers with tools to create product bundles (hampers).

**Key Features:**
-   **Gifting:** Allows customers to add personalized messages and gift wrapping at checkout.
-   **Seller-Centric Bundling ("Build a Hamper"):** Enables customers to create virtual hampers from a single seller's products, with potential bundle discounts and atomic inventory checks.

---

### 2. Meesho Guide AI

**Branch:** `meesho-guide-ai`

This service provides an AI-powered guide for Meesho users, leveraging Retrieval-Augmented Generation (RAG) to offer intelligent responses and product suggestions.

**Key Features:**
-   **Interactive Chat Interface:** Users can interact with an AI assistant via a WebSocket connection.
-   **RAG Service:** Generates responses by retrieving relevant information and using a Large Language Model (LLM).
-   **Product Suggestions:** Provides suggested products based on user queries.

---

### 3. Proactive AI Quality & Authenticity Engine

**Branch:** `feature/ProactiveAiQuality`

This engine ensures high-quality and authentic product listings by using AI to vet products before they are published. It employs an event-driven, microservices architecture.

**Key Features:**
-   **Image Analysis Service:** Uses computer vision to assess image quality (e.g., blurriness, stock photos).
-   **Text Analysis Service:** Uses NLP to parse descriptions for misleading claims or keyword stuffing.
-   **Listing Quality Service:** Orchestrates AI services, calculates a "Quality Score," and assigns a `quality_status` to each listing.
-   **Kafka Integration:** Utilizes Kafka for asynchronous event communication (`listing_created` events).

---

### 4. Immersive Commerce Engine

**Branch:** `immersive-management-service`

This service focuses on integrating 3D models and Augmented Reality (AR) experiences into the e-commerce platform, enhancing product visualization.

**Key Features:**
-   **3D Asset Management Service:** Manages the upload, storage, optimization, and retrieval of 3D models.
-   **Client-Side Implementation:** Integrates `model-viewer` web components for interactive 3D and AR experiences on product pages.
-   **Scalable Deployment:** Designed for high performance and scalability using CDN, load balancers, and caching.

---
### Note : To refer the design documentation for each of this services refer the branch , in the Readme.md the required details are mentioned.
