import { useState } from 'react'
import { Sparkles, Activity, Clock, Hash, Wind, Sun, Moon, Zap, Smile } from 'lucide-react'
import Navbar from './Navbar'

function MoodMatrix() {
  const [context, setContext] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const vibes = [
    { label: 'Gym', icon: <Zap size={16}/>, color: '#FF6B6B' },
    { label: 'Focus', icon: <Activity size={16}/>, color: '#7ED6A4' },
    { label: 'Chill', icon: <Wind size={16}/>, color: '#6EC6FF' },
    { label: 'Morning', icon: <Sun size={16}/>, color: '#FFD700' },
    { label: 'Late Night', icon: <Moon size={16}/>, color: '#9B8EC2' },
    { label: 'Romantic', icon: <Smile size={16}/>, color: '#FFB4D4' },
  ]

  const handleMoodSearch = async (val) => {
    const searchVal = val || context
    if (!searchVal) return
    setLoading(true)
    try {
      const res = await fetch('/api/recommend/mood', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context: searchVal, n: 12 })
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
        <div className="technical-header">
           <div className="logo-text-ultra" style={{ fontSize: '9px', marginBottom: '8px', color: 'var(--accent-magenta)' }}>SYSTEM_MODULE / MOOD_RESOLVER</div>
           <h2 style={{ fontSize: '36px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Mood Matrix</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginTop: '8px' }}>
              Semantic context resolution via behavioral latent embeddings.
           </p>
        </div>

        <div className="command-bar-container">
           <Sparkles size={22} style={{ position: 'absolute', left: '26px', top: '50%', transform: 'translateY(-50%)', color: 'var(--accent-magenta)', opacity: 0.5 }} />
           <input 
              type="text" 
              className="command-input-ultra" 
              placeholder="ENTER VIBE OR CONTEXT_"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleMoodSearch()}
           />
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', marginBottom: '60px' }}>
          {vibes.map(v => (
            <button 
              key={v.label} 
              className="btn-secondary-pill" 
              style={{ borderColor: v.color + '33' }}
              onClick={() => { setContext(v.label); handleMoodSearch(v.label); }}
            >
              <span style={{ color: v.color }}>{v.icon}</span>
              {v.label}
            </button>
          ))}
        </div>

        {(results.length > 0 || loading) && (
          <table className="tech-table">
            <thead>
              <tr>
                <th style={{width: '60px'}}>ID</th>
                <th style={{textAlign: 'left'}}>METADATA</th>
                <th style={{textAlign: 'left'}}>SENTIMENT</th>
                <th style={{textAlign: 'left'}}>DURATION</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                   <td colSpan="4" style={{ textAlign: 'center', padding: '80px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>RESOLVING_CONTEXTUAL_CLUSTERS...</td>
                </tr>
              ) : (
                results.map((track, i) => (
                  <tr key={i} className="tech-row">
                    <td className="tech-cell" style={{ textAlign: 'center', color: '#444', fontSize: '10px' }}>{i + 1}</td>
                    <td className="tech-cell">
                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                         <span style={{ fontWeight: 700, fontSize: '16px' }}>{track.track_name}</span>
                         <span style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>{track.artist_name}</span>
                      </div>
                    </td>
                    <td className="tech-cell">
                       <span className="mono-val">
                         {(track.hybrid_score || 0).toFixed(4)}
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
        )}
      </div>
    </div>
  )
}

export default MoodMatrix
