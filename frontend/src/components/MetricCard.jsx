
import React from 'react';

export default function MetricCard({ title, value, icon: Icon, color = 'text-brand-blue', bg = 'bg-brand-blue/10' }) {
  return (
    <div className="bg-dark-800 p-6 rounded-xl border border-dark-700 flex items-center gap-4 hover:border-slate-600 transition-colors shadow-lg">
      <div className={`p-4 rounded-lg ${bg} ${color}`}>
        <Icon size={24} />
      </div>
      <div>
        <p className="text-sm text-slate-400 font-medium">{title}</p>
        <p className="text-2xl font-bold text-white mt-1">{value}</p>
      </div>
    </div>
  );
}