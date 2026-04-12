import { useState, useEffect } from 'react'
import { BrainCircuit, Users, Activity, Clock, Hash } from 'lucide-react'
import Navbar from './Navbar'

function Mixes() {
  const [users, setUsers] = useState([])
  const [selectedUserId, setSelectedUserId] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(data => {
        setUsers(data.users)
        if (data.users.length > 0) {
          setSelectedUserId(data.users[0].user_id)
        }
      })
      .catch(err => console.error("Error fetching users", err))
  }, [])

  const generateMix = async () => {
    if (!selectedUserId) return
    setLoading(true)
    try {
      const res = await fetch('/api/recommend/user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: selectedUserId, n: 12 })
      })
      const data = await res.json()
      if (data.results) {
        setResults(data.results)
      }
    } catch (err) {
      console.error("Error generating mix", err)
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
           <div className="logo-text-ultra" style={{ fontSize: '9px', marginBottom: '8px', color: 'var(--accent-indigo)' }}>USER_MODEL / BEHAVIORAL_CENTROIDS</div>
           <h2 style={{ fontSize: '36px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Personal Mixes</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginTop: '8px' }}>
              Recency-weighted modeling of individual listening trajectories.
           </p>
        </div>

        <div style={{ display: 'flex', gap: '20px', marginBottom: '60px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px', display: 'block' }}>
              Select Behavioral Profile
            </label>
            <select 
              value={selectedUserId} 
              onChange={(e) => setSelectedUserId(e.target.value)}
              className="command-input-ultra"
              style={{ padding: '12px 24px', fontSize: '15px' }}
            >
              <option value="" disabled>SELECT_USER_ID_</option>
              {users.map(u => (
                <option key={u.user_id} value={u.user_id}>
                  {u.user_id} ({u.preferred_mood}) — {u.track_count} TKS
                </option>
              ))}
            </select>
          </div>
          <button className="btn-premium" onClick={generateMix} disabled={loading} style={{ height: '48px' }}>
            <BrainCircuit size={18} />
            {loading ? "PROCESSING..." : "GENERATE MIX"}
          </button>
        </div>

        {(results.length > 0 || loading) && (
          <table className="tech-table">
            <thead>
              <tr>
                <th style={{width: '60px'}}>ID</th>
                <th style={{textAlign: 'left'}}>METADATA</th>
                <th style={{textAlign: 'left'}}>PERSONAL_SCORE</th>
                <th style={{textAlign: 'left'}}>DURATION</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                   <td colSpan="4" style={{ textAlign: 'center', padding: '80px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>CALIBRATING_VECTORS...</td>
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

export default Mixes
