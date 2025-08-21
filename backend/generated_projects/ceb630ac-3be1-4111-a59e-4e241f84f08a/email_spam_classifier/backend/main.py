from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# Load the pre-trained model (replace 'model.pkl' with your actual model file)
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Error: model.pkl not found. Make sure to train and save your model.")
    exit(1)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        # Assuming the input is a single email as a string
        email_text = data.get('email')
        if email_text is None:
            return jsonify({'error': 'Email text is missing'}), 400

        # Preprocessing (Adapt this to your actual preprocessing steps)
        # Example:  Remove punctuation, lowercase, etc.
        # import string
        # email_text = email_text.lower()
        # email_text = email_text.translate(str.maketrans('', '', string.punctuation))
        
        # Feature Extraction (Adapt this to your actual feature extraction)
        # Example: TF-IDF vectorization (requires scikit-learn)
        # from sklearn.feature_extraction.text import TfidfVectorizer
        # vectorizer = TfidfVectorizer()
        # email_vec = vectorizer.fit_transform([email_text])
        # prediction = model.predict(email_vec)[0]
        
        # Placeholder for prediction - replace with your actual model prediction
        prediction = model.predict([email_text])[0] #Assuming your model accepts a list of strings

        result = {'prediction': 'spam' if prediction == 1 else 'not spam'}
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)