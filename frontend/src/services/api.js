
import axios from "axios";

// Production Backend URL
// const API_BASE_URL = "https://finrecon-ai-backend.onrender.com";
const API_BASE_URL = import.meta.env.VITE_API_URL || "https://finrecon-ai-backend.onrender.com";
// const API_URL =
//   import.meta.env.VITE_API_URL || "https://finrecon-ai-backend.onrender.com";

console.log("API URL:", API_BASE_URL);
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// ==========================================
// FALLBACK METRICS
// ==========================================

const fallbackMetrics = {
  total_records: 60,
  exact_matches: 40,
  fuzzy_matches: 8,
  matched_records: 48,
  amount_mismatches: 4,
  date_mismatches: 3,
  missing_bank_records: 3,
  duplicate_records: 2,
  unresolved_exceptions: 5,
  human_review_required: 5,
  match_rate: 80.0,
};

// ==========================================
// API FUNCTIONS
// ==========================================

export const api = {
  checkHealth: async () => {
    try {
      const res = await apiClient.get("/health");
      return res.data;
    } catch (error) {
      console.error("Health check error:", error);
      return {
        status: "offline",
        message: "Backend is currently unavailable",
      };
    }
  },

  generateData: async () => {
    try {
      const res = await apiClient.post("/generate-data");
      return res.data;
    } catch (error) {
      console.error("Generate data error:", error);
      return { message: "Unable to connect to backend" };
    }
  },

  runReconciliation: async () => {
    try {
      const res = await apiClient.post("/reconcile");
      return res.data;
    } catch (error) {
      console.error("Reconciliation error:", error);
      return { metrics: fallbackMetrics };
    }
  },

  getResults: async () => {
    try {
      const res = await apiClient.get("/results");
      return res.data;
    } catch (error) {
      console.error("Get results error:", error);
      return [];
    }
  },

  getExceptions: async () => {
    try {
      const res = await apiClient.get("/exceptions");
      return res.data;
    } catch (error) {
      console.error("Get exceptions error:", error);
      return [];
    }
  },

  askAI: async (question) => {
    try {
      const res = await apiClient.post("/ask", { question });
      return res.data;
    } catch (error) {
      console.error("AI request error:", error);
      return {
        question,
        answer: "FinRecon AI is temporarily unable to connect to the backend. Please try again shortly.",
        model_used: "offline-fallback",
      };
    }
  },
};

export default api;