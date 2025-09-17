import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import CodeGenerator from './CodeGenerator';
import SystemGraphPage from './SystemGraphPage';
import BlogGenerator from './BlogGenerator';
import SlideGenerator from './SlideGenerator';
import ExamForge from './ExamForge';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/generator" element={<CodeGenerator />} />
        <Route path="/graph" element={<SystemGraphPage />} />
        <Route path="/blog" element={<BlogGenerator />} />
        <Route path="/slide" element={<SlideGenerator />} />
        <Route path="/examforge" element={<ExamForge />} />
      </Routes>
    </Router>
  );
}

export default App;