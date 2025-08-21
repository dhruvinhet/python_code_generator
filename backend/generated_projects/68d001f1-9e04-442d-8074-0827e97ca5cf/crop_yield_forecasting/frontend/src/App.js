import React, { useState } from 'react';

function App() {
  const [features, setFeatures] = useState({
    temperature: '',
    rainfall: '',
    soil_ph: '',
    sunshine_hours: '',
  });

  const [prediction, setPrediction] = useState(null);

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
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data.prediction);
    } catch (error) {
      console.error('Error making prediction:', error);
      setPrediction('Error making prediction. Please check your input and try again.');
    }
  };

  const handleChange = (e) => {
    setFeatures({ ...features, [e.target.name]: e.target.value });
  };

  return (
    <div className="container">
      <h1>Crop Yield Forecasting</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="temperature">Temperature</label>
          <input 
            type="text" 
            className="form-control" 
            id="temperature" 
            name="temperature" 
            value={features.temperature} 
            onChange={handleChange} 
          />
        </div>
        <div className="form-group">
          <label htmlFor="rainfall">Rainfall</label>
          <input 
            type="text" 
            className="form-control" 
            id="rainfall" 
            name="rainfall" 
            value={features.rainfall} 
            onChange={handleChange} 
          />
        </div>
        <div className="form-group">
          <label htmlFor="soil_ph">Soil pH</label>
          <input 
            type="text" 
            className="form-control" 
            id="soil_ph" 
            name="soil_ph" 
            value={features.soil_ph} 
            onChange={handleChange} 
          />
        </div>
        <div className="form-group">
          <label htmlFor="sunshine_hours">Sunshine Hours</label>
          <input 
            type="text" 
            className="form-control" 
            id="sunshine_hours" 
            name="sunshine_hours" 
            value={features.sunshine_hours} 
            onChange={handleChange} 
          />
        </div>
        <button type="submit" className="btn btn-primary">Submit</button>
        {prediction !== null && (
          <div className="mt-3">
            <h2>Prediction: {prediction}</h2>
          </div>
        )}
      </form>
    </div>
  );
}

export default App;