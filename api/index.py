from flask import Flask, request, jsonify
import math  
import random  

app = Flask(__name__)


product_details = {
    "A": {"warehouse": "C1", "item_weight": 3},
    "B": {"warehouse": "C1", "item_weight": 2},
    "C": {"warehouse": "C1", "item_weight": 8},
    "D": {"warehouse": "C2", "item_weight": 12},
    "E": {"warehouse": "C2", "item_weight": 25},
    "F": {"warehouse": "C2", "item_weight": 15},
    "G": {"warehouse": "C3", "item_weight": 0.5},
    "H": {"warehouse": "C3", "item_weight": 1},
    "I": {"warehouse": "C3", "item_weight": 2},
}


distance_matrix = {
    "C1": {"C2": 4, "C3": 2.5, "L1": 3},
    "C2": {"C1": 4, "C3": 3, "L1": 3},
    "C3": {"C1": 2.5, "C2": 3, "L1": 2},
    "L1": {"C1": 3, "C2": 3, "C3": 2},
}
@app.route("/", methods=["GET"])
def hello():
    return "Welcome to the Delivery Cost API!"


def calculate_shipping_cost(total_weight_kg, travel_distance_km):
    """
    Determines the shipping cost based on the total weight of the items
    and the distance they need to be transported.
    """

    base_cost = 10  
    heavy_cost_per_5kg = 8  

    if total_weight_kg <= 0:
        return 0 

    cost = 0
    if total_weight_kg <= 5:
        cost = travel_distance_km * base_cost
    else:
        cost = travel_distance_km * (
            base_cost + math.floor(total_weight_kg / 5) * heavy_cost_per_5kg
        ) 
        remaining_weight = total_weight_kg % 5
        if remaining_weight > 0:
            cost += travel_distance_km * heavy_cost_per_5kg

  
    cost += random.uniform(-0.5, 0.5)  
    return round(cost, 2)  


def calculate_route_cost(route_taken, cumulative_weight):
    """
    Calculates the total cost of a given delivery route.
    """
    overall_cost = 0
    for i in range(len(route_taken) - 1):
        overall_cost += calculate_shipping_cost(
            cumulative_weight, distance_matrix[route_taken[i]][route_taken[i + 1]]
        )
    return overall_cost


def determine_minimum_delivery_cost(order_items):
    """
    Calculates the absolute minimum cost to deliver a set of ordered items
    from various warehouses to the customer's location.
    """

    minimum_cost = float("inf")  
    warehouses_involved = set()
    total_order_weight = 0

   
    for item, quantity_requested in order_items.items():
        if item in product_details:
            warehouses_involved.add(product_details[item]["warehouse"])
            total_order_weight += product_details[item]["item_weight"] * quantity_requested
        else:
            return jsonify({"error": f"Item '{item}' is not recognized."}), 400

    warehouse_list = list(warehouses_involved)

   
    if len(warehouses_involved) == 1:
        optimal_route = [warehouse_list[0], "L1"]
        cost_of_route = calculate_route_cost(optimal_route, total_order_weight)
        minimum_cost = min(minimum_cost, cost_of_route)

    
    elif len(warehouses_involved) > 1:
        from itertools import permutations 

        possible_routes = list(permutations(warehouse_list))

        for route_permutation in possible_routes:
            current_route = ["L1"] 
            for warehouse in route_permutation:
                current_route.append(warehouse)
                current_route.append("L1") 

            cost_for_permutation = calculate_route_cost(current_route, total_order_weight)
            minimum_cost = min(minimum_cost, cost_for_permutation)

    return round(minimum_cost, 2)


@app.route("/calculate_delivery_fee", methods=["POST"])
def delivery_fee_endpoint():
    """
    API endpoint to calculate the minimum delivery fee for a given order.
    """
    customer_order = request.get_json()
    if not customer_order:
        return (
            jsonify({"error": "Invalid request. Please provide order details in JSON."}),
            400,
        )

    try:
        lowest_fee = determine_minimum_delivery_cost(customer_order)
        return jsonify({"minimum_delivery_fee": lowest_fee}), 200
    except Exception as problem:
        return jsonify({"error": str(problem)}), 500


if __name__ == "__main__":
    app.run(debug=True)
