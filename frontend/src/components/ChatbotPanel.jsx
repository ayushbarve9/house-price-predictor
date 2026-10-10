import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Bot, User, RefreshCw, Zap } from 'lucide-react';
import { getGroundedAdvisorResponse } from '../utils/groundedAdvisor';

export default function ChatbotPanel({ estimate, form }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I am your GrihaValue property advisor. I am grounded specifically in the ML valuation for this ${form.bhk} BHK property in ${form.locality}, ${form.city}. Ask me anything about the acquisition costs, loan LTV, or stamp duty!`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const quickPrompts = [
    'Break down my total out-of-pocket cash needed',
    'How is my monthly EMI calculated?',
    'Explain the stamp duty and registration charges',
    'What is the RBI LTV cap on this loan amount?',
  ];

  const streamFallbackText = async (text) => {
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
    const words = text.split(' ');
    for (let i = 0; i < words.length; i++) {
      const current = words.slice(0, i + 1).join(' ');
      setMessages(prev => {
        const copy = [...prev];
        copy[copy.length - 1] = { role: 'assistant', content: current };
        return copy;
      });
      // smooth natural typing cadence
      await new Promise(r => setTimeout(r, 16));
    }
  };

  const handleSend = async (messageText) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading || !estimate) return;

    const newMessages = [...messages, { role: 'user', content: textToSend }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    const estimateContext = {
      predicted_price: estimate.predicted_price,
      rate_per_sqft: estimate.rate_per_sqft,
      finance: estimate.finance,
      city: form.city,
      locality: form.locality,
      bhk: form.bhk,
    };

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: newMessages.map(m => ({ role: m.role, content: m.content })),
          estimate_context: estimateContext,
        }),
      });

      // If backend has Anthropic API key configured and returns streaming response
      if (res.ok) {
        const reader = res.body.getReader();
        const decoder = new TextDecoder();

        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        let doneReading = false;
        while (!doneReading) {
          const { done, value } = await reader.read();
          if (done) {
            doneReading = true;
            break;
          }
          const chunk = decoder.decode(value, { stream: true });
          setMessages(prev => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: updated[lastIdx].content + chunk,
            };
            return updated;
          });
        }
      } else {
        // Zero-cost native grounded advisory fallback
        const responseText = getGroundedAdvisorResponse(textToSend, estimateContext);
        await streamFallbackText(responseText);
      }
    } catch {
      // Offline / zero-cost fallback
      const responseText = getGroundedAdvisorResponse(textToSend, estimateContext);
      await streamFallbackText(responseText);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-7 shadow-2xl flex flex-col h-[580px]">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              Model-Grounded AI Advisor
            </h2>
            <p className="text-[11px] text-slate-400">
              Real-time reasoning strictly grounded in current property valuation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-semibold">
          <Zap className="h-3 w-3" />
          <span>Active • 100% Free</span>
        </div>
      </div>

      {/* Message history */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1 text-sm">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 ${
              m.role === 'user' ? 'flex-row-reverse' : ''
            }`}
          >
            <div
              className={`h-7 w-7 rounded-lg flex items-center justify-center shrink-0 text-xs ${
                m.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/50'
              }`}
            >
              {m.role === 'user' ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
            </div>

            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 leading-relaxed ${
                m.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none text-xs sm:text-sm'
              }`}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
            </div>
          </div>
        ))}

        {loading && messages[messages.length - 1]?.role === 'user' && (
          <div className="flex items-center gap-2 text-xs text-slate-400 italic py-1">
            <RefreshCw className="h-3.5 w-3.5 animate-spin text-emerald-400" />
            Synthesizing response grounded in model figures...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Prompt chips */}
      <div className="pt-2 pb-3 flex flex-wrap gap-1.5 shrink-0">
        {quickPrompts.map((q, i) => (
          <button
            key={i}
            onClick={() => handleSend(q)}
            disabled={loading || !estimate}
            className="text-[11px] bg-slate-900 hover:bg-slate-850 text-slate-300 border border-slate-800 hover:border-slate-700 px-2.5 py-1 rounded-full transition-all disabled:opacity-40 cursor-pointer"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input row */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2 pt-2 border-t border-slate-800 shrink-0"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading || !estimate}
          placeholder={
            !estimate 
              ? 'Run an estimate first to consult the AI advisor...' 
              : 'Ask about EMI, RBI LTV cap, or stamp duty...'
          }
          className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim() || !estimate}
          className="h-10 px-4 rounded-xl font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all disabled:opacity-50 flex items-center justify-center shrink-0 cursor-pointer shadow-lg shadow-emerald-500/10"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
