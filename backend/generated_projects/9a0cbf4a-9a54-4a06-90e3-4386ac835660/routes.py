from flask import Blueprint, request, jsonify
from avl_tree import AVLTree
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')

# AVL Tree Specific Endpoint
@api.route('/build-avl-tree', methods=['POST'])
def build_avl_tree_api():
    data = request.get_json()
    if not data or 'numbers' not in data:
        logger.warning("Build AVL Tree: Missing 'numbers' in request body.")
        return jsonify({"error": "Invalid input: 'numbers' list is required."}), 400

    numbers_raw = data['numbers']

    if not isinstance(numbers_raw, list):
        logger.warning("Build AVL Tree: 'numbers' is not a list.")
        return jsonify({"error": "'numbers' must be a list of numeric values."}), 400

    # Validate and convert each number in the list
    validated_numbers = []
    for num in numbers_raw:
        try:
            # Attempt to convert to int. Floats are generally not used in simple AVL visualizers, 
            # but if allowed, float(num) would be more robust. Sticking to int for typical use case.
            if isinstance(num, (int, float)):
                validated_numbers.append(int(num)) # Convert floats to int if they came as floats
            elif isinstance(num, str):
                validated_numbers.append(int(num)) # Convert string representations of integers
            else:
                raise ValueError(f"Non-numeric value found: {num}")
        except (ValueError, TypeError):
            logger.warning(f"Build AVL Tree: Invalid numeric value encountered: {num}.")
            return jsonify({"error": f"All values in 'numbers' must be numeric. Found invalid value: {num}"}), 400

    if not validated_numbers:
        logger.info("Build AVL Tree: No valid numbers provided, returning empty tree.")
        return jsonify({"tree": None, "message": "No numbers provided to build tree."}), 200

    try:
        avl_tree = AVLTree()
        avl_tree.build_from_list(validated_numbers)
        tree_representation = avl_tree.to_dict()
        logger.info("AVL Tree built and serialized successfully.")
        return jsonify({"tree": tree_representation}), 200
    except Exception as e:
        logger.error(f"Error building AVL tree: {e}", exc_info=True)
        return jsonify({"error": "Failed to build AVL tree", "details": str(e)}), 500
