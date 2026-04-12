import { Link } from 'react-router-dom'
import { Sparkle } from 'lucide-react'

function Navbar() {
  return (
    <div className="navbar-pill-wrapper">
      <nav className="navbar-pill">
        <Link to="/" className="nav-logo-link">
          <Sparkle size={18} color="var(--accent-cyan)" />
          <span className="logo-text-ultra" style={{ marginRight: '20px' }}>S O N I C S E N S E</span>
        </Link>
        
        <div style={{ width: '1px', height: '20px', background: 'var(--glass-border)' }}></div>
        
        <div className="nav-links-pill">
          <Link to="/discover" className="nav-link-pill">Discover</Link>
          <Link to="/mixes" className="nav-link-pill">Mixes</Link>
          <Link to="/mood" className="nav-link-pill">Mood</Link>
          <Link to="/map" className="nav-link-pill">Map</Link>
          <Link to="/diagnostics" className="nav-link-pill">Studio</Link>
        </div>
      </nav>
    </div>
  )
}

export default Navbar
