import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import CodeGenerator from './CodeGenerator';
import SystemGraphPage from './SystemGraphPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/generator" element={<CodeGenerator />} />
        <Route path="/graph" element={<SystemGraphPage />} />
      </Routes>
    </Router>
  );
}

export default App;