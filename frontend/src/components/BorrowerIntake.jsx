import { useState } from 'react';
import { FileText, Building, Landmark } from 'lucide-react';

export default function BorrowerIntake({ onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    profession: '',
    city: '',
    consent: false
  });
  const [files, setFiles] = useState({
    bankStatement: null,
    rentAgreement: null,
    gstInvoice: null
  });
  const [isUploading, setIsUploading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFileChange = (e, fileType) => {
    setFiles(prev => ({
      ...prev,
      [fileType]: e.target.files[0]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.consent) return;

    setIsUploading(true);
    let documentPaths = [];

    // Upload files
    const filesToUpload = [files.bankStatement, files.rentAgreement, files.gstInvoice].filter(Boolean);
    for (const file of filesToUpload) {
      const uploadData = new FormData();
      uploadData.append('file', file);
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/api/upload`, {
          method: 'POST',
          body: uploadData,
        });
        const result = await res.json();
        if (result.status === 'success') {
          documentPaths.push(result.file_path);
        }
      } catch (err) {
        console.error("Upload failed for", file?.name, err);
      }
    }

    setIsUploading(false);
    
    // Submit the form with document paths
    onSubmit({
      ...formData,
      document_paths: documentPaths
    });
  };

  return (
    <div className="card" style={{ maxWidth: '500px', margin: '0 auto' }}>
      <h2>Borrower Intake</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>Full Name</label>
          <input 
            type="text" 
            name="name" 
            value={formData.name} 
            onChange={handleChange} 
            required 
            placeholder="e.g. Rahul Kumar"
          />
        </div>
        
        <div className="input-group">
          <label>Age</label>
          <input 
            type="number" 
            name="age" 
            value={formData.age} 
            onChange={handleChange} 
            required 
            placeholder="e.g. 28"
          />
        </div>

        <div className="input-group">
          <label>Profession</label>
          <select name="profession" value={formData.profession} onChange={handleChange} required>
            <option value="" disabled>Select Profession</option>
            <option value="street vendor">Street Vendor</option>
            <option value="gig worker">Gig Worker</option>
            <option value="freelancer">Freelancer</option>
            <option value="small shop owner">Small Shop Owner</option>
            <option value="delivery partner">Delivery Partner</option>
          </select>
        </div>

        <div className="input-group">
          <label>City</label>
          <input 
            type="text" 
            name="city" 
            value={formData.city} 
            onChange={handleChange} 
            required 
            placeholder="e.g. Bangalore"
          />
        </div>

        <div style={{ padding: '1.5rem', border: '1px dashed rgba(255,255,255,0.2)', borderRadius: '8px', background: 'rgba(0,0,0,0.2)', marginBottom: '1rem' }}>
          <h3 style={{ marginTop: 0, marginBottom: '1rem', color: '#c084fc', fontSize: '1.1rem' }}>Mandatory Documents</h3>
          
          <div className="input-group" style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Landmark size={16} color="#4ade80" /> Bank Statement (PDF)
            </label>
            <input 
              type="file" 
              onChange={(e) => handleFileChange(e, 'bankStatement')} 
              style={{ marginTop: '0.5rem', background: 'transparent', padding: 0 }}
              accept=".pdf"
              required
            />
          </div>

          <div className="input-group" style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Building size={16} color="#60a5fa" /> Rent Agreement / Utility Bill (PDF)
            </label>
            <input 
              type="file" 
              onChange={(e) => handleFileChange(e, 'rentAgreement')} 
              style={{ marginTop: '0.5rem', background: 'transparent', padding: 0 }}
              accept=".pdf"
              required
            />
          </div>

          <div className="input-group" style={{ marginBottom: '0' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={16} color="#facc15" /> GST Invoice / Tax Return (PDF)
            </label>
            <input 
              type="file" 
              onChange={(e) => handleFileChange(e, 'gstInvoice')} 
              style={{ marginTop: '0.5rem', background: 'transparent', padding: 0 }}
              accept=".pdf"
              required
            />
          </div>
        </div>

        <div className="input-group" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input 
            type="checkbox" 
            name="consent" 
            id="consent"
            checked={formData.consent} 
            onChange={handleChange} 
            style={{ width: 'auto' }}
          />
          <label htmlFor="consent" style={{ margin: 0, fontSize: '0.9rem', fontWeight: 'normal' }}>
            I consent to the fetch and analysis of alternative data signals for credit assessment.
          </label>
        </div>

        <button type="submit" disabled={!formData.consent || isUploading} style={{ width: '100%', marginTop: '1rem' }}>
          {isUploading ? 'Uploading & Analyzing...' : 'Generate Credit Score'}
        </button>
      </form>
    </div>
  );
}
