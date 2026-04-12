import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import { Map as MapIcon, Loader2 } from 'lucide-react'
import Navbar from './Navbar'

function SoundMap() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/map')
      .then(res => res.json())
      .then(res => {
        if (res.points) {
          const moodGroups = {}
          res.points.forEach(p => {
            if (!moodGroups[p.mood]) moodGroups[p.mood] = { x: [], y: [], text: [], mood: p.mood }
            moodGroups[p.mood].x.push(p.x)
            moodGroups[p.mood].y.push(p.y)
            moodGroups[p.mood].text.push(`${p.track_name} - ${p.artist_name}`)
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

  return (
    <div className="reveal-up">
      <Navbar />

      <div className="dashboard-container section-wrapper">
        <div className="technical-header">
           <div className="logo-text-ultra" style={{ fontSize: '9px', marginBottom: '8px', color: 'var(--accent-cyan)' }}>SPATIAL_PROJECTION / GENRE_LATENTS</div>
           <h2 style={{ fontSize: '36px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Sound Map</h2>
           <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginTop: '8px' }}>
              Dimensionality reduction of high-dimensional audio features via PCA.
           </p>
        </div>

        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
            <Loader2 className="animate-spin" size={32} color="var(--accent-cyan)" />
            <p style={{ marginTop: '20px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>PROJECTING_VECTORS_ON_PLANE...</p>
          </div>
        ) : (
          <div className="glass-panel" style={{ padding: '20px', display: 'flex', justifyContent: 'center', overflow: 'hidden' }}>
            <Plot
              data={data?.map(g => ({
                x: g.x,
                y: g.y,
                text: g.text,
                mode: 'markers',
                name: g.mood,
                marker: { size: 4, color: moodColors[g.mood] || '#555', opacity: 0.7 },
                hovertemplate: '<b>%{text}</b><extra></extra>'
              })) || []}
              layout={{
                width: 1100,
                height: 700,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: { l: 0, r: 0, b: 0, t: 0 },
                showlegend: true,
                legend: { font: { color: '#ededed', family: 'var(--font-mono)', size: 10 }, bgcolor: 'rgba(0,0,0,0.5)' },
                xaxis: { showgrid: false, zeroline: false, showticklabels: false },
                yaxis: { showgrid: false, zeroline: false, showticklabels: false },
                hovermode: 'closest'
              }}
              config={{ displayModeBar: false }}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default SoundMap
