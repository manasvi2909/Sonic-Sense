import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Navbar from './Navbar'

function Placeholder() {
  const navigate = useNavigate()
  const location = useLocation()
  
  const pathName = location.pathname.replace('/', '').toUpperCase()

  return (
    <div className="page-transition">
      <Navbar />
      <div className="dashboard-container">
        <div className="center-box">
          <Loader2 size={40} className="animate-spin" style={{ color: 'var(--accent-cyan)', marginBottom: '24px' }} />
          <h2 style={{ marginBottom: '16px', fontSize: '24px' }}>{pathName} OFFLINE</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', fontSize: '15px' }}>
            The {pathName} analytic module is currently undergoing high-dimensionality stabilization. 
            Check back after the next system epoch.
          </p>
          <button className="premium-btn" onClick={() => navigate('/')}>
            <ArrowLeft size={16} />
            Return to Command Center
          </button>
        </div>
      </div>
    </div>
  )
}

export default Placeholder
