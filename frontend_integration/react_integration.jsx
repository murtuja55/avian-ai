import React, { useState } from 'react';

const AvianAI = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setError(null);
        setResult(null);
    };

    const fileToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
            reader.readAsDataURL(file);
        });
    };

    const predictBird = async () => {
        if (!file) {
            setError('Please select an audio file');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            // Convert file to base64
            const base64 = await fileToBase64(file);
            
            // Send to API
            const response = await fetch('https://murtu55-avian-ai-backend.hf.space/run/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "data": [base64]
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                setResult(data);
            } else {
                setError(`API Error: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            setError(`Network Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const styles = {
        container: {
            fontFamily: 'Arial, sans-serif',
            maxWidth: '800px',
            margin: '0 auto',
            padding: '20px',
            backgroundColor: '#f5f5f5'
        },
        card: {
            background: 'white',
            padding: '30px',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        },
        title: {
            textAlign: 'center',
            color: '#333',
            marginBottom: '30px'
        },
        uploadSection: {
            margin: '20px 0',
            textAlign: 'center'
        },
        fileInput: {
            margin: '10px 0',
            padding: '10px',
            border: '2px dashed #ccc',
            borderRadius: '5px',
            background: '#fafafa'
        },
        button: {
            background: '#007bff',
            color: 'white',
            border: 'none',
            padding: '12px 30px',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '16px',
            margin: '10px 0'
        },
        buttonHover: {
            background: '#0056b3'
        },
        buttonDisabled: {
            background: '#ccc',
            cursor: 'not-allowed'
        },
        resultSection: {
            margin: '20px 0',
            padding: '20px',
            borderRadius: '5px',
            borderLeft: '4px solid #007bff'
        },
        loading: {
            textAlign: 'center',
            color: '#007bff',
            fontStyle: 'italic'
        },
        error: {
            color: '#dc3545',
            background: '#f8d7da',
            padding: '10px',
            borderRadius: '5px',
            margin: '10px 0'
        },
        success: {
            color: '#155724',
            background: '#d4edda',
            padding: '10px',
            borderRadius: '5px',
            margin: '10px 0'
        },
        resultText: {
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            background: '#e9ecef',
            padding: '10px',
            borderRadius: '3px',
            margin: '10px 0'
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h1 style={styles.title}>🐦 Avian AI - Bird Sound Recognition</h1>
                
                <div style={styles.uploadSection}>
                    <div style={styles.fileInput}>
                        <input 
                            type="file" 
                            accept="audio/*" 
                            onChange={handleFileChange}
                        />
                        <p>📤 Upload audio file (WAV, MP3, FLAC, M4A)</p>
                        {file && (
                            <small>Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</small>
                        )}
                    </div>
                    <button 
                        style={{
                            ...styles.button,
                            ...(loading ? styles.buttonDisabled : {})
                        }}
                        onClick={predictBird}
                        disabled={loading}
                    >
                        {loading ? '⏳ Processing...' : '🔍 Predict Bird Species'}
                    </button>
                </div>

                {loading && (
                    <div style={styles.loading}>
                        🧠 Analyzing audio... Please wait...
                    </div>
                )}

                {error && (
                    <div style={{...styles.resultSection, ...styles.error}}>
                        <strong>Error:</strong> {error}
                    </div>
                )}

                {result && (
                    <div style={{...styles.resultSection, ...styles.success}}>
                        <h3>📊 Prediction Results</h3>
                        <div style={styles.resultText}>
                            {result.data && result.data[0] ? result.data[0] : 'No prediction data received'}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AvianAI;
