import React from 'react';
import { Layers, MapPin, Building } from 'lucide-react';
import { formatINR } from '../utils/formatters';

export default function ComparablesSection({ comparables, targetLocality, targetPrice }) {
  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-7 shadow-2xl">
      <div className="flex items-center justify-between pb-5 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Layers className="h-5 w-5 text-emerald-400" />
            Verified Training Dataset Comparables
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real benchmark transactions from the model's calibrated training set
          </p>
        </div>
      </div>

      {!comparables || comparables.length === 0 ? (
        <div className="mt-6 p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800/80">
          <p className="text-sm text-slate-400">
            No exact historical comparables available in this micro-market slice.
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Valuation is derived via tree-ensemble spatial interpolation.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          {comparables.map((comp, idx) => {
            const price = comp.Price_INR || comp.Price || comp.price || 0;
            const area = comp.Area_SqFt || comp.area_sqft || 0;
            const rate = area > 0 ? price / area : 0;
            const diffPct = targetPrice > 0 ? ((price - targetPrice) / targetPrice) * 100 : 0;

            return (
              <div 
                key={idx}
                className="bg-slate-900/80 hover:bg-slate-900 transition-all rounded-xl p-4 border border-slate-800/90 hover:border-slate-700 flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {comp.BHK || comp.bhk} BHK • {comp.Property_Type || 'Apartment'}
                    </span>
                    {targetPrice > 0 && (
                      <span className={`text-[10px] font-bold ${
                        diffPct > 0 ? 'text-amber-400' : 'text-emerald-400'
                      }`}>
                        {diffPct > 0 ? `+${diffPct.toFixed(1)}%` : `${diffPct.toFixed(1)}%`}
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-bold text-slate-100 flex items-center gap-1.5 mt-2">
                    {formatINR(price)}
                  </h3>

                  <div className="mt-3 space-y-1 text-xs text-slate-400">
                    <div className="flex items-center gap-1.5">
                      <MapPin className="h-3 w-3 text-slate-500" />
                      <span className="truncate">{comp.Locality || targetLocality}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Building className="h-3 w-3 text-slate-500" />
                      <span>{area} sq.ft (₹{Math.round(rate).toLocaleString('en-IN')}/sq.ft)</span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 mt-3 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between">
                  <span>Status: {comp.Construction_Status || 'Ready'}</span>
                  <span>Age: {comp.Age_Years || 0} yrs</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
