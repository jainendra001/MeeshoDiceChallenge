# Gifting & Bundling Module Prototype

This project implements a prototype for an "Enhanced Gifting & Bundling Module" as described in the task. It consists of a simple Flask backend and a basic HTML/JavaScript frontend to demonstrate the core functionalities.

## Features

### Gifting

- At checkout, a "This is a gift" checkbox appears.
- If selected, options to add a personalized message and purchase gift wrapping are revealed.

### Seller-Centric Bundling ("Build a Hamper")

- A "Create a Bundle" feature is available on a simulated seller's storefront (Seller S1).
- Customers can select multiple products from that single seller, which are then grouped into a virtual "hamper."
- This hamper is added to the cart as a single line item with a potential bundle discount.
- The system simulates atomic inventory checks for all items within a bundle before adding it to the cart.
- The cart visually groups bundled items together and displays the applied savings clearly.

## Application Design

### High-Level Design (HLD)

1.  **Cart & Checkout Microservices (Simulated by Flask `app.py`):**

    - Modified to support a "gift" flag and associated metadata (message, wrapping preference).
    - Handles adding individual items and bundles to the cart.
    - Manages the checkout process, including gift options.

2.  **Bundling Service (Integrated into Flask `app.py`):**

    - Manages the logic for creating, pricing, and validating dynamic, user-generated bundles.
    - Exposes API endpoints for bundle creation and adding bundles to the cart.

3.  **Order Management System (OMS) (Simulated in Flask `checkout` endpoint):**
    - Updated to recognize a bundled item.
    - Generates a single fulfillment request to the seller and logistics partner, ensuring all items in the bundle are packed and shipped together (simulated by clearing the cart and returning an order ID).

### Low-Level Design (LLD)

#### Database Schema (In-memory representation in `app.py`):

- **`products` (Dictionary):** Simulates a products table with `id`, `name`, `price`, `seller_id`, `inventory`.
- **`sellers` (Dictionary):** Simulates a sellers table with `id`, `name`.
- **`cart` (Dictionary):** Represents the current user's cart with `items`, `total`, `is_gift`, `gift_message`, `gift_wrapping`.
- **`bundles` (Dictionary):** Simulates a new `bundles` table.
  - `bundle_id` (PK)
  - `seller_id` (FK)
  - `bundle_name` (VARCHAR)
  - `discount_type` (ENUM: 'PERCENTAGE', 'FIXED')
  - `discount_value` (DECIMAL)
  - `items`: A list of dictionaries, each containing `product_id` (FK) and `quantity`, simulating a `bundle_items` mapping table.

#### API (Implemented in Flask `app.py`):

- `GET /products`: Returns a list of all available products.
- `GET /sellers/<seller_id>/products`: Returns products belonging to a specific seller.
- `POST /bundles/create`:
  - **Purpose:** For sellers (or customers in bundle mode) to create a new bundle.
  - **Request Body:** `{ "bundle_name": "string", "seller_id": "string", "discount_type": "ENUM", "discount_value": "decimal", "items": [{ "product_id": "string", "quantity": "integer" }] }`
  - **Validation:** Ensures all products in the bundle belong to the specified `seller_id`.
  - **Response:** The created bundle object.
- `POST /cart/add-item`:
  - **Purpose:** Adds a single product to the cart.
  - **Request Body:** `{ "product_id": "string", "quantity": "integer" }`
  - **Inventory Check:** Checks product inventory.
- `POST /cart/add-bundle`:
  - **Purpose:** Adds a created bundle to the cart.
  - **Request Body:** `{ "bundle_id": "string" }`
  - **Atomic Inventory Checks:** Wraps inventory checks for all constituent products within a single logical transaction (simulated by `temp_inventory` in the prototype) to ensure all items are available before confirming the addition to the cart.
- `GET /cart`: Returns the current cart contents, including enhanced details for bundled items.
- `POST /checkout`:
  - **Purpose:** Simulates the checkout process.
  - **Request Body:** `{ "is_gift": "boolean", "gift_message": "string", "gift_wrapping": "boolean" }`
  - **Functionality:** Updates cart with gift options, simulates order creation, and clears the cart.

#### Frontend (Implemented in `static/index.html` using HTML, CSS, and JavaScript):

- **Seller's Store Page UI:** Features a "Start Building Hamper" button.
  - Clicking this button enters "bundle mode," highlighting seller-specific products.
  - Users can select multiple products to form a hamper.
  - A "Create Hamper" button becomes visible, along with input fields for bundle name, discount type, and discount value.
- **Cart Display:**
  - Visually groups bundled items together.
  - Displays the applied savings clearly for bundles.
  - Includes the "This is a gift" checkbox at checkout, which reveals fields for a personalized message and gift wrapping.

## Setup and Running the Prototype

1.  **Navigate to the project directory:**

    ```bash
    cd gifting_bundling_module
    ```

2.  **Activate the virtual environment:**

    ```bash
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application:**

    ```bash
    flask run
    ```

    The application will start on `http://127.0.0.1:5000`.

5.  **Open the prototype in your browser:**
    Navigate to `http://127.0.0.1:5000` in your web browser.

## How to Use the Prototype

### Adding Regular Products to Cart

- On the main page, you'll see a list of "Products".
- Click "Add to Cart" next to any product to add it to your cart.
- The cart section at the bottom will update.

### Gifting Options

- In the "Your Cart" section, check the "This is a gift" checkbox.
- Input fields for "Personalized Message" and "Add Gift Wrapping" will appear.
- Enter a message and/or check the gift wrapping option.
- Click "Checkout" to simulate placing the order with these gift options.

### Creating and Adding a Bundle (Hamper)

1.  **Enter Bundle Mode:** In the "Seller Storefront (Seller S1 Example)" section, click the "Start Building Hamper (Seller S1)" button.
    - The product cards for Seller S1 will be highlighted.
    - A "Create Hamper" button and bundle creation fields will appear.
2.  **Select Products:** Click on "Luxury Watch" and "Designer Handbag" within the Seller S1 section. They will be highlighted, and their names will appear in the "Selected for Hamper" list.
3.  **Configure Bundle:**
    - Enter a "Hamper Name" (e.g., "Luxury Duo Hamper").
    - Choose a "Discount Type" (e.g., "PERCENTAGE").
    - Enter a "Discount Value" (e.g., "10" for 10% or $10 fixed).
4.  **Create and Add to Cart:** Click the "Create Hamper" button.
    - The bundle will be created and automatically added to your cart as a single line item.
    - The cart display will show the bundle, its contents, original price, discount, and final price.
    - Bundle mode will automatically exit.

### Checkout

- After adding items and/or bundles, click the "Checkout" button in the "Your Cart" section.
- A success message will appear, and your cart will be cleared.
