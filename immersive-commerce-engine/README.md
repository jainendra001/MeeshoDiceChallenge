# Immersive Commerce Engine

A comprehensive 3D and AR-enabled e-commerce platform that enhances the online shopping experience through immersive product visualization.

## Design Documentation

### Overview

The Immersive Commerce Engine enables users to view and interact with products in 3D and AR, providing a more engaging and confident shopping experience. Sellers can upload 3D models of their products, while shoppers can view products from all angles and try them virtually.

### High-Level Design (HLD)

#### System Architecture

```
+------------------+     +----------------------+     +------------------+
|   Client Apps    |     | 3D Asset Management |     |   Cloud Storage |
| (Web/Mobile/AR)  |<--->|       Service       |<--->|    (AWS S3)     |
+------------------+     +----------------------+     +------------------+
         ^                         ^                         ^
         |                         |                         |
         v                         v                         v
+------------------+     +----------------------+     +------------------+
|   CDN Layer      |     |   Authentication &   |     |   Analytics &   |
| (CloudFront)     |     |   Authorization      |     |   Monitoring   |
+------------------+     +----------------------+     +------------------+
```

#### Core Components

1. **Frontend Applications**

   - Web interface with 3D viewer
   - Mobile apps with AR capabilities
   - Progressive Web App support

2. **Backend Services**

   - 3D Asset Management Service
   - Authentication Service
   - Analytics Service

3. **Infrastructure**
   - Cloud Storage for 3D models
   - CDN for global content delivery
   - Load balancers for scalability

For detailed technical documentation, architecture, and integration guide, please see [DESIGN.md](DESIGN.md).

## Quick Start Guide

### 1. 3D Asset Management Service

A Django-based backend service that handles 3D model storage and retrieval.

#### Setup and Running

```bash
cd 3d-asset-management-service
source venv/bin/activate
python manage.py migrate
python manage.py runserver
```

The service will run on http://localhost:8000

API Endpoints:

- GET /api/assets/3d/ - List all 3D assets
- POST /api/assets/3d/ - Upload a new 3D asset
- GET /api/assets/3d/{id}/ - Get specific 3D asset
- PUT /api/assets/3d/{id}/ - Update 3D asset
- DELETE /api/assets/3d/{id}/ - Delete 3D asset

### 2. Client-Side Implementation

A web-based 3D model viewer using Google's <model-viewer> web component.

#### Running

Simply open the index.html file in a modern web browser, or serve it using a local server:

```bash
cd client-side-implementation
python -m http.server 5000
```

The client will run on http://localhost:5000

## Security Considerations

- This is a prototype and includes development-only settings
- In production:
  - Remove CORS_ALLOW_ALL_ORIGINS
  - Implement proper authentication
  - Use environment variables for sensitive data
  - Implement input validation and sanitization
  - Set up proper SSL/TLS
  - Implement rate limiting

## CDN Integration Notes

- For production:
  - Use a CDN like Amazon CloudFront or Cloudflare
  - Configure proper caching headers
  - Use edge locations for global distribution
  - Implement cache invalidation strategy
  - Consider using signed URLs for protected content
