import { useState } from 'react'
import { Sparkles, ArrowLeft, Disc, Zap, Activity, Wind, Sun, Moon, Smile, ChevronDown } from 'lucide-react'
import Navbar from './Navbar'
import { useNavigate } from 'react-router-dom'

function MoodMatrix() {
  const [context, setContext] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const vibes = [
    { label: 'Gym', icon: <Zap size={18}/>, color: '#FF6B6B' },
    { label: 'Focus', icon: <Activity size={18}/>, color: '#7ED6A4' },
    { label: 'Chill', icon: <Wind size={18}/>, color: '#6EC6FF' },
    { label: 'Morning', icon: <Sun size={18}/>, color: '#FFD700' },
    { label: 'Late Night', icon: <Moon size={18}/>, color: '#9B8EC2' },
    { label: 'Romantic', icon: <Smile size={18}/>, color: '#FFB4D4' },
  ]

  const handleMoodSearch = async (val) => {
    const searchVal = val || context
    if (!searchVal) return
    setLoading(true)
    try {
      const res = await fetch('/api/recommend/mood', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context: searchVal, n: 16 })
      })
      const data = await res.json()
      if (data.results) {
        setResults(data.results)
      }
    } catch (err) {
      console.error("Error fetching mood recs", err)
    }
    setLoading(false)
  }

  return (
    <div className="dashboard-root">
      <Navbar />

      <div className="inner-container">
        <div className="technical-header" style={{ textAlign: 'center' }}>
           <div className="logo-text-ultra" style={{ fontSize: '10px', marginBottom: '12px', color: 'var(--accent-magenta)', letterSpacing: '0.2em' }}>
             SYSTEM_MODULE / CONTEXTUAL_RESOLVER
           </div>
           <h2 style={{ fontSize: '56px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Mood Matrix</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '16px', marginTop: '12px', maxWidth: '600px', margin: '12px auto 0' }}>
              Project sonic sentiments by calculating relative distance between your vibe and the global behavioral latent plane.
           </p>
        </div>

        <div className="mood-orbit-container">
          {/* CENTRAL RADAR */}
          <div className="mood-radar-central">
            <div className="mood-radar-ping"></div>
            <div className="mood-radar-ping" style={{ animationDelay: '1s' }}></div>
            <div className="mood-radar-ping" style={{ animationDelay: '2s' }}></div>
            
            <div style={{ zIndex: 10, textAlign: 'center' }}>
               <form 
                 onSubmit={(e) => { e.preventDefault(); handleMoodSearch(); }}
                 className="command-bar-container" 
                 style={{ width: '380px', background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(20px)' }}
                >
                 <Sparkles size={20} style={{ position: 'absolute', left: '26px', top: '50%', transform: 'translateY(-50%)', color: 'var(--accent-magenta)', opacity: 0.6 }} />
                 <input 
                    type="text" 
                    className="command-input-ultra" 
                    placeholder="DEFINE_VIBE_"
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    style={{ fontSize: '14px', textAlign: 'center', paddingLeft: '50px' }}
                 />
               </form>

               <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginTop: '24px', flexWrap: 'wrap', maxWidth: '400px' }}>
                  {vibes.map(v => (
                    <button 
                      key={v.label} 
                      onClick={() => { setContext(v.label); handleMoodSearch(v.label); }}
                      style={{ 
                        background: 'rgba(255,255,255,0.03)', 
                        border: '1px solid rgba(255,255,255,0.08)',
                        borderRadius: '100px',
                        padding: '10px 18px',
                        color: 'var(--text-primary)',
                        fontSize: '12px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(255,255,255,0.08)';
                        e.currentTarget.style.borderColor = v.color;
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
                        e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)';
                      }}
                    >
                      <span style={{ color: v.color }}>{v.icon}</span>
                      {v.label}
                    </button>
                  ))}
               </div>
            </div>
          </div>
        </div>

        {/* RESULTS SECTION */}
        {(results.length > 0 || loading) && (
          <div className="reveal-up" style={{ marginTop: '40px' }}>
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
               <ChevronDown size={24} className="animate-bounce" opacity={0.3} />
               <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)', marginTop: '12px' }}>
                 {loading ? 'CALCULATING_CENTROIDS...' : 'RESOLVED_ORBITAL_HITS'}
               </p>
            </div>

            <div className="sleek-list" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
              {results.map((track, i) => (
                <div key={i} className="sleek-item" style={{ animationDelay: `${i * 0.05}s` }}>
                  <div className="sleek-item-meta">
                    <span className="sleek-item-title">{track.track_name}</span>
                    <span className="sleek-item-subtitle">{track.artist_name}</span>
                  </div>
                  <div className="sleek-item-stat" style={{ color: 'var(--accent-magenta)' }}>
                    {(track.hybrid_score || 0).toFixed(3)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ marginTop: '100px', textAlign: 'center' }}>
           <button className="btn-secondary-pill" onClick={() => navigate('/')}>
              <ArrowLeft size={16} /> RETURN_TO_BASE
           </button>
        </div>
      </div>
    </div>
  )
}

export default MoodMatrix
