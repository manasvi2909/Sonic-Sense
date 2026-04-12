import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Hero from './components/Hero'
import Discovery from './components/Discovery'
import Mixes from './components/Mixes'
import MoodMatrix from './components/MoodMatrix'
import SoundMap from './components/SoundMap'
import DiagnosticsStudio from './components/DiagnosticsStudio'

function App() {
  return (
    <Router>
      <div className="app-bg-layers">
        <div className="mesh-bg"></div>
        <div className="glow-overlay"></div>
        <div className="grid-overlay"></div>
      </div>
      <Routes>
        <Route path="/" element={<Hero />} />
        <Route path="/discover" element={<Discovery />} />
        <Route path="/mixes" element={<Mixes />} />
        <Route path="/mood" element={<MoodMatrix />} />
        <Route path="/map" element={<SoundMap />} />
        <Route path="/diagnostics" element={<DiagnosticsStudio />} />
      </Routes>
    </Router>
  )
}

export default App
