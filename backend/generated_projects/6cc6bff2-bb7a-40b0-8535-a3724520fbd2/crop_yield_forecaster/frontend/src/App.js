import React, { useState } from 'react';

function App() {
  const [features, setFeatures] = useState({
    temperature: '',
    rainfall: '',
    sunlightHours: '',
    soilType: '',
  });

  const [prediction, setPrediction] = useState(null);

  const handleChange = (e) => {
    setFeatures({ ...features, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(features),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.error || `HTTP error! status: ${response.status}`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setPrediction(data.prediction);
    } catch (error) {
      console.error('Error:', error);
      setPrediction(`Error predicting yield: ${error.message}`);
    }
  };

  return (
    <div className="container">
      <h1>Crop Yield Forecaster</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="temperature">Temperature (°C):</label>
          <input
            type="number"
            className="form-control"
            id="temperature"
            name="temperature"
            value={features.temperature}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="rainfall">Rainfall (mm):</label>
          <input
            type="number"
            className="form-control"
            id="rainfall"
            name="rainfall"
            value={features.rainfall}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="sunlightHours">Sunlight Hours:</label>
          <input
            type="number"
            className="form-control"
            id="sunlightHours"
            name="sunlightHours"
            value={features.sunlightHours}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="soilType">Soil Type:</label>
          <input
            type="text"
            className="form-control"
            id="soilType"
            name="soilType"
            value={features.soilType}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary">Predict</button>
      </form>
      {prediction !== null && (
        <div className="alert alert-success mt-3" role="alert">
          Predicted Yield: {prediction}
        </div>
      )}
      {prediction === 'Error predicting yield.' && (
        <div className="alert alert-danger mt-3" role="alert">
          {prediction}
        </div>
      )}
    </div>
  );
}

export default App;