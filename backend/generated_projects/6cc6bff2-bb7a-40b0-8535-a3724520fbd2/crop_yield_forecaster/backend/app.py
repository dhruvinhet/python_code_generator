from flask import Flask, request, jsonify
import json
import pickle
import numpy as np

# Replace with your actual model loading code
# Assuming a pre-trained model is saved as 'model.pkl'
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Error: model.pkl not found. Train your model and save it before running the app.")
    exit(1)

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        # Assuming your data is a dictionary with keys matching your features
        # Replace with the actual feature names from your dataset 
        # Example:  if features are ['temperature', 'rainfall', 'humidity']
        try:
            input_data = [data['temperature'], data['rainfall'], data['humidity']]
            input_data = np.array(input_data, dtype=float).reshape(1, -1) #Reshape for single prediction

        except KeyError as e:
            return jsonify({'error': f'Missing required feature: {e}'}), 400
        except ValueError as e:
            return jsonify({'error': f'Invalid input data type: {e}'}), 400


        prediction = model.predict(input_data)
        result = {'crop_yield': prediction[0]}
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)