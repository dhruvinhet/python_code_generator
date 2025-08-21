import React, { useEffect } from 'react';

const GoogleCustomSearch = ({ 
  searchEngineId = "417dbc2216a1d4406", 
  width = "100%", 
  height = "400px",
  placeholder = "Search for research topics..."
}) => {
  useEffect(() => {
    // Load Google Custom Search script if not already loaded
    if (!window.google || !window.google.search) {
      const script = document.createElement('script');
      script.src = `https://cse.google.com/cse.js?cx=${searchEngineId}`;
      script.async = true;
      document.head.appendChild(script);

      return () => {
        // Cleanup script when component unmounts
        if (document.head.contains(script)) {
          document.head.removeChild(script);
        }
      };
    }
  }, [searchEngineId]);

  return (
    <div style={{ 
      width: width, 
      height: height, 
      border: '1px solid #ddd', 
      borderRadius: '8px',
      padding: '16px',
      backgroundColor: '#f9f9f9'
    }}>
      <h3 style={{ 
        marginTop: 0, 
        color: '#333',
        fontSize: '18px',
        marginBottom: '16px'
      }}>
        🔍 Research Search Engine
      </h3>
      <div 
        className="gcse-search"
        data-resultsUrl=""
        data-newWindow="true"
        data-linktarget="_blank"
      ></div>
      <p style={{ 
        fontSize: '12px', 
        color: '#666', 
        marginTop: '12px',
        fontStyle: 'italic'
      }}>
        Use this search engine to research topics before generating your blog. 
        Results will open in new tabs for reference.
      </p>
    </div>
  );
};

export default GoogleCustomSearch;