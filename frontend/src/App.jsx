import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Reconciliation from './pages/Reconciliation';
import Exceptions from './pages/Exceptions';
import AIInsights from './pages/AIInsights';

export default function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-dark-900">
        <Sidebar />
        <div className="flex-1 ml-64 flex flex-col">
          <Header />
          <main className="flex-1 p-8 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/reconciliation" element={<Reconciliation />} />
              <Route path="/exceptions" element={<Exceptions />} />
              <Route path="/ai-insights" element={<AIInsights />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}