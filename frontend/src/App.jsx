import React, { useState, useEffect, useCallback } from 'react';
import HeroSection from './components/HeroSection';
import Header from './components/Header';
import ValuationForm from './components/ValuationForm';
import ValuationHero from './components/ValuationHero';
import FinancialBreakdown from './components/FinancialBreakdown';
import ComparablesSection from './components/ComparablesSection';
import ChatbotPanel from './components/ChatbotPanel';
import { AlertCircle, RefreshCw, Sparkles, Building, ChevronDown } from 'lucide-react';

export default function App() {
  const [meta, setMeta] = useState(null);
  const [loadingMeta, setLoadingMeta] = useState(true);
  const [metaError, setMetaError] = useState(null);

  const [form, setForm] = useState({
    city: 'Bengaluru',
    locality: '',
    bhk: 3,
    area_sqft: 1500,
    bathrooms: 3,
    property_type: 'Apartment',
    furnishing: 'Semi-Furnished',
    construction_status: 'Ready to Move',
    age_years: 3,
    parking: 1,
    down_payment_pct: 20,
    annual_rate_pct: 8.5,
    tenure_years: 20,
  });

  const [estimate, setEstimate] = useState(null);
  const [estimateLoading, setEstimateLoading] = useState(false);
  const [estimateError, setEstimateError] = useState(null);

  const runEstimate = useCallback(async (formPayload) => {
    setEstimateLoading(true);
    setEstimateError(null);
    try {
      const res = await fetch('/api/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formPayload),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        let message = `Estimation failed (${res.status})`;
        if (errJson.detail) {
          if (Array.isArray(errJson.detail)) {
            message = errJson.detail.map(d => d.msg).join(', ');
          } else {
            message = errJson.detail;
          }
        }
        throw new Error(message);
      }

      const data = await res.json();
      setEstimate(data);
    } catch (err) {
      setEstimateError(err.message);
    } finally {
      setEstimateLoading(false);
    }
  }, []);

  // Fetch metadata once at startup
  useEffect(() => {
    async function loadMeta() {
      try {
        setLoadingMeta(true);
        setMetaError(null);
        const res = await fetch('/api/meta');
        if (!res.ok) {
          throw new Error(`Failed to load model metadata (${res.status})`);
        }
        const data = await res.json();
        setMeta(data);

        // Pick initial city and locality
        const defaultCity = data.cities?.[0] || 'Bengaluru';
        const defaultLocality = data.city_locality_map?.[defaultCity]?.[0] || '';

        const initialForm = {
          city: defaultCity,
          locality: defaultLocality,
          bhk: 3,
          area_sqft: 1500,
          bathrooms: 3,
          property_type: data.property_types?.[0] || 'Apartment',
          furnishing: data.furnishing_options?.[1] || 'Semi-Furnished',
          construction_status: data.status_options?.[0] || 'Ready to Move',
          age_years: 3,
          parking: 1,
          down_payment_pct: 20,
          annual_rate_pct: 8.5,
          tenure_years: 20,
        };

        setForm(initialForm);

        // Auto-run baseline estimate for immediate feedback
        runEstimate(initialForm);
      } catch (err) {
        setMetaError(err.message || 'Error connecting to backend API');
      } finally {
        setLoadingMeta(false);
      }
    }

    loadMeta();
  }, [runEstimate]);

  const handleFormSubmit = (e) => {
    e?.preventDefault();
    runEstimate(form);
  };

  const scrollToValuation = () => {
    const el = document.getElementById('valuation-workspace');
    el?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-[#5E0ED7] selection:text-white">
      {/* 1. Full-Screen Video Hero Section */}
      <HeroSection onExploreClick={scrollToValuation} />

      {/* 2. Transition Divider / Anchor */}
      <div 
        id="valuation-workspace" 
        className="w-full relative z-20 border-t border-slate-800/80 bg-slate-950"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 pb-2 flex items-center justify-between text-xs text-slate-400">
          <button
            onClick={scrollToValuation}
            className="flex items-center gap-2 text-emerald-400 font-semibold hover:text-emerald-300 transition-colors cursor-pointer"
          >
            <ChevronDown className="w-4 h-4 animate-bounce" />
            <span>GrihaValue Valuation & Acquisition Suite</span>
          </button>
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            Interactive ML Studio • Live Inference
          </span>
        </div>
      </div>

      {/* 3. GrihaValue Workspace Header */}
      <Header meta={meta} loading={loadingMeta} />

      {/* 4. Main Valuation Engine & Intelligence Workspace */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {/* API / Backend Connection Error Banner */}
        {metaError && (
          <div className="mb-6 p-4 rounded-2xl bg-red-950/40 border border-red-800 text-red-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-red-400 shrink-0" />
              <div>
                <h3 className="font-bold text-sm">Cannot connect to GrihaValue Backend</h3>
                <p className="text-xs text-red-300 mt-0.5">{metaError}</p>
              </div>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="px-3 py-1.5 rounded-lg bg-red-900/60 hover:bg-red-800 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <RefreshCw className="h-3 w-3" /> Retry
            </button>
          </div>
        )}

        {/* Section Tagline */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-3">
            <Sparkles className="h-3.5 w-3.5" />
            Empirical Real Estate Valuation & Regulatory Cost Stack
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white max-w-3xl">
            Accurate Property Valuation with Real Acquisition Costs
          </h2>
          <p className="text-sm sm:text-base text-slate-400 mt-2 max-w-2xl">
            Trained on multi-city Indian housing data with strict RBI Loan-to-Value enforcement and exact state-wise stamp duty calculations.
          </p>
        </div>

        {/* 2-Column Responsive Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Input Form (5 cols on lg) */}
          <div className="lg:col-span-5 sticky top-24">
            <ValuationForm
              meta={meta}
              form={form}
              setForm={setForm}
              onSubmit={handleFormSubmit}
              loading={estimateLoading}
              error={estimateError}
            />
          </div>

          {/* Right Column: Valuation Results, Breakdown, Comps & Chat (7 cols on lg) */}
          <div className="lg:col-span-7 space-y-6">
            {estimate ? (
              <>
                <ValuationHero estimate={estimate} form={form} />
                <FinancialBreakdown
                  finance={estimate.finance}
                  city={form.city}
                />
                <ComparablesSection
                  comparables={estimate.comparables}
                  targetLocality={form.locality}
                  targetPrice={estimate.predicted_price}
                />
                <ChatbotPanel estimate={estimate} form={form} />
              </>
            ) : (
              <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
                <Building className="h-12 w-12 text-slate-600 mx-auto mb-3 animate-pulse" />
                <h3 className="text-base font-bold text-slate-300">
                  Ready for Evaluation
                </h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                  Adjust the property specifications on the left and run valuation to view predicted market price, loan eligibility, and government charges.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* 5. Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>
            GrihaValue Engine © 2026 • Powered by scikit-learn Pipeline & FastAPI
          </p>
          <p className="flex items-center gap-2">
            <span>RBI Master Direction (Housing Finance)</span>
            <span>•</span>
            <span>State Stamp Acts 2026</span>
          </p>
        </div>
      </footer>
    </div>
  );
}
