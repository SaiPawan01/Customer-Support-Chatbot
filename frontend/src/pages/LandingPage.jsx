import { useState, useEffect } from 'react';

import Footer from '../components/LandingPage/Footer';
import Navbar from '../components/LandingPage/Navbar';
import HeroSection from '../components/LandingPage/HeroSection';
import StatsSection from '../components/LandingPage/StatsSection';
import Features from '../components/LandingPage/Features';
import Benefits from '../components/LandingPage/Benefits';


export default function LandingPage() {
  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "http://localhost:3000/chatbot-widget.css";

    // ✅ Load JS
    const script = document.createElement("script");
    script.src = "http://localhost:3000/chatbot-widget.js";
    script.async = true;

    script.onload = () => {
      window.ChatbotWidget.init({
        apiUrl: import.meta.env.VITE_API_URL,
        clientId: "test123",
      });
    };

    document.head.appendChild(link);
    document.body.appendChild(script);

    return () => {
      // cleanup
      document.getElementById("chatbot-widget-root")?.remove();
      link.remove();
      script.remove();
    };
  }, []);

  return (
    <div className="min-h-screen bg-linear-to-b from-slate-900 via-slate-800 to-slate-900">
        <Navbar />
        <HeroSection />
        <StatsSection />
        <Benefits />
        <Features />
        <Footer />
    </div>
  );
}