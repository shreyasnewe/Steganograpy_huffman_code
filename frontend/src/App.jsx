import { useState } from 'react';
import { Upload, Lock, Unlock, Download, AlertCircle, Image } from 'lucide-react';
import './index.css';
import './app.css';
import Loader from "./Loader.jsx"; // loader import
import "./loader.css"; // import CSS for fade animation

export default function App() {
  const [mode, setMode] = useState('encode');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [textToEncode, setTextToEncode] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
      setResult(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
      setResult(null);
    }
  };

  const handleEncode = async () => {
    if (!selectedFile || !textToEncode.trim()) {
      setError('Please select an image and enter text to encode');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('text', textToEncode);

    try {
      const response = await fetch('http://localhost:5000/encode', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Encoding failed');
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to encode. Make sure Flask server is running on port 5000');
    } finally {
      setLoading(false);
    }
  };

  const handleDecode = async () => {
    if (!selectedFile) {
      setError('Please select an encoded image');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch('http://localhost:5000/decode', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Decoding failed');
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to decode. Make sure Flask server is running on port 5000');
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = () => {
    if (result?.encoded_image_url) {
      window.open(`http://localhost:5000${result.encoded_image_url}`, '_blank');
    }
  };

  return (
    <div className="card">
      <img src="/logo.png" className="logo" alt="App logo" />
      <h1>Steganography</h1>
      <p className="read-the-docs">Hide messages in images</p>
      <div className="flex gap-2 mb-6" style={{ justifyContent: 'center', margin: '1em 0' }}>
        <button
          onClick={() => { setMode('encode'); setResult(null); setError(null); }}
          className={mode === 'encode' ? 'bg-gray-900 text-white' : ''}
          style={{ marginRight: 8 }}
        >
          <Lock size={16} /> Encode
        </button>
        <button
          onClick={() => { setMode('decode'); setResult(null); setError(null); setTextToEncode(''); }}
          className={mode === 'decode' ? 'bg-gray-900 text-white' : ''}
        >
          <Unlock size={16} /> Decode
        </button>
      </div>

      <div
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
        style={{
          border: '1px dashed #646cff',
          borderRadius: 8,
          padding: '1.5em',
          marginBottom: '1.5em',
          cursor: 'pointer',
          background: '#19191c'
        }}
        onClick={() => document.getElementById('file-input').click()}
      >
        {previewUrl
          ? <img src={previewUrl} alt="Preview" style={{ maxHeight: '180px', margin: 'auto' }} />
          : <Upload size={36} style={{ display: 'block', margin: 'auto', color: '#888' }} />}
        <p style={{ color: '#aaa', fontSize: '0.98em' }}>{selectedFile ? selectedFile.name : "Drop or click to upload (PNG/JPG/BMP)"}</p>
        <input
          id="file-input"
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          hidden
        />
      </div>

      {mode === 'encode' && (
        <div style={{ marginBottom: '1.2em' }}>
          <label>Secret message</label>
          <textarea
            value={textToEncode}
            onChange={e => setTextToEncode(e.target.value)}
            placeholder="Type message..."
            rows={3}
            style={{ width: '100%', resize: 'vertical' }}
          />
          <div style={{ color: '#888', fontSize: '0.93em' }}>
            {textToEncode.length} characters ({textToEncode.length * 8} bits uncompressed)
          </div>
        </div>
      )}

      {error && (
        <div style={{ background: '#3c2222', color: '#ffaaaa', padding: 12, borderRadius: 8, marginBottom: 18 }}>
          <AlertCircle size={16} /> <span>{error}</span>
        </div>
      )}

      {result && mode === 'encode' && (
        <div style={{ background: '#234626', color: '#b8f2bb', padding: 12, borderRadius: 8, marginBottom: 18 }}>
          <h3 style={{ marginBottom: 6 }}>Encoding Successful</h3>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.95em' }}>
            <span>Bits: {result.bits}</span>
            <span>Compression: {result.compression}%</span>
          </div>
          <button onClick={downloadImage} style={{ marginTop: 12 }}>
            <Download size={16} /> Download Image
          </button>
        </div>
      )}

      {result && mode === 'decode' && (
        <div style={{ background: '#22293a', color: '#fff', padding: 12, borderRadius: 8, marginBottom: 18 }}>
          <h3>Decoded message</h3>
          <p style={{ fontSize: '0.98em', wordBreak: 'break-word', marginTop: 12 }}>{result.decoded_text}</p>
        </div>
      )}

      <button
        onClick={mode === 'encode' ? handleEncode : handleDecode}
        disabled={loading || !selectedFile || (mode === 'encode' && !textToEncode.trim())}
        style={{
          background: loading ? '#444' : '#646cff',
          color: '#fff',
          width: '100%',
          padding: '0.9em',
          marginBottom: 12,
          marginTop: 6,
          opacity: loading ? 0.7 : 1,
          borderRadius: 8,
          border: 'none'
        }}
      >
        {loading ? "Processing..." : mode === 'encode' ? "Encode & Hide" : "Extract & Decode"}
      </button>
      <div className="read-the-docs" style={{ marginTop: 16 }}></div>
    </div>
  );
}
