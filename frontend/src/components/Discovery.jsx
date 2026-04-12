import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Command, Activity, Clock, Hash, ArrowLeft } from 'lucide-react'
import Navbar from './Navbar'

function Discovery() {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetch('/api/status')
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error("API Error", err))
  }, [])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query) return
    
    setLoading(true)
    const res = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    })
    const data = await res.json()
    if (data.results) {
      setResults(data.results)
    }
    setLoading(false)
  }

  const msToMinSec = (ms) => {
    if (!ms) return '--:--'
    const minutes = Math.floor(ms / 60000)
    const seconds = ((ms % 60000) / 1000).toFixed(0)
    return minutes + ":" + (seconds < 10 ? '0' : '') + seconds
  }

  return (
    <div className="reveal-up">
      <Navbar />

      <div className="dashboard-container section-wrapper">
        <div className="technical-header staggered-item" style={{ animationDelay: '0.1s' }}>
           <div className="logo-text-ultra" style={{ fontSize: '9px', marginBottom: '8px', color: 'var(--accent-cyan)' }}>SUBSYSTEM_ROOT / CATALOG_SCAN</div>
           <h2 style={{ fontSize: '36px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Search Engine</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginTop: '8px' }}>
              {status ? `System Synced // ${status.catalog_size} vectors indexed.` : "Connecting..."}
           </p>
        </div>

        <form onSubmit={handleSearch} className="command-bar-container staggered-item" style={{ animationDelay: '0.2s' }}>
           <Search size={22} style={{ position: 'absolute', left: '26px', top: '50%', transform: 'translateY(-50%)', color: 'var(--accent-cyan)', opacity: 0.5 }} />
           <input 
              type="text" 
              className="command-input-ultra" 
              placeholder="SEARCH_LATENT_SPACE_"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
           />
           <div style={{ position: 'absolute', right: '28px', top: '50%', transform: 'translateY(-50%)' }}>
              <Command size={18} color="var(--text-secondary)" opacity={0.3} />
           </div>
        </form>

        {(results.length > 0 || loading) && (
          <div className="staggered-item" style={{ animationDelay: '0.3s' }}>
            <table className="tech-table">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>ID</th>
                  <th style={{ textAlign: 'left' }}>METADATA</th>
                  <th style={{ textAlign: 'left' }}>SENTIMENT</th>
                  <th style={{ textAlign: 'left' }}>DURATION</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="4" style={{ textAlign: 'center', padding: '100px', color: 'var(--text-secondary)', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>CALIBRATING_SENSORS...</td>
                  </tr>
                ) : (
                  results.map((track, i) => (
                    <tr key={i} className="tech-row">
                      <td className="tech-cell" style={{ textAlign: 'center', color: '#444', fontSize: '10px' }}>{i + 1}</td>
                      <td className="tech-cell">
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                           <span style={{ fontWeight: 700, fontSize: '16px', letterSpacing: '-0.01em' }}>{track.track_name}</span>
                           <span style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>{track.artist_name || track.artists}</span>
                        </div>
                      </td>
                      <td className="tech-cell">
                         <span className="mono-val">
                           {((track.search_score || track.popularity || 0) / 10).toFixed(4)}
                         </span>
                      </td>
                      <td className="tech-cell">
                         <span className="mono-val" style={{ opacity: 0.6 }}>
                            {msToMinSec(track.duration_ms)}
                         </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        <div className="staggered-item" style={{ marginTop: '80px', textAlign: 'center', animationDelay: '0.4s' }}>
           <button className="btn-secondary-pill" onClick={() => navigate('/')}>
              <ArrowLeft size={16} /> Return to Home
           </button>
        </div>
      </div>
    </div>
  )
}

export default Discovery
