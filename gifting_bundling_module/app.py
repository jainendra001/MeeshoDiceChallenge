from flask import Flask, request, jsonify, render_template
import uuid
import random

app = Flask(__name__, static_folder='static', template_folder='static')

# In-memory "database"
products = {
    "p1": {"id": "p1", "name": "Luxury Watch", "price": 200.00, "seller_id": "s1", "inventory": 5},
    "p2": {"id": "p2", "name": "Designer Handbag", "price": 150.00, "seller_id": "s1", "inventory": 3},
    "p3": {"id": "p3", "name": "Gourmet Coffee Set", "price": 50.00, "seller_id": "s2", "inventory": 10},
    "p4": {"id": "p4", "name": "Artisanal Chocolates", "price": 30.00, "seller_id": "s2", "inventory": 12},
    "p5": {"id": "p5", "name": "Bluetooth Speaker", "price": 80.00, "seller_id": "s3", "inventory": 7},
}

sellers = {
    "s1": {"id": "s1", "name": "Luxury Goods Inc."},
    "s2": {"id": "s2", "name": "Gourmet Delights"},
    "s3": {"id": "s3", "name": "Tech Gadgets Co."},
}

cart = {
    "items": [],
    "total": 0.0,
    "is_gift": False,
    "gift_message": "",
    "gift_wrapping": False
}

bundles = {} # bundle_id: {bundle_name, seller_id, discount_type, discount_value, items: [{product_id, quantity}]}

# Helper to calculate cart total
def calculate_cart_total():
    total = 0.0
    for item in cart["items"]:
        if "bundle_id" in item and item["bundle_id"]:
            bundle = bundles[item["bundle_id"]]
            bundle_price = 0.0
            for b_item in bundle["items"]:
                bundle_price += products[b_item["product_id"]]["price"] * b_item["quantity"]
            
            if bundle["discount_type"] == "PERCENTAGE":
                total += bundle_price * (1 - bundle["discount_value"] / 100)
            elif bundle["discount_type"] == "FIXED":
                total += bundle_price - bundle["discount_value"]
        else:
            total += products[item["product_id"]]["price"] * item["quantity"]
    cart["total"] = round(total, 2)

# API Endpoints

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(list(products.values()))

@app.route('/sellers/<seller_id>/products', methods=['GET'])
def get_seller_products(seller_id):
    seller_products = [p for p in products.values() if p["seller_id"] == seller_id]
    return jsonify(seller_products)

@app.route('/bundles/create', methods=['POST'])
def create_bundle():
    data = request.get_json()
    bundle_id = str(uuid.uuid4())
    
    # Validate products belong to the same seller
    seller_id = data["seller_id"]
    for item in data["items"]:
        if products[item["product_id"]]["seller_id"] != seller_id:
            return jsonify({"error": "All products in a bundle must belong to the same seller."}), 400

    bundles[bundle_id] = {
        "id": bundle_id,
        "name": data["bundle_name"],
        "seller_id": seller_id,
        "discount_type": data.get("discount_type", "FIXED"),
        "discount_value": data.get("discount_value", 0.0),
        "items": data["items"] # [{product_id, quantity}]
    }
    return jsonify(bundles[bundle_id]), 201

@app.route('/cart/add-item', methods=['POST'])
def add_item_to_cart():
    data = request.get_json()
    product_id = data["product_id"]
    quantity = data.get("quantity", 1)

    if product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    if products[product_id]["inventory"] < quantity:
        return jsonify({"error": "Not enough inventory"}), 400

    # Simulate atomic inventory check and update
    products[product_id]["inventory"] -= quantity
    cart["items"].append({"product_id": product_id, "quantity": quantity})
    calculate_cart_total()
    return jsonify(cart), 200

@app.route('/cart/add-bundle', methods=['POST'])
def add_bundle_to_cart():
    data = request.get_json()
    bundle_id = data["bundle_id"]
    
    if bundle_id not in bundles:
        return jsonify({"error": "Bundle not found"}), 404

    bundle = bundles[bundle_id]
    
    # Simulate atomic inventory check for all bundle items
    # This would typically be a database transaction
    temp_inventory = {pid: p["inventory"] for pid, p in products.items()}
    
    for item in bundle["items"]:
        product_id = item["product_id"]
        quantity = item["quantity"]
        if temp_inventory.get(product_id, 0) < quantity:
            return jsonify({"error": f"Not enough inventory for product {products[product_id]['name']}"}), 400
        temp_inventory[product_id] -= quantity # Deduct from temp inventory

    # If all checks pass, update actual inventory and add to cart
    for item in bundle["items"]:
        products[item["product_id"]]["inventory"] -= item["quantity"]
    
    cart["items"].append({"bundle_id": bundle_id, "quantity": 1}) # Bundle is a single line item
    calculate_cart_total()
    return jsonify(cart), 200

@app.route('/cart', methods=['GET'])
def get_cart():
    # Enhance cart items with product details and bundle info for display
    display_items = []
    for item in cart["items"]:
        if "bundle_id" in item and item["bundle_id"]:
            bundle = bundles[item["bundle_id"]]
            bundle_display = {
                "type": "bundle",
                "id": bundle["id"],
                "name": bundle["name"],
                "quantity": item["quantity"],
                "discount_type": bundle["discount_type"],
                "discount_value": bundle["discount_value"],
                "products": []
            }
            bundle_original_price = 0.0
            for b_item in bundle["items"]:
                product = products[b_item["product_id"]]
                bundle_display["products"].append({
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["price"],
                    "quantity": b_item["quantity"]
                })
                bundle_original_price += product["price"] * b_item["quantity"]
            
            if bundle["discount_type"] == "PERCENTAGE":
                bundle_display["price_after_discount"] = bundle_original_price * (1 - bundle["discount_value"] / 100)
                bundle_display["savings"] = bundle_original_price * (bundle["discount_value"] / 100)
            elif bundle["discount_type"] == "FIXED":
                bundle_display["price_after_discount"] = bundle_original_price - bundle["discount_value"]
                bundle_display["savings"] = bundle["discount_value"]
            
            bundle_display["original_price"] = bundle_original_price
            display_items.append(bundle_display)
        else:
            product = products[item["product_id"]]
            display_items.append({
                "type": "product",
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"]
            })
    
    return jsonify({
        "items": display_items,
        "total": cart["total"],
        "is_gift": cart["is_gift"],
        "gift_message": cart["gift_message"],
        "gift_wrapping": cart["gift_wrapping"]
    })

@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    cart["is_gift"] = data.get("is_gift", False)
    cart["gift_message"] = data.get("gift_message", "")
    cart["gift_wrapping"] = data.get("gift_wrapping", False)
    
    # Simulate order processing and fulfillment request
    # In a real system, this would interact with OMS
    order_id = str(uuid.uuid4())
    
    # Clear cart after checkout
    cart["items"] = []
    cart["total"] = 0.0
    cart["is_gift"] = False
    cart["gift_message"] = ""
    cart["gift_wrapping"] = False

    return jsonify({"message": "Checkout successful", "order_id": order_id}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
