import React, { useEffect, useState } from 'react';
import { Activity } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { api } from '../services/api';

export default function Header() {
  const location = useLocation();
  const [status, setStatus] = useState('Checking...');

  useEffect(() => {
    api.checkHealth().then(res => setStatus(res.status === 'offline' ? 'Offline (Mock Mode)' : 'System Operational'));
  }, []);

  const titles = {
    '/': { title: 'Dashboard', desc: 'Overview of reconciliation metrics and system status.' },
    '/reconciliation': { title: 'Reconciliation Hub', desc: 'Inspect all transaction matches and discrepancies.' },
    '/exceptions': { title: 'Exceptions', desc: 'Transactions requiring human review and intervention.' },
    '/ai-insights': { title: 'AI Insights', desc: 'Intelligent analysis and automated recommendations.' },
  };
  const current = titles[location.pathname] || titles['/'];

  return (
    <header className="h-20 bg-dark-800 border-b border-dark-700 flex items-center justify-between px-8 sticky top-0 z-10">
      <div>
        <h2 className="text-xl font-bold text-white">{current.title}</h2>
        <p className="text-sm text-slate-400">{current.desc}</p>
      </div>
      <div className="flex items-center gap-2 bg-dark-900 px-4 py-2 rounded-full border border-dark-700">
        <div className={`w-2 h-2 rounded-full ${status.includes('Operational') ? 'bg-green-500 animate-pulse' : 'bg-orange-500'}`}></div>
        <span className="text-sm font-medium text-slate-300">{status}</span>
      </div>
    </header>
  );
}