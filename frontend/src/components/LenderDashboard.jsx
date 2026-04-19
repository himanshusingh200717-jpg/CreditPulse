import { useState, useEffect } from 'react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer 
} from 'recharts';
import { Download, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';

export default function LenderDashboard({ profile, onReset }) {
  const [loading, setLoading] = useState(true);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    let timer;
    if (loading) {
      timer = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [loading]);

  useEffect(() => {
    const fetchScore = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/score`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(profile)
        });
        
        if (!response.ok) throw new Error("Failed to fetch score");
        
        const data = await response.json();
        setResult(data.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchScore();
  }, [profile]);

  if (error) {
    return (
      <div className="card">
        <h2 style={{ color: '#ef4444' }}>Error</h2>
        <p>{error}</p>
        <button onClick={onReset}>Go Back</button>
      </div>
    );
  }

  const handleExportPdf = async () => {
    if (!result) return;
    setIsExporting(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          borrower_name: profile.name,
          profession: profile.profession,
          score_data: result
        })
      });
      
      if (!response.ok) throw new Error("Export failed");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CreditPulse_${profile.name.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF Export error:", err);
      alert("Failed to export PDF.");
    } finally {
      setIsExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h2>Orchestrating AI Agents...</h2>
        <div className="timer">{timeElapsed}s / 90s max</div>
        <div className="loading-spinner"></div>
        <div style={{ textAlign: 'left', marginTop: '2rem' }}>
          <p>📡 Contacting UPI Agent...</p>
          {timeElapsed > 1 && <p>📡 Contacting GST Agent...</p>}
          {timeElapsed > 2 && <p>📡 Contacting Rent Agent...</p>}
          {timeElapsed > 3 && <p>📡 Contacting Social / Employment Agent...</p>}
        </div>
      </div>
    );
  }

  const { agent_outputs, conflict_resolution, credit_score } = result;

  const chartData = [
    { subject: 'Income (UPI/GST)', A: (conflict_resolution.reconciled_income / 100000) * 100, fullMark: 100 },
    { subject: 'Stability (Rent)', A: agent_outputs.rent.stability_score * 10, fullMark: 100 },
    { subject: 'Job/Social', A: agent_outputs.social.job_stability * 10, fullMark: 100 },
    { subject: 'Compliance (GST)', A: agent_outputs.gst.compliance_score * 10, fullMark: 100 },
    { subject: 'Discipline (UPI)', A: agent_outputs.upi.spending_discipline * 10, fullMark: 100 },
  ];

  return (
    <div style={{ animation: 'fadeIn 0.5s ease' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Dashboard: {profile.name} ({profile.profession})</h2>
        <button onClick={onReset} style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)' }}>
          <RefreshCw size={16} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          New Evaluation
        </button>
      </div>

      <div className="dashboard-grid">
        {/* Score Card */}
        <div className="card score-display">
          <h3 style={{ margin: 0, color: '#a3b8cc' }}>CreditPulse Score</h3>
          <div className="score-value">{credit_score.score}</div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
            <span className="tier-badge" style={{ 
              color: credit_score.tier === 'A' || credit_score.tier === 'B' ? '#4ade80' : '#facc15',
              borderColor: credit_score.tier === 'A' || credit_score.tier === 'B' ? '#4ade80' : '#facc15',
              borderWidth: '1px', borderStyle: 'solid'
            }}>
              Tier {credit_score.tier}
            </span>
            <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>{timeElapsed}s execution</span>
          </div>
          <p style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>{credit_score.explanation_summary}</p>
          <div style={{ marginTop: 'auto', paddingTop: '1rem', width: '100%' }}>
             <button 
               onClick={handleExportPdf}
               disabled={isExporting}
               style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
             >
                <Download size={18} />
                {isExporting ? 'Generating PDF...' : 'Export PDF Report'}
             </button>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="card" style={{ height: '350px' }}>
          <h3 style={{ margin: '0 0 1rem 0' }}>Signal Breakdown</h3>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
              <PolarGrid stroke="rgba(255,255,255,0.2)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#a3b8cc', fontSize: 12 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar name="Borrower" dataKey="A" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.5} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Conflict Resolution */}
        <div className="card agent-output" style={{ gridColumn: '1 / -1' }}>
          <h3 style={{ color: '#c084fc', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} />
            Conflict Resolution Engine (XAI)
          </h3>
          <div className="conflict-log" style={{ background: conflict_resolution.conflict_detected ? 'rgba(239, 68, 68, 0.1)' : 'rgba(34, 197, 94, 0.1)', borderColor: conflict_resolution.conflict_detected ? 'rgba(239, 68, 68, 0.3)' : 'rgba(34, 197, 94, 0.3)' }}>
            <strong>{conflict_resolution.conflict_detected ? 'Conflict Detected & Reconciled' : 'No Major Conflicts'}</strong>
            <p style={{ margin: '0.5rem 0' }}>{conflict_resolution.reasoning}</p>
            <div style={{ display: 'flex', gap: '2rem', fontSize: '0.9rem', marginTop: '1rem', color: '#a3b8cc' }}>
              <span>Reliability Weight: <strong style={{ color: '#fff' }}>{conflict_resolution.reliability_weight}%</strong></span>
              <span>Reconciled Income: <strong style={{ color: '#fff' }}>₹{conflict_resolution.reconciled_income}</strong></span>
            </div>
          </div>
        </div>

        {/* Specialist Agents */}
        <div className="card agent-output">
          <h3>UPI Agent</h3>
          <p>Avg Income: ₹{agent_outputs.upi.average_income}</p>
          <p>Discipline: {agent_outputs.upi.spending_discipline}/10</p>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{agent_outputs.upi.explanation}</p>
        </div>
        <div className="card agent-output">
          <h3>GST Agent</h3>
          <p>Declared Rev: ₹{agent_outputs.gst.declared_revenue}</p>
          <p>Compliance: {agent_outputs.gst.compliance_score}/10</p>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{agent_outputs.gst.explanation}</p>
        </div>
        <div className="card agent-output">
          <h3>Rent Agent</h3>
          <p>Payment Streak: {agent_outputs.rent.payment_streak_months} months</p>
          <p>Stability: {agent_outputs.rent.stability_score}/10</p>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{agent_outputs.rent.explanation}</p>
        </div>
        <div className="card agent-output">
          <h3>Social / Employment Agent</h3>
          <p>Job Stability: {agent_outputs.social.job_stability}/10</p>
          <p>Network Credibility: {agent_outputs.social.professional_network_credibility}/10</p>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{agent_outputs.social.explanation}</p>
        </div>
      </div>
    </div>
  );
}
