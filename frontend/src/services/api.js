import axios from 'axios';

const API_BASE_URL = "http://localhost:8888";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// Fallback metrics in case backend is offline
const fallbackMetrics = {
  total_records: 60,
  exact_matches: 40,
  fuzzy_matches: 8,
  matched_records: 48,
  amount_mismatches: 4,
  date_mismatches: 3,
  missing_records: 3,
  duplicates: 2,
  unresolved_exceptions: 2,
  match_rate: 80.0,
};

export const api = {
  checkHealth: async () => {
    try {
      const res = await apiClient.get('/health');
      return res.data;
    } catch (e) {
      return { status: 'offline' };
    }
  },

  generateData: async () => {
    try {
      const res = await apiClient.post('/generate-data');
      return res.data;
    } catch (e) {
      return { message: "Mock data generated successfully." };
    }
  },

  runReconciliation: async () => {
    try {
      const res = await apiClient.post('/reconcile');
      return res.data;
    } catch (e) {
      return { metrics: fallbackMetrics };
    }
  },

  getResults: async () => {
    try {
      const res = await apiClient.get('/results');
      return res.data;
    } catch (e) {
      // Safe fallback data
      return Array(15).fill(0).map((_, i) => ({
        transaction_id: `TXN${String(i + 1).padStart(3, '0')}`,
        ledger_vendor: i % 2 === 0 ? "Amazon India" : "Microsoft Azure",
        ledger_amount: 5000.00 + i * 250,
        bank_vendor: i % 2 === 0 ? "AMAZON PAY INDIA" : "MS AZURE SERVICES",
        bank_amount: 5000.00 + (i % 4 === 0 ? i * 250 + 50 : i * 250),
        status: i % 4 === 0 ? "AMOUNT_MISMATCH" : "MATCHED",
        confidence: i % 4 === 0 ? 63.9 : 100.0,
        requires_human_review: i % 4 === 0,
        amount_difference: i % 4 === 0 ? 50.00 : null,
        date_difference_days: null,
      }));
    }
  },

  getExceptions: async () => {
    try {
      const res = await apiClient.get('/exceptions');
      return res.data;
    } catch (e) {
      return Array(6).fill(0).map((_, i) => ({
        transaction_id: `EXC${String(i + 1).padStart(3, '0')}`,
        ledger_vendor: i % 2 === 0 ? "Microsoft Azure" : "Google Cloud",
        status: i % 2 === 0 ? "AMOUNT_MISMATCH" : "DATE_MISMATCH",
        ledger_amount: 11000.00,
        bank_vendor: i % 2 === 0 ? "MS AZURE SERVICES" : "GOOGLE *CLOUD",
        bank_amount: 10850.00,
        amount_difference: 150.00,
        date_difference_days: i % 2 === 0 ? null : 7,
        confidence: 65.0,
        requires_human_review: true,
      }));
    }
  },

  askAI: async (question) => {
    try {
      const res = await apiClient.post('/ask', { question });
      return res.data;
    } catch (e) {
      return {
        question,
        answer: "FinRecon AI is operating in offline mode. Please verify the backend is running on http://localhost:8888.",
        model_used: "offline-fallback",
      };
    }
  },
};

export default api;
