import { useEffect, useState } from "react";

const API = import.meta.env.import.meta.env.VITE_API_BASE_URL;

export default function App() {
  const [formData, setFormData] = useState({
    state: "",
    district: "",
    market: "",
    commodity: "",
    variety: "",
    grade: "",
    date: "",
  });

  const [options, setOptions] = useState({
    states: [],
    districts: [],
    markets: [],
    commodities: [],
    varieties: [],
    grades: [],
  });

  const [prediction, setPrediction] = useState(null);
  const [pricePerKg, setPricePerKg] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fallbackUsed, setFallbackUsed] = useState("");

  // Load states on mount
  useEffect(() => {
    fetch(`${API}/states`)
      .then(res => res.json())
      .then(data =>
        setOptions(prev => ({ ...prev, states: data || [] }))
      )
      .catch(() => setError("Failed to load states"));
  }, []);

  // Handle form changes and cascade data loading
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    if (name === "state") {
      reset(["district", "market", "commodity", "variety", "grade"]);
      fetch(`${API}/districts?state=${value}`)
        .then(r => r.json())
        .then(d => setOptions(p => ({ ...p, districts: d || [] })));
    }

    if (name === "district") {
      reset(["market", "commodity", "variety", "grade"]);
      fetch(`${API}/markets?state=${formData.state}&district=${value}`)
        .then(r => r.json())
        .then(d => setOptions(p => ({ ...p, markets: d || [] })));
    }

    if (name === "market") {
      reset(["commodity", "variety", "grade"]);
      fetch(`${API}/commodities?state=${formData.state}&district=${formData.district}&market=${value}`)
        .then(r => r.json())
        .then(d => setOptions(p => ({ ...p, commodities: d || [] })));
    }

    if (name === "commodity") {
      reset(["variety", "grade"]);
      fetch(`${API}/varieties?state=${formData.state}&district=${formData.district}&market=${formData.market}&commodity=${value}`)
        .then(r => r.json())
        .then(d => setOptions(p => ({ ...p, varieties: d || [] })));
    }

    if (name === "variety") {
      reset(["grade"]);
      fetch(`${API}/grades?state=${formData.state}&district=${formData.district}&market=${formData.market}&commodity=${formData.commodity}&variety=${value}`)
        .then(r => r.json())
        .then(d => setOptions(p => ({ ...p, grades: d || [] })));
    }
  };

  const reset = (fields) => {
    setFormData(prev => {
      const copy = { ...prev };
      fields.forEach(f => (copy[f] = ""));
      return copy;
    });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setPrediction(null);
    setPricePerKg(null);

    try {
      const res = await fetch(`${API}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Prediction failed");
      
      setPrediction(data.prediction);
      setPricePerKg((data.prediction / 100).toFixed(2));
      setFallbackUsed(data.fallback_used || "exact");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderSelect = (label, name, items, icon) => (
    <div className="form-group">
      <label className="select-label">
        <span className="icon">{icon}</span>
        {label}
      </label>
      <select
        name={name}
        value={formData[name]}
        onChange={handleChange}
        required
        className="select-input"
      >
        <option value="">Select {label}</option>
        {Array.isArray(items) && items.map(i => (
          <option key={i} value={i}>{i}</option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="app-container">
      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .app-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #1a4d2e 0%, #2d6a4f 50%, #52b788 100%);
          background-attachment: fixed;
          position: relative;
          overflow-x: hidden;
          padding: 20px;
        }

        /* Animated background elements */
        .app-container::before {
          content: '';
          position: fixed;
          top: -50%;
          right: -10%;
          width: 600px;
          height: 600px;
          background: radial-gradient(circle, rgba(129, 200, 113, 0.1) 0%, transparent 70%);
          border-radius: 50%;
          animation: float 8s ease-in-out infinite;
          pointer-events: none;
          z-index: 0;
        }

        .app-container::after {
          content: '';
          position: fixed;
          bottom: -20%;
          left: -5%;
          width: 500px;
          height: 500px;
          background: radial-gradient(circle, rgba(212, 163, 58, 0.08) 0%, transparent 70%);
          border-radius: 50%;
          animation: float 10s ease-in-out infinite reverse;
          pointer-events: none;
          z-index: 0;
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          50% { transform: translateY(-30px) translateX(20px); }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(40px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.8; }
        }

        @keyframes shimmer {
          0% { background-position: -1000px 0; }
          100% { background-position: 1000px 0; }
        }

        .main-wrapper {
          position: relative;
          z-index: 1;
          max-width: 800px;
          margin: 0 auto;
        }

        .header {
          text-align: center;
          margin-bottom: 50px;
          animation: slideDown 0.8s ease-out;
          color: white;
        }

        .header h1 {
          font-size: 3em;
          font-weight: 700;
          margin-bottom: 10px;
          text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
          letter-spacing: -1px;
        }

        .header-icon {
          font-size: 60px;
          margin-bottom: 10px;
          display: inline-block;
          animation: float 4s ease-in-out infinite;
        }

        .header p {
          font-size: 1.1em;
          opacity: 0.95;
          font-weight: 500;
        }

        .form-card {
          background: white;
          border-radius: 20px;
          padding: 40px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
          animation: slideUp 0.8s ease-out;
          margin-bottom: 30px;
          border-top: 4px solid #2d6a4f;
          backdrop-filter: blur(10px);
        }

        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 25px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          animation: slideUp 0.6s ease-out;
        }

        .form-group:nth-child(odd) {
          animation-delay: 0.05s;
        }

        .form-group:nth-child(even) {
          animation-delay: 0.1s;
        }

        .select-label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.95em;
          font-weight: 600;
          color: #2d6a4f;
          margin-bottom: 8px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .icon {
          font-size: 1.3em;
        }

        .select-input {
          padding: 12px 14px;
          border: 2px solid #e0e0e0;
          border-radius: 10px;
          font-size: 1em;
          background-color: #f8f9f7;
          color: #333;
          cursor: pointer;
          transition: all 0.3s ease;
          appearance: none;
          background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232d6a4f' stroke-width='2'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
          background-repeat: no-repeat;
          background-position: right 10px center;
          background-size: 20px;
          padding-right: 35px;
          font-weight: 500;
        }

        .select-input:hover {
          border-color: #52b788;
          background-color: #f0f7f4;
          box-shadow: 0 6px 20px rgba(82, 183, 136, 0.15);
          transform: translateY(-2px);
        }

        .select-input:focus {
          outline: none;
          border-color: #2d6a4f;
          box-shadow: 0 0 0 4px rgba(45, 106, 79, 0.1), 0 6px 20px rgba(82, 183, 136, 0.15);
          background-color: white;
        }

        .form-row-full {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 20px;
          margin-bottom: 25px;
        }

        .date-input {
          padding: 12px 14px;
          border: 2px solid #e0e0e0;
          border-radius: 10px;
          font-size: 1em;
          background-color: #f8f9f7;
          color: #333;
          cursor: pointer;
          transition: all 0.3s ease;
          font-weight: 500;
        }

        .date-input:hover {
          border-color: #52b788;
          background-color: #f0f7f4;
          box-shadow: 0 6px 20px rgba(82, 183, 136, 0.15);
          transform: translateY(-2px);
        }

        .date-input:focus {
          outline: none;
          border-color: #2d6a4f;
          box-shadow: 0 0 0 4px rgba(45, 106, 79, 0.1);
          background-color: white;
        }

        .submit-btn {
          width: 100%;
          padding: 14px 28px;
          background: linear-gradient(135deg, #2d6a4f 0%, #1a4d2e 100%);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 1.05em;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.4s ease;
          text-transform: uppercase;
          letter-spacing: 1px;
          box-shadow: 0 10px 30px rgba(45, 106, 79, 0.3);
          position: relative;
          overflow: hidden;
        }

        .submit-btn::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
          transition: left 0.5s ease;
        }

        .submit-btn:hover:not(:disabled) {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(45, 106, 79, 0.4);
        }

        .submit-btn:hover::before {
          left: 100%;
        }

        .submit-btn:active:not(:disabled) {
          transform: translateY(-1px);
        }

        .submit-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .loading-spinner {
          display: inline-block;
          width: 20px;
          height: 20px;
          border: 3px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top-color: white;
          animation: spin 0.8s linear infinite;
          margin-right: 8px;
          vertical-align: middle;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        /* Price Cards Section */
        .result-container {
          animation: fadeIn 0.6s ease-out;
        }

        .price-cards-wrapper {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 25px;
          animation: slideUp 0.8s ease-out 0.2s both;
        }

        .price-card {
          background: linear-gradient(135deg, #f0f7f4 0%, #e8f3ed 100%);
          border-radius: 15px;
          padding: 25px;
          border: 2px solid #52b788;
          position: relative;
          overflow: hidden;
          transition: all 0.3s ease;
          box-shadow: 0 10px 30px rgba(45, 106, 79, 0.1);
        }

        .price-card::before {
          content: '';
          position: absolute;
          top: -50%;
          right: -50%;
          width: 200px;
          height: 200px;
          background: radial-gradient(circle, rgba(82, 183, 136, 0.1) 0%, transparent 70%);
          border-radius: 50%;
          pointer-events: none;
        }

        .price-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 15px 40px rgba(45, 106, 79, 0.2);
          border-color: #2d6a4f;
        }

        .price-card.quintal {
          background: linear-gradient(135deg, #fff8e8 0%, #fef3d4 100%);
          border-color: #d4a347;
        }

        .price-card.quintal:hover {
          border-color: #c4933b;
        }

        .price-label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.9em;
          font-weight: 700;
          color: #2d6a4f;
          margin-bottom: 12px;
          text-transform: uppercase;
          letter-spacing: 1px;
          position: relative;
          z-index: 1;
        }

        .price-card.quintal .price-label {
          color: #8b6e2c;
        }

        .price-value {
          font-size: 2.8em;
          font-weight: 700;
          background: linear-gradient(135deg, #1a4d2e 0%, #2d6a4f 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          position: relative;
          z-index: 1;
          margin-bottom: 5px;
        }

        .price-card.quintal .price-value {
          background: linear-gradient(135deg, #8b6e2c 0%, #d4a347 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .price-unit {
          font-size: 0.75em;
          color: #666;
          font-weight: 500;
          position: relative;
          z-index: 1;
        }

        .info-box {
          background: white;
          border-radius: 12px;
          padding: 20px;
          border-left: 4px solid #52b788;
          margin-bottom: 20px;
          animation: slideUp 0.8s ease-out 0.3s both;
        }

        .info-box p {
          color: #555;
          font-size: 0.95em;
          line-height: 1.6;
          margin-bottom: 8px;
        }

        .info-box p:last-child {
          margin-bottom: 0;
        }

        .info-label {
          font-weight: 700;
          color: #2d6a4f;
          display: inline-block;
          margin-right: 6px;
        }

        .info-value {
          color: #666;
        }

        /* Error Message */
        .error-box {
          background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
          border-radius: 15px;
          padding: 25px;
          border-left: 4px solid #e53935;
          margin-bottom: 25px;
          animation: slideUp 0.6s ease-out;
          display: flex;
          gap: 15px;
        }

        .error-icon {
          font-size: 2.5em;
          flex-shrink: 0;
        }

        .error-content h3 {
          color: #c62828;
          font-size: 1.1em;
          margin-bottom: 5px;
        }

        .error-content p {
          color: #b71c1c;
          font-size: 0.95em;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .form-grid {
            grid-template-columns: 1fr;
          }

          .form-row-full {
            grid-template-columns: 1fr;
          }

          .price-cards-wrapper {
            grid-template-columns: 1fr;
          }

          .header h1 {
            font-size: 2.2em;
          }

          .form-card {
            padding: 25px;
          }

          .price-value {
            font-size: 2.2em;
          }
        }

        /* Features Section */
        .features-section {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 15px;
          margin-top: 30px;
          animation: fadeIn 0.8s ease-out 0.5s both;
        }

        .feature-card {
          text-align: center;
          padding: 20px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          backdrop-filter: blur(10px);
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .feature-icon {
          font-size: 2.5em;
          margin-bottom: 10px;
          display: inline-block;
        }

        .feature-text {
          font-weight: 600;
          font-size: 0.9em;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        @media (max-width: 768px) {
          .features-section {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <div className="main-wrapper">
        {/* Header */}
        <div className="header">
          <div className="header-icon">🌾</div>
          <h1>Crop Price Predictor</h1>
          <p>AI-Powered Agricultural Market Analysis</p>
        </div>

        {/* Form Card */}
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              {renderSelect("State", "state", options.states, "📍")}
              {renderSelect("District", "district", options.districts, "🗺️")}
              {renderSelect("Market", "market", options.markets, "🏪")}
              {renderSelect("Commodity", "commodity", options.commodities, "🌽")}
              {renderSelect("Variety", "variety", options.varieties, "🎯")}
              {renderSelect("Grade", "grade", options.grades, "⭐")}
            </div>

            <div className="form-row-full">
              <div className="form-group">
                <label className="select-label">
                  <span className="icon">📅</span>
                  Select Date
                </label>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  required
                  className="date-input"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="submit-btn"
            >
              {loading ? (
                <>
                  <span className="loading-spinner"></span>
                  Analyzing Market Data...
                </>
              ) : (
                <>
                  📊 Predict Price
                </>
              )}
            </button>
          </form>
        </div>

        {/* Results Section */}
        {prediction && (
          <div className="result-container">
            <div className="price-cards-wrapper">
              {/* Per Quintal Card */}
              <div className="price-card quintal">
                <div className="price-label">
                  <span>📦</span>
                  Per Quintal
                </div>
                <div className="price-value">₹{prediction}</div>
                <div className="price-unit">(100 kg)</div>
              </div>

              {/* Per KG Card */}
              <div className="price-card">
                <div className="price-label">
                  <span>⚖️</span>
                  Per Kilogram
                </div>
                <div className="price-value">₹{pricePerKg}</div>
                <div className="price-unit">(1 kg)</div>
              </div>
            </div>

            {/* Info Box */}
            <div className="info-box">
              <p>
                <span className="info-label">📐 Conversion:</span>
                <span className="info-value">1 Quintal = 100 Kilograms</span>
              </p>
              <p>
                <span className="info-label">🔍 Method:</span>
                <span className="info-value">
                  {fallbackUsed === "exact" ? "Exact Match" : "Approximate Match"}
                </span>
              </p>
              <p>
                <span className="info-label">⏰ Date:</span>
                <span className="info-value">{formData.date}</span>
              </p>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-box">
            <div className="error-icon">⚠️</div>
            <div className="error-content">
              <h3>Prediction Error</h3>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Features Section */}
        {!prediction && !error && (
          <div className="features-section">
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <div className="feature-text">Accurate Data</div>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <div className="feature-text">Real-time Results</div>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <div className="feature-text">Smart Predictions</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}