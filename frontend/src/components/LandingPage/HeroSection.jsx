import React from 'react'
import { ArrowRight } from 'lucide-react'

import { verifyToken, refreshToken } from '../../api/auth.api'
import { useNavigate } from 'react-router-dom';

function HeroSection() {
  const navigate = useNavigate();
  

  const handleStart = async (tokenParam) => {
    const tok = tokenParam;
    if (!tok) {
      navigate('/login');
      return;
    }
    try {
      const response = await verifyToken(tok);
      if (response.data?.success) {
        navigate('/chatbot');
        return;
      }
      navigate('/login');
    }
    catch (verifyError) {
      console.error('Token verification failed:', verifyError);
      try{
        const data = await refreshToken();
        console.log('Refreshed token data:', data);
        navigate('/chatbot');
        return;
      }
      catch (refreshError){
        console.error('Token refresh failed:', refreshError);
        navigate('/login');
      }
    }
  }
  return <>
    {/* Hero Section */}
    <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto text-center">
        <div className="mb-8 inline-block">
          <span className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded-full text-sm font-semibold">
            🚀 AI-Powered Support Solution
          </span>
        </div>
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Intelligent Support That <span className="text-transparent bg-clip-text bg-linear-to-r from-blue-400 to-cyan-400">Works 24/7</span>
        </h1>
        <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
          Reduce support ticket volume by 70%. Provide instant, accurate answers to your customers and employees using AI-powered intelligent chatbot backed by your knowledge base.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button onClick={() => handleStart(localStorage.getItem('access_token'))} className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition transform hover:scale-105">
            Start  <ArrowRight className="w-5 h-5" />
          </button>
          <button className="border border-slate-500 hover:border-slate-300 text-white px-8 py-3 rounded-lg font-semibold transition">
            Watch Demo
          </button>
        </div>
      </div>
    </section>
  </>
}

export default HeroSection