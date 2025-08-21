# This is a sample model training script.  Replace with your actual training code.
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

# Replace 'your_email_data.csv' with your actual dataset file
data = pd.read_csv('your_email_data.csv') #This requires a CSV file with at least 'email' and 'spam' columns

# Assuming your data has columns 'email' (text) and 'spam' (0 or 1)
X = data['email']
y = data['spam']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression()
model.fit(X_train_vec, y_train)

# Save the trained model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
    pickle.dump(vectorizer, f) #Save vectorizer as well

print('Model trained and saved successfully!')