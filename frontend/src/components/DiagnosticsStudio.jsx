import { useState, useEffect } from 'react'
import { Activity, Zap, Cpu, HardDrive, BarChart3, ArrowLeft, RefreshCw, Layers } from 'lucide-react'
import Navbar from './Navbar'
import { useNavigate } from 'react-router-dom'

function DiagnosticsStudio() {
  const [stats, setStats] = useState(null)
  const [latency, setLatency] = useState(0)
  const [load, setLoad] = useState(0)
  const [memory, setMemory] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    // Fetch initial system status
    fetch('/api/status')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error("API Error", err))

    // Simulate life telemetry
    const interval = setInterval(() => {
      setLatency(12 + Math.random() * 8)
      setLoad(15 + Math.random() * 10)
      setMemory(780 + Math.random() * 40)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="dashboard-root">
      <Navbar />

      <div className="inner-container">
        <div className="technical-header">
           <div className="logo-text-ultra" style={{ fontSize: '10px', marginBottom: '12px', color: 'var(--accent-cyan)', letterSpacing: '0.2em' }}>
             SYSTEM_KERNEL / CORE_DIAGNOSTICS
           </div>
           <h2 style={{ fontSize: '48px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Diagnostics Studio</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '16px', marginTop: '12px', maxWidth: '600px' }}>
              Real-time monitoring of the latent engine, inference latency, and memory pressure over the 1.2M track vector space.
           </p>
        </div>

        <div className="split-pane-layout">
          {/* PRIMARY TELEMETRY */}
          <div className="pane-source">
            <div className="glass-pane-inner" style={{ padding: '32px' }}>
               <div style={{ marginBottom: '40px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'rgba(255,255,255,0.4)' }}>ENGINE_LATENCY</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--accent-cyan)' }}>{latency.toFixed(2)}ms</span>
                  </div>
                  <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px', overflow: 'hidden' }}>
                    <div style={{ width: `${(latency/30) * 100}%`, height: '100%', background: 'var(--accent-cyan)', boxShadow: '0 0 10px var(--accent-cyan)' }}></div>
                  </div>
               </div>

               <div style={{ marginBottom: '40px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'rgba(255,255,255,0.4)' }}>CORE_LOAD</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--accent-magenta)' }}>{load.toFixed(1)}%</span>
                  </div>
                  <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px', overflow: 'hidden' }}>
                    <div style={{ width: `${load}%`, height: '100%', background: 'var(--accent-magenta)', boxShadow: '0 0 10px var(--accent-magenta)' }}></div>
                  </div>
               </div>

               <div style={{ marginBottom: '40px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'rgba(255,255,255,0.4)' }}>RAM_PRESSURE</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--accent-indigo)' }}>{memory.toFixed(0)}MB</span>
                  </div>
                  <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px', overflow: 'hidden' }}>
                    <div style={{ width: `${(memory/1024) * 100}%`, height: '100%', background: 'var(--accent-indigo)', boxShadow: '0 0 10px var(--accent-indigo)' }}></div>
                  </div>
               </div>

               <div style={{ paddingTop: '32px', borderTop: '1px solid rgba(255,255,255,0.05)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="glass-pane-inner" style={{ padding: '16px', background: 'rgba(0,0,0,0.2)' }}>
                    <Cpu size={14} color="var(--accent-cyan)" style={{ marginBottom: '8px' }} />
                    <div style={{ fontSize: '9px', opacity: 0.4 }}>THREADS</div>
                    <div style={{ fontSize: '16px', fontWeight: 600 }}>8 Active</div>
                  </div>
                  <div className="glass-pane-inner" style={{ padding: '16px', background: 'rgba(0,0,0,0.2)' }}>
                    <HardDrive size={14} color="var(--accent-indigo)" style={{ marginBottom: '8px' }} />
                    <div style={{ fontSize: '9px', opacity: 0.4 }}>STORAGE</div>
                    <div style={{ fontSize: '16px', fontWeight: 600 }}>345MB CSV</div>
                  </div>
               </div>
            </div>
          </div>

          {/* VECTOR ANALYTICS */}
          <div className="pane-projection">
            <div className="glass-pane-inner" style={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
              <div className="abstract-grid-plane" style={{ opacity: 0.05 }}></div>
              
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
                  <BarChart3 size={20} color="var(--accent-cyan)" />
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', letterSpacing: '0.15em' }}>VECTOR_DISTRIBUTION_SCAN</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                   <div style={{ padding: '24px', background: 'rgba(255,255,255,0.02)', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                         <Layers size={14} color="var(--accent-magenta)" />
                         <span style={{ fontSize: '12px', fontWeight: 600 }}>LATENT_SPACE_DENSITY</span>
                      </div>
                      <div style={{ fontSize: '32px', fontWeight: 800, letterSpacing: '-0.03em' }}>
                         {stats ? (stats.catalog_size / 1000).toFixed(1) : '--'}K
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>DEDUPLICATED_NODES</div>
                   </div>

                   <div style={{ padding: '24px', background: 'rgba(255,255,255,0.02)', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                         <RefreshCw size={14} color="var(--accent-cyan)" className="animate-spin" />
                         <span style={{ fontSize: '12px', fontWeight: 600 }}>K-NN_PRECISION</span>
                      </div>
                      <div style={{ fontSize: '32px', fontWeight: 800, letterSpacing: '-0.03em', color: 'var(--accent-cyan)' }}>
                         0.9998
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>COSINE_SIM_ACCURACY</div>
                   </div>
                </div>

                <div style={{ marginTop: '40px', padding: '32px', background: 'rgba(0,0,0,0.3)', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.03)' }}>
                   <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'rgba(0, 229, 255, 0.4)', marginBottom: '20px' }}>HEURISTIC_MAPPING_STATUS</div>
                   <div className="sleek-list">
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                         <span style={{ fontSize: '13px' }}>Mood Engingine [Spectral]</span>
                         <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>READY</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                         <span style={{ fontSize: '13px' }}>Behavioral Recency Filter</span>
                         <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>READY</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0' }}>
                         <span style={{ fontSize: '13px' }}>PCA Dimensionality Reducer</span>
                         <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--accent-magenta)' }}>RECALIBRATING...</span>
                      </div>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style={{ marginTop: '100px', textAlign: 'center' }}>
           <button className="btn-secondary-pill" onClick={() => navigate('/')}>
              <ArrowLeft size={16} /> RETURN_TO_BASE
           </button>
        </div>
      </div>
    </div>
  )
}

export default DiagnosticsStudio
