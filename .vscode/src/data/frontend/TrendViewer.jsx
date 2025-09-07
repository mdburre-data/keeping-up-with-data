// src/components/TrendViewer.jsx
import React, {useState} from 'react';

export default function TrendViewer(){
  const [kw, setKw] = useState('oversized blazer');
  const [data, setData] = useState(null);

  async function getPredictions(){
    const res = await fetch(`http://localhost:8000/predict?keyword=${encodeURIComponent(kw)}&periods=12`);
    const json = await res.json();
    setData(json);
  }

  return (
    <div>
      <input value={kw} onChange={e=>setKw(e.target.value)} />
      <button onClick={getPredictions}>Predict</button>

      {data && (
        <pre style={{whiteSpace:'pre-wrap', maxHeight:400, overflow:'auto'}}>
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}
