import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import CodeGenerator from './CodeGenerator';
import SystemGraphPage from './SystemGraphPage';
import BlogGenerator from './BlogGenerator';
import DataWash from './DataWash';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/generator" element={<CodeGenerator />} />
        <Route path="/graph" element={<SystemGraphPage />} />
        <Route path="/blog" element={<BlogGenerator />} />
        <Route path="/data" element={<DataWash />} />
      </Routes>
    </Router>
  );
}

export default App;