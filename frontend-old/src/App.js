import React, { useEffect, useState } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [apiStatus, setApiStatus] = useState('Checking...');

  useEffect(() => {
    const checkAPI = async () => {
      try {
        const response = await axios.get('http://localhost:8000/health');
        setApiStatus(`Connected - ${response.data.status}`);
      } catch (error) {
        setApiStatus('API not reachable');
      }
    };

    checkAPI();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>CAPTCHA Dental AI</h1>
        <p>Dental Annotation and Classification Platform</p>
        <div className="status">
          <strong>API Status:</strong> {apiStatus}
        </div>
      </header>
    </div>
  );
}

export default App;
