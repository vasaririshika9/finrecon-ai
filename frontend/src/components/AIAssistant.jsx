import React, { useState } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { api } from '../services/api';

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: "Hello! I am your FINRECON AI assistant. Ask me anything about your reconciliation results, exceptions, or match rates."
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userQuestion = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userQuestion }]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.askAI(userQuestion);
      setMessages(prev => [
        ...prev,
        {
          role: 'ai',
          text: res.answer || "Unable to get an answer.",
          model: res.model_used
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'ai',
          text: "I encountered an error connecting to the AI controller. Please verify backend status."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-dark-800 rounded-xl border border-dark-700 flex flex-col h-[520px] shadow-lg">
      <div className="p-4 border-b border-dark-700 bg-dark-700/50 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-brand-purple/20 text-brand-purple">
            <Bot size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-white text-sm">FinRecon AI Agent</h3>
            <p className="text-[11px] text-slate-400">Autonomous Finance Controller</p>
          </div>
        </div>
        <span className="text-[11px] bg-green-500/10 text-green-400 px-2 py-0.5 rounded-full border border-green-500/20 font-medium">
          Active
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === 'ai' ? '' : 'flex-row-reverse'}`}>
            <div className={`p-2 rounded-full h-fit shrink-0 ${m.role === 'ai' ? 'bg-brand-purple/20 text-brand-purple' : 'bg-brand-blue/20 text-brand-blue'}`}>
              {m.role === 'ai' ? <Bot size={16} /> : <User size={16} />}
            </div>
            <div className={`p-3.5 rounded-xl max-w-[85%] text-sm leading-relaxed ${m.role === 'ai' ? 'bg-dark-700 text-slate-200 border border-dark-600' : 'bg-brand-blue text-white'}`}>
              <p>{m.text}</p>
              {m.model && (
                <p className="text-[10px] text-slate-400 mt-1 pt-1 border-t border-dark-600/50">
                  Model: {m.model}
                </p>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 items-center text-slate-400 text-xs italic">
            <div className="p-2 rounded-full bg-brand-purple/20 text-brand-purple">
              <Loader2 size={16} className="animate-spin" />
            </div>
            <span>FinRecon AI is analyzing report data...</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="p-4 border-t border-dark-700 flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask: 'What is the match rate?', 'Show exceptions'..." 
          className="flex-1 bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-brand-blue transition-colors placeholder:text-slate-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-brand-blue hover:bg-blue-500 disabled:opacity-50 text-white p-2.5 rounded-lg transition-colors flex items-center justify-center"
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
