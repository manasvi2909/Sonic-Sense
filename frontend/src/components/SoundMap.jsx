import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import { Map as MapIcon, Loader2, Info, Navigation, ArrowLeft, Target } from 'lucide-react'
import Navbar from './Navbar'
import { useNavigate } from 'react-router-dom'

function SoundMap() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [hoveredTrack, setHoveredTrack] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetch('/api/map')
      .then(res => res.json())
      .then(res => {
        if (res.points) {
          const moodGroups = {}
          res.points.forEach(p => {
            if (!moodGroups[p.mood]) moodGroups[p.mood] = { x: [], y: [], text: [], artist: [], mood: p.mood }
            moodGroups[p.mood].x.push(p.x)
            moodGroups[p.mood].y.push(p.y)
            moodGroups[p.mood].text.push(p.track_name)
            moodGroups[p.mood].artist.push(p.artist_name)
          })
          setData(Object.values(moodGroups))
        }
      })
      .catch(err => console.error("Error fetching map data", err))
      .finally(() => setLoading(false))
  }, [])

  const moodColors = {
    "Chill": "#6EC6FF",
    "Energetic": "#FF6B6B",
    "Romantic": "#FFB4D4",
    "Melancholic": "#9B8EC2",
    "Focus": "#7ED6A4"
  }

  const handleHover = (event) => {
    if (event.points && event.points[0]) {
      const p = event.points[0]
      // Use customdata for reliable metadata capture in Plotly
      setHoveredTrack({
        name: p.text,
        artist: p.customdata,
        mood: p.data.name
      })
    }
  }

  return (
    <div className="dashboard-root">
      <Navbar />

      <div className="inner-container">
        <div className="technical-header">
           <div className="logo-text-ultra" style={{ fontSize: '10px', marginBottom: '12px', color: 'var(--accent-cyan)', letterSpacing: '0.2em' }}>
             SPATIAL_PROJECTION / GENRE_LATENTS
           </div>
           <h2 style={{ fontSize: '48px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Sound Map</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '16px', marginTop: '12px', maxWidth: '600px' }}>
              Dimensionality reduction of high-dimensional audio features via PCA plotting.
           </p>
        </div>

        <div className="split-pane-layout">
          {/* TELEMETRY PANE */}
          <div className="pane-source">
            <div className="glass-pane-inner">
               <div style={{ marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--accent-cyan)' }}>
                 <Navigation size={18} />
                 <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', letterSpacing: '0.15em' }}>MAP_TELEMETRY_</span>
               </div>

               {hoveredTrack ? (
                 <div className="reveal-up">
                    <div style={{ padding: '24px', background: 'rgba(255,255,255,0.02)', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.05)' }}>
                       <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>SCANNING_FOCAL_POINT</div>
                       <h3 style={{ fontSize: '20px', marginBottom: '4px' }}>{hoveredTrack.name}</h3>
                       <p style={{ color: 'var(--accent-cyan)', fontSize: '14px', marginBottom: '16px' }}>{hoveredTrack.artist}</p>
                       <div style={{ display: 'inline-flex', padding: '6px 12px', borderRadius: '100px', background: moodColors[hoveredTrack.mood] + '22', color: moodColors[hoveredTrack.mood], fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                         CLUSTER: {hoveredTrack.mood.toUpperCase()}
                       </div>
                    </div>
                 </div>
               ) : (
                 <div style={{ padding: '60px 20px', textAlign: 'center', opacity: 0.2 }}>
                    <Target size={32} style={{ margin: '0 auto 16px' }} />
                    <p style={{ fontSize: '12px', fontFamily: 'var(--font-mono)' }}>HOVER_VECTOR_TO_SCAN_</p>
                 </div>
               )}

               <div style={{ marginTop: '40px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '32px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: 'rgba(255,255,255,0.4)' }}>
                    <Info size={14} /> <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>PROJECTION_STATS</span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                     <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '12px' }}>
                        <div style={{ fontSize: '9px', opacity: 0.4, marginBottom: '4px' }}>DIMENSIONS</div>
                        <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--accent-cyan)' }}>9D → 2D</div>
                     </div>
                     <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '12px' }}>
                        <div style={{ fontSize: '9px', opacity: 0.4, marginBottom: '4px' }}>SAMPLE_SIZE</div>
                        <div style={{ fontSize: '16px', fontWeight: 600 }}>5,000 Pts</div>
                     </div>
                  </div>
               </div>
            </div>
          </div>

          {/* MAP PANE */}
          <div className="pane-projection">
            <div className="glass-pane-inner" style={{ padding: '0', position: 'relative', overflow: 'hidden', height: '600px' }}>
               <div className="abstract-grid-plane" style={{ opacity: 0.1 }}></div>
               {loading ? (
                 <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                   <Loader2 className="animate-spin" size={32} color="var(--accent-cyan)" />
                   <p style={{ marginTop: '20px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>PROJECTING_VECTORS...</p>
                 </div>
               ) : (
                 <Plot
                   data={data?.map(g => ({
                     x: g.x,
                     y: g.y,
                     text: g.text,
                     customdata: g.artist,
                     mode: 'markers',
                     name: g.mood,
                     marker: { size: 6, color: moodColors[g.mood] || '#555', opacity: 0.6, line: { width: 0 } },
                     hovertemplate: '<b>%{text}</b><extra></extra>'
                   })) || []}
                   onHover={handleHover}
                   onUnhover={() => setHoveredTrack(null)}
                   layout={{
                     autosize: true,
                     paper_bgcolor: 'rgba(0,0,0,0)',
                     plot_bgcolor: 'rgba(0,0,0,0)',
                     margin: { l: 40, r: 40, b: 40, t: 40 },
                     showlegend: true,
                     legend: { font: { color: 'rgba(255,255,255,0.6)', family: 'var(--font-mono)', size: 10 }, bgcolor: 'rgba(0,0,0,0.3)', x: 0, y: 1 },
                     xaxis: { showgrid: false, zeroline: false, showticklabels: false, range: [-15, 15] },
                     yaxis: { showgrid: false, zeroline: false, showticklabels: false, range: [-15, 15] },
                     hovermode: 'closest',
                     dragmode: 'pan'
                   }}
                   config={{ displayModeBar: false, responsive: true }}
                   style={{ width: '100%', height: '100%' }}
                 />
               )}
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

export default SoundMap
