import { useEffect } from 'react';

import Footer from '../components/LandingPage/Footer';
import Navbar from '../components/LandingPage/Navbar';
import HeroSection from '../components/LandingPage/HeroSection';
import StatsSection from '../components/LandingPage/StatsSection';
import Features from '../components/LandingPage/Features';
import Benefits from '../components/LandingPage/Benefits';


export default function LandingPage() {
  useEffect(() => {
    const SCRIPT_ID = "chatbot-widget-script";
    const STYLE_ID = "chatbot-widget-style";


    if (document.getElementById(SCRIPT_ID)) return;

    // Create stylesheet
    const link = document.createElement("link");
    link.id = STYLE_ID;
    link.rel = "stylesheet";
    link.href = "http://localhost:3000/chatbot-widget.css";

    // Create script
    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.src = "http://localhost:3000/chatbot-widget.js";
    script.async = true;

    script.integrity = import.meta.env.VITE_SCRIPT_INTEGRITY_HASH;
    script.crossOrigin = "anonymous";

    script.onload = () => {
      if (globalThis.ChatbotWidget?.init) {
        globalThis.ChatbotWidget.init({
          apiUrl: import.meta.env.VITE_API_URL,
          clientId: "test123",
        });
      }
    };

    document.head.appendChild(link);
    document.body.appendChild(script);

    return () => {
      document.getElementById("chatbot-widget-root")?.remove();
      document.getElementById(SCRIPT_ID)?.remove();
      document.getElementById(STYLE_ID)?.remove();
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