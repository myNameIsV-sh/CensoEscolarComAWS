import { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus('');
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Por favor, selecione um arquivo CSV primeiro.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setStatus('Enviando...');

    try {
      // Substitua pelo IP público da sua EC2
      const response = await fetch('http://18.234.83.141:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Erro no upload');
      }

      setStatus(`Sucesso: ${data.message}`);
    } catch (error) {
      setStatus(`Erro: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'sans-serif' }}>
      <h1>Upload do Censo Escolar</h1>
      
      <div style={{ margin: '20px' }}>
        <input type="file" onChange={handleFileChange} accept=".csv" />
        <button onClick={handleUpload} disabled={loading || !file}>
          {loading ? 'Enviando...' : 'Enviar para S3'}
        </button>
      </div>

      {status && <p style={{ color: status.includes('Erro') ? 'red' : 'green' }}>{status}</p>}
    </div>
  );
}

export default App;
