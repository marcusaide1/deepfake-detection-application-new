import { useState, useEffect } from 'react'
import axios from 'axios'
import { FiShield, FiCheck, FiX, FiLoader, FiFolder, FiEye, FiBarChart2, FiGithub, FiExternalLink } from 'react-icons/fi'
import './App.css'

function App() {
  const [image, setImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [dashboardUrl, setDashboardUrl] = useState(null)
  const [githubRepo, setGithubRepo] = useState(null)

  useEffect(() => {
    // Fetch dashboard and GitHub repo URLs
    const fetchLinks = async () => {
      try {
        const apiEndpoint = import.meta.env.VITE_API_ENDPOINT
        if (apiEndpoint) {
          const response = await axios.get(`${apiEndpoint}/dashboard`)
          if (response.data) {
            // Handle both string and object responses
            let data = response.data
            if (typeof data === 'string') {
              try {
                data = JSON.parse(data)
              } catch (e) {
                // If parsing fails, log error and try to continue with original data
                console.warn('Failed to parse response data as JSON:', e)
                // If it's already a string, try to check if it might be a wrapped response
                // Otherwise, set data to null to avoid further errors
                data = null
              }
            }
            // Handle nested body structure from API Gateway
            if (data && data.body) {
              if (typeof data.body === 'string') {
                try {
                  data = JSON.parse(data.body)
                } catch (e) {
                  console.warn('Failed to parse body as JSON:', e)
                  data = null
                }
              } else {
                data = data.body
              }
            }
            if (data && data.dashboard_url && data.github_repo) {
              setDashboardUrl(data.dashboard_url)
              setGithubRepo(data.github_repo)
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch dashboard info:', error)
        // Set default GitHub repo if API fails
        setGithubRepo('https://github.com/yourusername/deepfake-detection')
      }
    }
    fetchLinks()
  }, [])

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => setImage(e.target.result)
      reader.readAsDataURL(file)
      setResult(null)
      setError(null)
    }
  }

  const uploadImage = async () => {
    if (!image) return
    
    setLoading(true)
    setError(null)
    
    try {
      const base64 = image.split(',')[1]
      const response = await axios.post(`${import.meta.env.VITE_API_ENDPOINT}/upload`, {
        image: base64
      })
      

      setResult(response.data)
    } catch (error) {
      console.error('Upload failed:', error)
      setError(error.response?.data?.error || 'Upload failed')
    }
    setLoading(false)
  }

  return (
    <div className="app">
      {/* Banner Section */}
      <div className="banner-container">
        {dashboardUrl && (
          <a 
            href={dashboardUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="banner-link"
          >
            <div className="banner dashboard-banner">
              <div className="banner-content">
                <FiBarChart2 className="banner-icon" />
                <span>Monitoring Dashboard</span>
              </div>
              <FiExternalLink className="external-icon" />
            </div>
          </a>
        )}
        {githubRepo && (
          <a 
            href={githubRepo} 
            target="_blank" 
            rel="noopener noreferrer"
            className="banner-link"
          >
            <div className="banner github-banner">
              <div className="banner-content">
                <FiGithub className="banner-icon" />
                <span>GitHub Repository</span>
              </div>
              <FiExternalLink className="external-icon" />
            </div>
          </a>
        )}
      </div>

      <div className="header">
        <FiShield className="header-icon" />
        <h1>Deepfake Detection</h1>
        <p>Advanced deepfake detection powered by AI</p>
      </div>
      
      <div className="upload-section">
        <div className="file-input-wrapper">
          <input 
            type="file" 
            accept="image/*" 
            onChange={handleImageUpload}
            id="file-input"
            className="file-input"
          />
          <label htmlFor="file-input" className="file-label">
            <FiFolder />
            Choose Image
          </label>
        </div>
        
        {image && (
          <div className="image-preview">
            <img src={image} alt="Preview" className="preview-img" />
            <button 
              onClick={uploadImage} 
              disabled={loading}
              className="upload-btn"
            >
              {loading ? (
                <>
                  <FiLoader className="spinning" />
                  Analyzing...
                </>
              ) : (
                <>
                  <FiEye />
                  Analyze
                </>
              )}
            </button>
          </div>
        )}
      </div>
      
      {error && (
        <div className="alert error">
          <FiX />
          <span>{error}</span>
        </div>
      )}
      
      {result && result.body?.detection_result && (
        <div className="results-section">
          <div className="results-header">
            <FiEye className="results-icon" />
            <h3>Analysis Complete</h3>
          </div>
          
          {result.body.detection_result.data[0].bounding_boxes.map((detection, i) => {
            const isDeepfake = detection.is_deepfake > 0.5
            const fakeConfidence = (detection.is_deepfake * 100).toFixed(1)
            const realConfidence = ((1 - detection.is_deepfake) * 100).toFixed(1)
            const detectionConf = (detection.bbox_confidence * 100).toFixed(1)
            
            return (
              <div key={i} className={`result-card ${isDeepfake ? 'fake' : 'real'}`}>
                <div className="result-main">
                  <div className="result-icon">
                    {isDeepfake ? <FiX size={24} /> : <FiCheck size={24} />}
                  </div>
                  <div className="result-content">
                    <div className="status-badge">
                      {isDeepfake ? 'DEEPFAKE DETECTED' : 'AUTHENTIC IMAGE'}
                    </div>
                    <div className="confidence-score">
                      {isDeepfake ? 'Fake' : 'Authentic'} Confidence: <strong>{isDeepfake ? fakeConfidence : realConfidence}%</strong>
                    </div>
                    <div className="detection-score">
                      Detection Accuracy: <strong>{detectionConf}%</strong>
                    </div>
                  </div>
                </div>
                <div className="confidence-bar">
                  <div 
                    className={`confidence-fill ${isDeepfake ? 'fake-fill' : 'real-fill'}`}
                    style={{ width: `${isDeepfake ? fakeConfidence : realConfidence}%` }}
                  ></div>
                </div>
              </div>
            )
          })}
        </div>
      )}
      
      <footer style={{ 
        textAlign: 'center', 
        marginTop: '2rem', 
        padding: '1rem', 
        fontSize: '0.8rem', 
        opacity: '0.7',
        color: 'white'
      }}>
        Built by Louis Echefu
      </footer>
    </div>
  )
}

export default App