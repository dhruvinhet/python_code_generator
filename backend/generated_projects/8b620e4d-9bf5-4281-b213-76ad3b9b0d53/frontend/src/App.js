import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (event) => {
    setText(event.target.value);
  };

  const analyzeSentiment = async () => {
    setLoading(true);
    setError(null);
    setSentiment(null);

    try {
      const response = await axios.post('http://localhost:7000/analyze', { text });
      setSentiment(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>Sentiment Analysis</h1>
      <textarea
        rows="4"
        cols="50"
        placeholder="Enter text to analyze..."
        value={text}
        onChange={handleChange}
      />
      <button onClick={analyzeSentiment} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>

      {error && <div className="error-message">Error: {error}</div>}

      {sentiment && (
        <div className="sentiment-result">
          <h2>Result:</h2>
          <p><b>Label:</b> {sentiment.label}</p>
          <p><b>Score:</b> {sentiment.score}</p>
        </div>
      )}
    </div>
  );
}

export default App;