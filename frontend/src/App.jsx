import React from 'react'
import { Routes, Route } from 'react-router-dom'


import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage';
import ChatbotInterface from './pages/ChatbotInterface';
import ProtectedRoute from './components/ProtectedRoute';
import ChatbotContextProvider from './context/ChatbotContext';
import ForgotPassword from './components/AuthPage/ForgetPassword';

function App() {
  return <Routes>
    <Route path="/" element={<LandingPage />} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/forgot-password" element={<ForgotPassword />} />
    <Route path="/chatbot" element={
      <ProtectedRoute>
        <ChatbotContextProvider>
          <ChatbotInterface />
        </ChatbotContextProvider>
      </ProtectedRoute>
    } />
  </Routes>
}

export default App;