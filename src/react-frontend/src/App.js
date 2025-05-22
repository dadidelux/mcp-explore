import React, { useState } from 'react';
import './App.css';

const TEMPLATES = [
  { id: '97984', name: 'Disaster Girl' },
  { id: '112126428', name: 'Distracted Boyfriend' },
  { id: '124822590', name: 'Left Exit 12 Off Ramp' },
  { id: '61579', name: 'One Does Not Simply' },
  { id: '181913649', name: 'Drake Hotline Bling' },
];

function App() {
  const [templateId, setTemplateId] = useState(TEMPLATES[0].id);
  const [topText, setTopText] = useState('');
  const [bottomText, setBottomText] = useState('');
  const [memeUrl, setMemeUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/generate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: templateId,
          text0: topText,
          text1: bottomText,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setMemeUrl(data.url);
      }
    } catch (error) {
      console.error('Error generating meme:', error);
    }
  };

  return (
    <div className="App">
      <div className="container mt-5">
        <h1 className="mb-4">Meme Generator</h1>
        
        <div className="row">
          <div className="col-md-6">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Choose Template</label>
                <select 
                  className="form-select"
                  value={templateId}
                  onChange={(e) => setTemplateId(e.target.value)}
                >
                  {TEMPLATES.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="mb-3">
                <label className="form-label">Top Text</label>
                <input
                  type="text"
                  className="form-control"
                  value={topText}
                  onChange={(e) => setTopText(e.target.value)}
                />
              </div>
              
              <div className="mb-3">
                <label className="form-label">Bottom Text</label>
                <input
                  type="text"
                  className="form-control"
                  value={bottomText}
                  onChange={(e) => setBottomText(e.target.value)}
                />
              </div>
              
              <button type="submit" className="btn btn-primary">
                Generate Meme
              </button>
            </form>
          </div>
          
          <div className="col-md-6">
            {memeUrl && (
              <div className="meme-preview">
                <h2>Your Meme:</h2>
                <img src={memeUrl} alt="Generated Meme" className="img-fluid" />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
