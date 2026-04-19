import { useState } from 'react'
import BorrowerIntake from './components/BorrowerIntake'
import LenderDashboard from './components/LenderDashboard'
import './index.css'

function App() {
  const [profile, setProfile] = useState(null)

  const handleStartScoring = (data) => {
    setProfile(data)
  }

  const handleReset = () => {
    setProfile(null)
  }

  return (
    <>
      <h1 style={{ background: '-webkit-linear-gradient(#3b82f6, #9333ea)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '2.5rem', marginBottom: '0.5rem' }}>
        CreditPulse
      </h1>
      <p style={{ color: '#94a3b8', marginBottom: '2rem' }}>AI-Powered Alternative Credit Scoring Engine</p>
      
      {!profile ? (
        <BorrowerIntake onSubmit={handleStartScoring} />
      ) : (
        <LenderDashboard profile={profile} onReset={handleReset} />
      )}
    </>
  )
}

export default App
