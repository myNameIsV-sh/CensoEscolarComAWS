import { useState, useEffect } from 'react';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Busca os dados da API Flask
    fetch('http://localhost:5000/')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Erro na requisição ao backend');
        }
        return response.json();
      })
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'sans-serif' }}>
      <h1>Consumindo API Flask com React</h1>
      
      {loading && <p>Carregando...</p>}
      
      {error && <p style={{ color: 'red' }}>Erro: {error}</p>}
      
      {data && (
        <div style={{ padding: '20px', border: '1px solid #ccc', display: 'inline-block', borderRadius: '8px' }}>
          <h3>Mensagem recebida do Python:</h3>
          <p style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#007bff' }}>
            {data.message}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
