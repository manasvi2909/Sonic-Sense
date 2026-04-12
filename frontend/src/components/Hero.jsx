import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Sparkles } from 'lucide-react'
import Navbar from './Navbar'

function Hero() {
  const navigate = useNavigate()
  const transitionRef = useRef(null)
  const bentoRef = useRef(null)
  const [lineVisible, setLineVisible] = useState(false)
  const [bentoVisible, setBentoVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        // Continuous Trigger Logic: Resets when off-screen
        if (entry.target.id === 'transition-trigger') {
          setLineVisible(entry.isIntersecting)
        }
        if (entry.target.id === 'bento-trigger') {
          setBentoVisible(entry.isIntersecting)
        }
      })
    }, { threshold: 0.15 })

    if (transitionRef.current) observer.observe(transitionRef.current)
    if (bentoRef.current) observer.observe(bentoRef.current)

    return () => observer.disconnect()
  }, [])

  return (
    <div className="reveal-up">
      <Navbar />
      
      <section className="hero-container">
        <div className="hero-caption-pill staggered-item" style={{ animationDelay: '0.05s', textTransform: 'none', letterSpacing: '0.02em', fontSize: '13px' }}>
          <Sparkles size={14} style={{ marginRight: '8px', color: 'var(--accent-cyan)' }} />
          Contextual mapping & advanced audio intelligence
        </div>
        
        <h1 className="hero-main-title text-shimmer-platinum staggered-item" style={{ animationDelay: '0.1s' }}>
           Intelligent<br/>
           <span className="text-gradient">Music Discovery.</span>
        </h1>
        <p className="hero-copy staggered-item" style={{ animationDelay: '0.2s', maxWidth: '800px', margin: '0 auto 48px' }}>
           SonicSense leverages high-dimensional latent space projections and context-aware resolution 
           to calibrate your listening experience with mathematical precision.
        </p>

        <div className="hero-actions staggered-item" style={{ animationDelay: '0.3s', display: 'flex', gap: '20px', justifyContent: 'center' }}>
          <button className="btn-premium" onClick={() => navigate('/discover')}>
            Initialize Engine <ArrowRight size={18} />
          </button>
          <button className="btn-secondary-pill">
            System Protocol
          </button>
        </div>
      </section>

      <div className="transition-container" ref={transitionRef} id="transition-trigger">
        <div className={`transition-line ${lineVisible ? 'start-grow' : ''}`}></div>
      </div>

      <section 
        className="section-wrapper" 
        style={{ 
          opacity: bentoVisible ? 1 : 0, 
          transform: bentoVisible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s cubic-bezier(0.16, 1, 0.3, 1)' 
        }}
        ref={bentoRef}
        id="bento-trigger"
      >
        <h2 style={{ fontSize: '42px', marginBottom: '80px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800, textAlign: 'center', opacity: 0.9 }}>Intelligence Architecture</h2>
        
        <div className="frameless-dash-container">
          
          {/* Frameless Pane 1: Behavior */}
          <div className="glass-pane-frameless" style={{ gridColumn: '1 / 9', cursor: 'pointer' }} onClick={() => navigate('/mixes')}>
            <div className="abstract-spectrum-huge">
               <div className="abstract-bar" style={{height: '10%'}}></div>
               <div className="abstract-bar" style={{height: '30%'}}></div>
               <div className="abstract-bar" style={{height: '80%'}}></div>
               <div className="abstract-bar" style={{height: '50%'}}></div>
               <div className="abstract-bar" style={{height: '100%'}}></div>
               <div className="abstract-bar" style={{height: '40%'}}></div>
               <div className="abstract-bar" style={{height: '70%'}}></div>
               <div className="abstract-bar" style={{height: '20%'}}></div>
            </div>
            <span className="dash-tag-floating">sys_module // vectors</span>
            <h3>Behavioral Vectors</h3>
            <p style={{ maxWidth: '420px' }}>
               Recency-decay projections mapping your unique sonic evolution across the global latent plane.
            </p>
          </div>

          {/* Frameless Pane 2: Mood */}
          <div className="glass-pane-frameless" style={{ gridColumn: '5 / 13', marginTop: '-100px', cursor: 'pointer' }} onClick={() => navigate('/mood')}>
            <div className="abstract-radar-huge"></div>
            <span className="dash-tag-floating" style={{ color: 'var(--accent-magenta)' }}>sys_cluster // mood</span>
            <h3>Mood Matrix</h3>
            <p style={{ maxWidth: '400px' }}>
               Semantic context resolution via behavioral embeddings and dynamic cluster bounding.
            </p>
          </div>

          {/* Frameless Pane 3: Sound Map */}
          <div className="glass-pane-frameless" style={{ gridColumn: '1 / 7', marginTop: '-60px', cursor: 'pointer' }} onClick={() => navigate('/map')}>
            <div className="abstract-grid-plane"></div>
            <div className="abstract-scatter-huge">
               <div className="scatter-dot dot-1"></div>
               <div className="scatter-dot dot-2"></div>
               <div className="scatter-dot dot-3"></div>
            </div>
            <span className="dash-tag-floating">core_projection // pca</span>
            <h3>Sound Map</h3>
            <p style={{ maxWidth: '350px' }}>
              Visual principal component analysis plotting 124K+ audio vectors on a 2D sensory plane.
            </p>
          </div>
          
          {/* Frameless Pane 4: Diagnostics */}
          <div className="glass-pane-frameless" style={{ gridColumn: '6 / 13', marginTop: '-160px', cursor: 'pointer' }} onClick={() => navigate('/diagnostics')}>
            <div className="abstract-telemetry-huge">
               <div className="telemetry-node node-start"></div>
               <div className="telemetry-pulse"></div>
               <div className="telemetry-node node-end"></div>
            </div>
            <span className="dash-tag-floating" style={{ color: 'var(--text-secondary)' }}>sys_status // telemetry</span>
            <h3>Diagnostics Core</h3>
            <p style={{ maxWidth: '350px' }}>
              Real-time latency telemetry and automated precision scoring of the inference models.
            </p>
          </div>
          
        </div>
      </section>

      <footer className="section-wrapper" style={{ textAlign: 'center', opacity: 0.8, letterSpacing: '0.4em', fontSize: '10px', paddingTop: '100px', color: 'var(--accent-cyan)', textShadow: '0 0 10px rgba(0, 229, 255, 0.4)' }}>
         &copy; 2026 SONICSENSE // QUANTUM SOUND INTELLIGENCE
      </footer>
    </div>
  )
}

export default Hero
