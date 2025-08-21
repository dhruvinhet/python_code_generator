import React, { useState } from 'react';

function App() {
  const [features, setFeatures] = useState({
    openPrice: '',
    highPrice: '',
    lowPrice: '',
    volume: '',
    previousClose: ''
  });

  const [prediction, setPrediction] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const requestBody = {
      openPrice: parseFloat(features.openPrice),
      highPrice: parseFloat(features.highPrice),
      lowPrice: parseFloat(features.lowPrice),
      volume: parseFloat(features.volume),
      previousClose: parseFloat(features.previousClose)
    };

    try {
      const response = await fetch('/predict', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error('Error:', error);
      setPrediction({ error: 'Prediction failed. Please check your input and try again.' });
    }
  };

  const handleChange = (e) => {
    setFeatures({ ...features, [e.target.name]: e.target.value });
  };

  return (
    <div className="App">
      <h1>Price Prediction</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="openPrice">Open Price:</label>
          <input type="number" id="openPrice" name="openPrice" value={features.openPrice} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="highPrice">High Price:</label>
          <input type="number" id="highPrice" name="highPrice" value={features.highPrice} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="lowPrice">Low Price:</label>
          <input type="number" id="lowPrice" name="lowPrice" value={features.lowPrice} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="volume">Volume:</label>
          <input type="number" id="volume" name="volume" value={features.volume} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="previousClose">Previous Close:</label>
          <input type="number" id="previousClose" name="previousClose" value={features.previousClose} onChange={handleChange} />
        </div>
        <button type="submit">Predict</button>
      </form>
      {prediction && prediction.error ? (
        <p style={{ color: 'red' }}>{prediction.error}</p>
      ) : prediction && prediction.prediction ? (
        <p>Prediction: {prediction.prediction}</p>
      ) : null}
    </div>
  );
}

export default App;