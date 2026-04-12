import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { BrainCircuit, Users, Activity, ArrowLeft, Disc, Sparkles, ChevronRight, BarChart3, Database } from 'lucide-react'
import Navbar from './Navbar'

function Mixes() {
  const [users, setUsers] = useState([])
  const [selectedUserId, setSelectedUserId] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(data => {
        setUsers(data.users)
        if (data.users.length > 0) {
          const firstUser = data.users[0]
          setSelectedUserId(firstUser.user_id)
          setSelectedUser(firstUser)
        }
      })
      .catch(err => console.error("Error fetching users", err))
  }, [])

  const handleUserSelect = (userId) => {
    setSelectedUserId(userId)
    const user = users.find(u => u.user_id === userId)
    setSelectedUser(user)
    setResults([]) // Clear previous results
  }

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

  return (
    <div className="dashboard-root">
      <Navbar />
      
      <div className="inner-container">
        {/* HEADER AREA */}
        <div className="technical-header">
           <div className="logo-text-ultra" style={{ fontSize: '10px', marginBottom: '12px', color: 'var(--accent-indigo)', letterSpacing: '0.2em' }}>
             USER_MODEL / BEHAVIORAL_CENTROIDS
           </div>
           <h2 style={{ fontSize: '48px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Personal Mixes</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '16px', marginTop: '12px', maxWidth: '600px' }}>
             Synthesize unique listening trajectories using recency-decay behavioral modeling.
           </p>
        </div>

        <div className="split-pane-layout">
          {/* PROFILE SELECTION PANE */}
          <div className="pane-source">
            <div className="glass-pane-inner">
              <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Users size={18} color="var(--accent-indigo)" />
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', letterSpacing: '0.1em' }}>SELECT_PROFILE_</span>
              </div>
              
              <div className="sleek-list" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {users.map(u => (
                  <div 
                    key={u.user_id} 
                    className={`sleek-item ${selectedUserId === u.user_id ? 'active' : ''}`}
                    onClick={() => handleUserSelect(u.user_id)}
                    style={selectedUserId === u.user_id ? { borderColor: 'var(--accent-indigo)', background: 'rgba(99, 102, 241, 0.08)' } : {}}
                  >
                    <div className="sleek-item-meta">
                      <span className="sleek-item-title">{u.user_id}</span>
                      <span className="sleek-item-subtitle">{u.preferred_mood.toUpperCase()} PREFERENCE</span>
                    </div>
                    <div className="sleek-item-stat" style={{ color: 'var(--accent-indigo)' }}>
                      {u.track_count} TKS
                    </div>
                  </div>
                ))}
              </div>

              {selectedUser && (
                <div style={{ marginTop: '32px', padding: '24px', background: 'rgba(99, 102, 241, 0.03)', borderRadius: '16px', border: '1px solid rgba(99, 102, 241, 0.1)' }}>
                  <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--accent-indigo)' }}>
                    <BarChart3 size={14} /> PROFILE_INSIGHTS
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div>
                      <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)', marginBottom: '4px' }}>LATENT_FOCUS</div>
                      <div style={{ fontSize: '14px', fontWeight: 600 }}>{selectedUser.preferred_mood}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)', marginBottom: '4px' }}>VECTOR_DEPTH</div>
                      <div style={{ fontSize: '14px', fontWeight: 600 }}>{selectedUser.track_count} Hits</div>
                    </div>
                  </div>
                  <button 
                    className="btn-premium" 
                    onClick={generateMix} 
                    disabled={loading}
                    style={{ width: '100%', marginTop: '24px', background: 'var(--accent-indigo)', borderColor: 'var(--accent-indigo)' }}
                  >
                    <BrainCircuit size={18} />
                    {loading ? "CALCULATING..." : "GENERATE_VECTORS"}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* MIX GENERATION PANE */}
          <div className="pane-projection">
             {results.length > 0 ? (
               <div className="reveal-up">
                 <div style={{ marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div className="logo-text-ultra" style={{ fontSize: '11px', color: 'var(--accent-indigo)' }}>BEHAVIORAL_RESONANCE_SCAN</div>
                    <div style={{ height: '1px', flex: 1, background: 'linear-gradient(90deg, var(--accent-indigo), transparent)', opacity: 0.2 }}></div>
                 </div>

                 <div className="sleek-list" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    {results.map((track, i) => (
                      <div key={i} className="sleek-item" style={{ animationDelay: `${i * 0.05}s`, background: 'rgba(255,255,255,0.01)' }}>
                        <div className="sleek-item-meta">
                          <span className="sleek-item-title" style={{ fontSize: '16px' }}>{track.track_name}</span>
                          <span className="sleek-item-subtitle">{track.artist_name}</span>
                        </div>
                        <div className="viz-container" style={{ width: '50px', height: '30px', marginBottom: '0', marginLeft: '12px' }}>
                           <div className="viz-bar" style={{ height: `${20 + Math.random() * 80}%`, background: 'var(--accent-indigo)' }}></div>
                           <div className="viz-bar" style={{ height: `${20 + Math.random() * 80}%`, background: 'var(--accent-indigo)' }}></div>
                           <div className="viz-bar" style={{ height: `${20 + Math.random() * 80}%`, background: 'var(--accent-indigo)' }}></div>
                        </div>
                      </div>
                    ))}
                 </div>
               </div>
             ) : (
               <div className="glass-pane-inner" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.2, borderStyle: 'dashed' }}>
                  <Database size={48} style={{ marginBottom: '24px' }} />
                  <p style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>AWAITING_TRAJECTORY_CALCULATION</p>
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

export default Mixes
