import { useState } from 'react';
import { MessageCircle } from 'lucide-react';

import Form from '../components/AuthPage/Form.jsx';

export default function LoginPage() {

  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    agreeTerms: false,
    otp:''
  });
  const [errors, setErrors] = useState({});


  // Toggle between Login and Signup modes
  const toggleAuthMode = () => {
    setIsLogin(!isLogin);
    setErrors({});
    setFormData({
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: '',
      agreeTerms: false,
      otp: ''
    });
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      {/* Background Elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>

      <div className="w-full max-w-md relative z-10">
        { isLogin && <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <MessageCircle className="w-10 h-10 text-blue-500" />
            <span className="text-2xl font-bold text-white">SupportBot AI</span>
          </div>
          <p className="text-slate-400">AI-Powered Customer Support</p>
        </div>}

        {/* Card Container */}
        <div className="bg-slate-800/50 backdrop-blur-md border border-slate-700/50 rounded-2xl p-8 shadow-2xl">

          {/* Form */}
          <Form 
            isLogin={isLogin}
            setIsLogin={setIsLogin}
            formData={formData}
            setFormData={setFormData}
            errors={errors}
            setErrors={setErrors}
          />


          {/* Toggle Message */}
          <p className="text-center text-slate-400 text-sm mt-6">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <button
              type="button"
              onClick={toggleAuthMode}
              className="text-blue-400 hover:text-blue-300 font-semibold transition"
            >
              {isLogin ? 'Sign up' : 'Login'}
            </button>
          </p>
        </div>

        {/* Footer */}
        <p className="text-center text-slate-500 text-xs mt-6">
          By continuing, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}