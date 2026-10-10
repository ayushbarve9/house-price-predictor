import React from 'react';
import { 
  Building2, 
  MapPin, 
  Sliders, 
  Calendar, 
  Car, 
  Sparkles,
  AlertCircle
} from 'lucide-react';

export default function ValuationForm({ 
  meta, 
  form, 
  setForm, 
  onSubmit, 
  loading, 
  error 
}) {
  const localities = (meta?.city_locality_map && form.city) 
    ? (meta.city_locality_map[form.city] || []) 
    : [];

  const minArea = form.bhk * 200;
  const isAreaInvalid = form.area_sqft < minArea;
  const maxBathrooms = form.bhk + 2;
  const isBathroomsInvalid = form.bathrooms > maxBathrooms;

  const handleChange = (field, value) => {
    setForm(prev => {
      const updated = { ...prev, [field]: value };
      if (field === 'city' && meta?.city_locality_map) {
        const nextLocalities = meta.city_locality_map[value] || [];
        updated.locality = nextLocalities.length > 0 ? nextLocalities[0] : '';
      }
      if (field === 'bhk') {
        const nextMin = value * 200;
        if (updated.area_sqft < nextMin) {
          updated.area_sqft = nextMin;
        }
        if (updated.bathrooms > value + 2) {
          updated.bathrooms = value;
        }
      }
      return updated;
    });
  };

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-7 shadow-2xl relative overflow-hidden">
      <div className="flex items-center justify-between pb-5 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Building2 className="h-5 w-5 text-emerald-400" />
            Property Specifications
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Parameters mapped directly to trained pipeline features
          </p>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3.5 rounded-xl bg-red-950/50 border border-red-800/60 text-red-300 text-xs flex items-start gap-2.5">
          <AlertCircle className="h-4 w-4 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-200">Validation / Estimation Error</p>
            <p className="mt-0.5">{error}</p>
          </div>
        </div>
      )}

      <form onSubmit={onSubmit} className="mt-6 space-y-5">
        {/* City and Locality */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5 text-emerald-400" /> City
            </label>
            <select
              value={form.city}
              onChange={(e) => handleChange('city', e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-colors"
            >
              {meta?.cities?.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Locality / Micro-market
            </label>
            <select
              value={form.locality}
              onChange={(e) => handleChange('locality', e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-colors"
            >
              {localities.map(loc => (
                <option key={loc} value={loc}>{loc}</option>
              ))}
            </select>
          </div>
        </div>

        {/* BHK Selector */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">
            Configuration (BHK)
          </label>
          <div className="grid grid-cols-5 gap-2">
            {[1, 2, 3, 4, 5].map(b => (
              <button
                type="button"
                key={b}
                onClick={() => handleChange('bhk', b)}
                className={`py-2 text-sm font-semibold rounded-xl transition-all cursor-pointer ${
                  form.bhk === b
                    ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/25 ring-2 ring-emerald-400'
                    : 'bg-slate-900/90 text-slate-300 border border-slate-800 hover:border-slate-700 hover:bg-slate-850'
                }`}
              >
                {b} BHK
              </button>
            ))}
          </div>
        </div>

        {/* Area and Bathrooms */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-semibold text-slate-300">
                Super Built-up Area (sq.ft)
              </label>
              <span className="text-[11px] text-slate-400">Min {minArea} sq.ft</span>
            </div>
            <input
              type="number"
              min={minArea}
              max={10000}
              step={10}
              value={form.area_sqft}
              onChange={(e) => handleChange('area_sqft', Number(e.target.value))}
              className={`w-full bg-slate-900 border ${
                isAreaInvalid ? 'border-red-500 ring-1 ring-red-500' : 'border-slate-700/80'
              } rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50`}
            />
            {isAreaInvalid && (
              <p className="text-[11px] text-red-400 mt-1">
                Area must be at least {minArea} sq.ft for {form.bhk} BHK.
              </p>
            )}
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-semibold text-slate-300">
                Bathrooms
              </label>
              <span className="text-[11px] text-slate-400">Max {maxBathrooms}</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handleChange('bathrooms', Math.max(1, form.bathrooms - 1))}
                className="h-10 w-11 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 hover:bg-slate-800 flex items-center justify-center font-bold text-base transition-colors cursor-pointer"
              >
                -
              </button>
              <input
                type="number"
                readOnly
                value={form.bathrooms}
                className="w-full text-center bg-slate-900 border border-slate-700/80 rounded-xl py-2.5 text-sm font-semibold text-slate-100"
              />
              <button
                type="button"
                onClick={() => handleChange('bathrooms', Math.min(maxBathrooms, form.bathrooms + 1))}
                className="h-10 w-11 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 hover:bg-slate-800 flex items-center justify-center font-bold text-base transition-colors cursor-pointer"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* Property Type, Furnishing, Status */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Property Type
            </label>
            <select
              value={form.property_type}
              onChange={(e) => handleChange('property_type', e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs sm:text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            >
              {meta?.property_types?.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Furnishing
            </label>
            <select
              value={form.furnishing}
              onChange={(e) => handleChange('furnishing', e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs sm:text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            >
              {meta?.furnishing_options?.map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Construction Status
            </label>
            <select
              value={form.construction_status}
              onChange={(e) => handleChange('construction_status', e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs sm:text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            >
              {meta?.status_options?.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Age and Parking */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5 text-slate-400" /> Property Age: {form.age_years} yrs
            </label>
            <input
              type="range"
              min="0"
              max="30"
              value={form.age_years}
              onChange={(e) => handleChange('age_years', Number(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>Brand New (0)</span>
              <span>15 yrs</span>
              <span>30+ yrs</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Car className="h-3.5 w-3.5 text-slate-400" /> Reserved Parking: {form.parking}
            </label>
            <input
              type="range"
              min="0"
              max="4"
              value={form.parking}
              onChange={(e) => handleChange('parking', Number(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>0 spot</span>
              <span>1 spot</span>
              <span>2 spots</span>
              <span>3+ spots</span>
            </div>
          </div>
        </div>

        {/* Financing Section */}
        <div className="pt-4 border-t border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
              <Sliders className="h-3.5 w-3.5 text-emerald-400" />
              Loan & Acquisition Assumptions
            </span>
            <span className="text-[11px] text-emerald-400/90 font-medium bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-900/40">
              RBI LTV Cap Enforced
            </span>
          </div>

          <div className="space-y-3.5 bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
            <div>
              <div className="flex justify-between text-xs font-medium mb-1.5">
                <span className="text-slate-300">Down Payment</span>
                <span className="text-emerald-400 font-bold">{form.down_payment_pct}%</span>
              </div>
              <input
                type="range"
                min="10"
                max="50"
                step="5"
                value={form.down_payment_pct}
                onChange={(e) => handleChange('down_payment_pct', Number(e.target.value))}
                className="w-full accent-emerald-500 bg-slate-800 h-1.5 rounded cursor-pointer"
              />
            </div>

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <div className="flex justify-between text-xs font-medium mb-1.5">
                  <span className="text-slate-300">Interest Rate</span>
                  <span className="text-emerald-400 font-bold">{form.annual_rate_pct}%</span>
                </div>
                <input
                  type="range"
                  min="6.5"
                  max="13.0"
                  step="0.1"
                  value={form.annual_rate_pct}
                  onChange={(e) => handleChange('annual_rate_pct', Number(e.target.value))}
                  className="w-full accent-emerald-500 bg-slate-800 h-1.5 rounded cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium mb-1.5">
                  <span className="text-slate-300">Tenure</span>
                  <span className="text-emerald-400 font-bold">{form.tenure_years} yrs</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="30"
                  step="1"
                  value={form.tenure_years}
                  onChange={(e) => handleChange('tenure_years', Number(e.target.value))}
                  className="w-full accent-emerald-500 bg-slate-800 h-1.5 rounded cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || isAreaInvalid || isBathroomsInvalid}
          className="w-full py-3.5 px-4 rounded-xl font-bold text-sm text-slate-950 bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-500 hover:from-emerald-300 hover:to-teal-300 transition-all shadow-xl shadow-emerald-500/20 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
        >
          {loading ? (
            <>
              <div className="h-4 w-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              <span>Evaluating Model Inference...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4 text-slate-950 fill-current" />
              <span>Calculate Valuation & Cost Breakdown</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
