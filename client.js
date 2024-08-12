// client-app/src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [plates, setPlates] = useState([]);

  useEffect(() => {
    axios.get('/api/plates')
      .then(response => {
        setPlates(response.data);
      })
      .catch(error => {
        console.error('Error fetching plates:', error);
      });
  }, []);

  return (
    <div>
      <h1>Client App</h1>
      <ul>
        {plates.map(plate => (
          <li key={plate.id}>{plate.plate_text}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
