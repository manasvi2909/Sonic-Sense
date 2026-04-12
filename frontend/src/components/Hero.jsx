import { useNavigate } from 'react-router-dom'
import { ArrowRight, Cpu, Target, AudioWaveform } from 'lucide-react'
import Navbar from './Navbar'

function Hero() {
  const navigate = useNavigate()

  return (
    <div className="reveal-up">
      <Navbar />
      
      {/* RESTORED PERFECT HEADER */}
      <section className="hero-container">
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

      {/* INTELLIGENCE MODULES (BENTO) */}
      <section className="section-wrapper staggered-item" style={{ animationDelay: '0.4s' }}>
        <h2 style={{ fontSize: '42px', marginBottom: '60px', letterSpacing: 'var(--tracking-tighter)', fontWeight: 800 }}>Intelligence Modules</h2>
        
        <div className="bento-grid-ultra">
          <div className="glass-panel bento-item item-large" onClick={() => navigate('/mixes')}>
            <div className="bento-content">
              <div>
                <Cpu size={32} color="var(--accent-indigo)" style={{marginBottom: '20px'}}/>
                <h3 style={{fontSize: '28px', marginBottom: '16px', fontWeight: 700}}>Behavioral Vectors</h3>
                <p style={{color: 'var(--text-secondary)', maxWidth: '400px', fontSize: '15.5px'}}>
                   Recency-decay projections mapping your unique sonic evolution across the global latent plane.
                </p>
              </div>
              <div className="logo-text-ultra" style={{fontSize: '9px', marginTop: '30px'}}>Access Core →</div>
            </div>
          </div>

          <div className="glass-panel bento-item item-medium" onClick={() => navigate('/mood')}>
            <div className="bento-content">
              <div>
                <Target size={32} color="var(--accent-magenta)" style={{marginBottom: '20px'}}/>
                <h3 style={{fontSize: '28px', marginBottom: '16px', fontWeight: 700}}>Mood Matrix</h3>
                <p style={{color: 'var(--text-secondary)', fontSize: '15.5px'}}>
                   Semantic context resolution via behavioral embeddings and cluster resolution.
                </p>
              </div>
              <div className="logo-text-ultra" style={{fontSize: '9px', marginTop: '30px'}}>Open Resolver →</div>
            </div>
          </div>

          <div className="glass-panel bento-item item-small" onClick={() => navigate('/map')}>
            <div className="bento-content">
               <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                  <AudioWaveform size={24} color="var(--accent-cyan)" />
                  <h3 style={{fontSize: '20px', fontWeight: 700}}>Sound Map</h3>
               </div>
               <p style={{fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '8px'}}>Visual PCA projection of 124K+ audio vectors on a 2D coordinate layer.</p>
            </div>
          </div>
          
          <div className="glass-panel bento-item item-small" onClick={() => navigate('/diagnostics')}>
            <div className="bento-content">
               <h3 style={{fontSize: '20px', fontWeight: 700}}>Diagnostics</h3>
               <p style={{fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '8px'}}>Real-time latency telemetry and precision scoring of the inference model.</p>
            </div>
          </div>
        </div>
      </section>

      <footer className="section-wrapper" style={{ textAlign: 'center', borderTop: '1px solid var(--glass-border)', opacity: 0.3, letterSpacing: '0.4em', fontSize: '10px' }}>
         &copy; 2026 SONICSENSE // QUANTUM SOUND INTELLIGENCE
      </footer>
    </div>
  )
}

export default Hero
