import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileSpreadsheet, AlertTriangle, Cpu } from 'lucide-react';

export default function Sidebar() {
  const links = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Reconciliation', path: '/reconciliation', icon: FileSpreadsheet },
    { name: 'Exceptions', path: '/exceptions', icon: AlertTriangle },
    { name: 'AI Insights', path: '/ai-insights', icon: Cpu },
  ];

  return (
    <div className="w-64 bg-dark-800 h-screen fixed left-0 top-0 border-r border-dark-700 flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-brand-blue to-brand-purple">FINRECON AI</h1>
        <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">Autonomous Controller</p>
      </div>
      <nav className="flex-1 mt-6 px-4 space-y-2">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.name}
              to={link.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive ? 'bg-brand-blue/10 text-brand-blue border border-brand-blue/20' : 'text-slate-400 hover:bg-dark-700 hover:text-white'
                }`
              }
            >
              <Icon size={20} />
              <span className="font-medium">{link.name}</span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}