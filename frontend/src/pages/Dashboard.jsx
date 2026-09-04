import React, { useState } from 'react';
import { Database, Play, RefreshCw, FileText, CheckSquare, AlertTriangle, HelpCircle } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import ReconciliationChart from '../components/ReconciliationChart';
import { api } from '../services/api';

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setActionMessage('Generating synthetic financial transactions...');
    try {
      const res = await api.generateData();
      setActionMessage(res.message || 'Synthetic data generated successfully!');
    } catch (err) {
      setActionMessage('Failed generating data. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleReconcile = async () => {
    setLoading(true);
    setActionMessage('Running reconciliation engine across Ledger, Bank, and Gateway...');
    try {
      const data = await api.runReconciliation();
      const m = data.metrics || data.summary;
      setMetrics(m);
      setActionMessage(`Reconciliation complete! Match rate: ${m.match_rate}%`);
    } catch (err) {
      setActionMessage('Reconciliation failed. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  // Safe metric calculation
  const total = metrics?.total_records ?? 0;
  const matchRate = metrics?.match_rate != null ? `${metrics.match_rate}%` : '0.0%';
  const matchedCount = metrics?.matched_records ?? ((metrics?.exact_matches ?? 0) + (metrics?.fuzzy_matches ?? 0));
  const exceptionsCount = (metrics?.amount_mismatches ?? 0) +
    (metrics?.date_mismatches ?? 0) +
    (metrics?.missing_records ?? 0) +
    (metrics?.duplicates ?? 0) +
    (metrics?.unresolved_exceptions ?? 0);
  const reviewCount = exceptionsCount;

  return (
    <div className="space-y-6">
      {/* Top Banner & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between bg-dark-800 p-6 rounded-xl border border-dark-700 shadow-lg gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">Welcome to FinRecon AI</h2>
          <p className="text-slate-400 text-sm">
            Autonomous multi-source financial transaction reconciliation controller.
          </p>
          {actionMessage && (
            <p className="text-xs text-brand-blue font-medium mt-2 bg-brand-blue/10 px-3 py-1 rounded-md border border-brand-blue/20 w-fit">
              ℹ️ {actionMessage}
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-4 py-2.5 rounded-lg font-medium transition-colors border border-dark-600 disabled:opacity-50 text-sm"
          >
            <Database size={18} /> Generate Data
          </button>
          <button
            onClick={handleReconcile}
            disabled={loading}
            className="flex items-center gap-2 bg-brand-blue hover:bg-blue-500 text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-lg shadow-brand-blue/20 disabled:opacity-50 text-sm"
          >
            {loading ? <RefreshCw className="animate-spin" size={18} /> : <Play size={18} />} Run Reconciliation
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      {metrics && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Ledger Records"
              value={total}
              icon={FileText}
              color="text-brand-purple"
              bg="bg-brand-purple/10"
            />
            <MetricCard
              title="Autonomous Match Rate"
              value={matchRate}
              icon={CheckSquare}
              color="text-green-400"
              bg="bg-green-400/10"
            />
            <MetricCard
              title="Exceptions Detected"
              value={exceptionsCount}
              icon={AlertTriangle}
              color="text-orange-400"
              bg="bg-orange-400/10"
            />
            <MetricCard
              title="Human Review Required"
              value={reviewCount}
              icon={HelpCircle}
              color="text-red-400"
              bg="bg-red-400/10"
            />
          </div>

          {/* Charts & System Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <ReconciliationChart data={metrics} />
            </div>

            <div className="lg:col-span-2 bg-dark-800 p-6 rounded-xl border border-dark-700 shadow-lg flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Controller Audit Summary</h3>
                <div className="space-y-3 text-slate-300 text-sm">
                  <div className="flex items-center justify-between p-3 bg-dark-900 rounded-lg border border-dark-700">
                    <span className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-green-500"></span>
                      Exact Matches (100% confidence):
                    </span>
                    <strong className="text-white">{metrics.exact_matches ?? 0}</strong>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-dark-900 rounded-lg border border-dark-700">
                    <span className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                      Fuzzy Vendor Matches (75-94% confidence):
                    </span>
                    <strong className="text-white">{metrics.fuzzy_matches ?? 0}</strong>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-dark-900 rounded-lg border border-dark-700">
                    <span className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
                      Amount Mismatches:
                    </span>
                    <strong className="text-orange-400">{metrics.amount_mismatches ?? 0}</strong>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-dark-900 rounded-lg border border-dark-700">
                    <span className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span>
                      Date Mismatches:
                    </span>
                    <strong className="text-yellow-400">{metrics.date_mismatches ?? 0}</strong>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-dark-900 rounded-lg border border-dark-700">
                    <span className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-pink-500"></span>
                      Missing Bank Records:
                    </span>
                    <strong className="text-pink-400">{metrics.missing_records ?? 0}</strong>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-dark-900 rounded-lg border border-dark-700">
                    <span className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span>
                      Duplicate Bank Entries:
                    </span>
                    <strong className="text-purple-400">{metrics.duplicates ?? 0}</strong>
                  </div>
                </div>
              </div>

              <div className="mt-4 p-4 bg-dark-900/80 rounded-lg border border-dark-700">
                <p className="text-xs text-slate-400 italic">
                  "FinRecon AI operates on an honest reconciliation policy: unresolved transactions and discrepancies are explicitly separated from verified matches for human controller audit."
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Empty State */}
      {!metrics && !loading && (
        <div className="h-72 flex flex-col items-center justify-center border-2 border-dashed border-dark-700 rounded-xl text-slate-500 p-8 text-center bg-dark-800/50">
          <Database size={48} className="mb-4 text-brand-blue opacity-40" />
          <h4 className="text-white font-medium mb-1">No Reconciliation Batch Loaded</h4>
          <p className="text-sm max-w-md text-slate-400 mb-4">
            Click <strong>Generate Data</strong> to populate internal ledger and statements, then click <strong>Run Reconciliation</strong> to view real-time matching metrics.
          </p>
          <button
            onClick={handleReconcile}
            className="flex items-center gap-2 bg-brand-blue hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Play size={16} /> Run First Reconciliation
          </button>
        </div>
      )}
    </div>
  );
}
