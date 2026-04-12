import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Command, Activity, ArrowLeft, Disc, Sparkles, ChevronRight, Zap } from 'lucide-react'
import Navbar from './Navbar'

function Discovery() {
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [selectedTrack, setSelectedTrack] = useState(null)
  const [loadingSearch, setLoadingSearch] = useState(false)
  const [loadingRecs, setLoadingRecs] = useState(false)
  const [status, setStatus] = useState(null)
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
    
    setLoadingSearch(true)
    const res = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    })
    const data = await res.json()
    if (data.results) {
      setSearchResults(data.results)
    }
    setLoadingSearch(false)
  }

  const getRecommendations = async (track) => {
    setSelectedTrack(track)
    setLoadingRecs(true)
    try {
      const res = await fetch('/api/recommend/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ track_id: track.track_id, n: 12 })
      })
      const data = await res.json()
      if (data.results) {
        setRecommendations(data.results)
      }
    } catch (err) {
      console.error("Rec API Error", err)
    }
    setLoadingRecs(false)
  }

  return (
    <div className="dashboard-root">
      <Navbar />
      
      <div className="inner-container">
        {/* HEADER AREA */}
        <div className="technical-header staggered-item" style={{ animationDelay: '0.1s' }}>
           <div className="logo-text-ultra" style={{ fontSize: '10px', marginBottom: '12px', color: 'var(--accent-cyan)', letterSpacing: '0.2em' }}>
             SUBSYSTEM_ROOT // NEAREST_NEIGHBOR_SEARCH
           </div>
           <h2 style={{ fontSize: '48px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Discovery Engine</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '16px', marginTop: '12px', maxWidth: '600px' }}>
              Query the 1.2M+ latent vector space. Select a source focal point to project its nearest sonic neighbors.
           </p>
        </div>

        <div className="split-pane-layout">
          {/* SEARCH & SOURCE PANE */}
          <div className="pane-source">
            <form onSubmit={handleSearch} className="command-bar-container" style={{ marginBottom: '32px' }}>
               <Search size={20} style={{ position: 'absolute', left: '24px', top: '50%', transform: 'translateY(-50%)', color: 'var(--accent-cyan)', opacity: 0.6 }} />
               <input 
                  type="text" 
                  className="command-input-ultra" 
                  placeholder="SCAN_FOR_TRACK_"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  style={{ fontSize: '14px' }}
               />
               <div style={{ position: 'absolute', right: '24px', top: '50%', transform: 'translateY(-50%)' }}>
                  <Command size={16} color="var(--text-secondary)" opacity={0.4} />
               </div>
            </form>

            <div className="glass-pane-inner" style={{ padding: '0', overflow: 'hidden' }}>
              <div style={{ padding: '24px', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)', opacity: 0.6 }}>SEARCH_RESULTS // {searchResults.length}</span>
                {loadingSearch && <Activity size={14} className="animate-pulse" color="var(--accent-cyan)" />}
              </div>
              
              <div className="sleek-list" style={{ maxHeight: '500px', overflowY: 'auto', padding: '12px' }}>
                {searchResults.length === 0 && !loadingSearch && (
                  <div style={{ padding: '60px 20px', textAlign: 'center', opacity: 0.3 }}>
                    <Disc size={32} style={{ margin: '0 auto 16px' }} />
                    <p style={{ fontSize: '12px', fontFamily: 'var(--font-mono)' }}>WAITING_FOR_INPUT...</p>
                  </div>
                )}
                
                {searchResults.map((track, i) => (
                  <div 
                    key={i} 
                    className={`sleek-item ${selectedTrack?.track_id === track.track_id ? 'active' : ''}`}
                    onClick={() => getRecommendations(track)}
                  >
                    <div className="sleek-item-meta">
                      <span className="sleek-item-title">{track.track_name}</span>
                      <span className="sleek-item-subtitle">{track.artist_name}</span>
                    </div>
                    <ChevronRight size={16} opacity={0.3} />
                  </div>
                ))}
              </div>
            </div>
            
            {status && (
              <div style={{ marginTop: '24px', padding: '20px', background: 'rgba(0, 229, 255, 0.03)', borderRadius: '16px', border: '1px solid rgba(0, 229, 255, 0.1)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Zap size={14} color="var(--accent-cyan)" />
                  <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>ENGINE_ONLINE</span>
                </div>
                <div style={{ marginTop: '8px', fontSize: '13px', color: 'rgba(255,255,255,0.4)', lineHeight: '1.4' }}>
                   Mapping {status.catalog_size.toLocaleString()} audio vectors. Feature dimensionality: {status.feature_dim}.
                </div>
              </div>
            )}
          </div>

          {/* RECOMMENDATIONS PANE */}
          <div className="pane-projection">
             {selectedTrack ? (
               <div className="reveal-up">
                 <div style={{ marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div className="logo-text-ultra" style={{ fontSize: '11px', color: 'var(--accent-cyan)' }}>PROJECTION_TARGET_INSTALLED</div>
                    <div style={{ height: '1px', flex: 1, background: 'linear-gradient(90deg, var(--accent-cyan), transparent)', opacity: 0.2 }}></div>
                 </div>

                 <div className="glass-pane-inner" style={{ background: 'rgba(0, 229, 255, 0.03)', border: '1px solid rgba(0, 229, 255, 0.1)', marginBottom: '40px' }}>
                    <h3 style={{ fontSize: '24px', marginBottom: '8px' }}>{selectedTrack.track_name}</h3>
                    <p style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', fontSize: '14px' }}>BY {selectedTrack.artist_name.toUpperCase()}</p>
                 </div>

                 <div style={{ marginBottom: '24px', fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Sparkles size={14} color="var(--accent-magenta)" />
                    LATENT_NEIGHBORS // CALCULATED_RESULTS
                    {loadingRecs && <span className="animate-pulse ms-2">COMPUTING...</span>}
                 </div>

                 <div className="sleek-list" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    {recommendations.map((rec, i) => (
                      <div key={i} className="sleek-item" style={{ animationDelay: `${i * 0.05}s` }}>
                        <div className="sleek-item-meta">
                          <span className="sleek-item-title" style={{ fontSize: '16px' }}>{rec.track_name}</span>
                          <span className="sleek-item-subtitle">{rec.artist_name}</span>
                        </div>
                        <div className="sleek-item-stat">
                          {Math.round(rec.similarity * 100)}% MATCH
                        </div>
                      </div>
                    ))}
                 </div>
               </div>
             ) : (
               <div className="glass-pane-inner" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.2, borderStyle: 'dashed' }}>
                  <Activity size={48} style={{ marginBottom: '24px' }} />
                  <p style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>AWAITING_FOCAL_POINT_SELECTION</p>
               </div>
             )}
          </div>
        </div>

        <div style={{ marginTop: '100px', display: 'flex', justifyContent: 'center' }}>
           <button className="btn-secondary-pill" onClick={() => navigate('/')}>
              <ArrowLeft size={16} /> RETURN_TO_BASE
           </button>
        </div>
      </div>
    </div>
  )
}

export default Discovery
