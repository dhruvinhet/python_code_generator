import React, { useState, useEffect } from 'react';

const LOADING_MESSAGES = [
  "Uploading your document...",
  "Extracting text and preparing for analysis...",
  "Chunking the document into smaller, manageable sections...",
  "Generating embeddings for efficient retrieval...",
  "Building the FAISS index for lightning-fast search...",
  "Consulting the knowledge base to generate your quiz...",
  "Finalizing questions and answers...",
  "Almost there! Just a moment longer..."
];

const LoadingSpinner = () => {
  const [messageIndex, setMessageIndex] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex(prevIndex => {
        if (prevIndex === LOADING_MESSAGES.length - 1) {
          return prevIndex;
        }
        return prevIndex + 1;
      });
    }, 3000);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-[#7847eb]"></div>
      <p className="mt-4 text-[#a59db8]">{LOADING_MESSAGES[messageIndex]}</p>
    </div>
  );
};

export default LoadingSpinner;
