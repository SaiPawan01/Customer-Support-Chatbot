import React, { useState } from "react";
import { User, ArrowRight } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser, loginUser, sendOtp, verifyOtp } from '../../api/auth.api.js';

import EmailInput from "../../elements/EmailInput.jsx";
import OtpInput from "../../elements/OtpInput.jsx";

import PropTypes from 'prop-types';
import PasswordInput from "../../elements/PasswordInput.jsx";

Form.propTypes = {
  isLogin: PropTypes.bool.isRequired,
  setIsLogin: PropTypes.func.isRequired,
  formData: PropTypes.object.isRequired,
  setFormData: PropTypes.func.isRequired,
  errors: PropTypes.object.isRequired,
  setErrors: PropTypes.func.isRequired,
}


export default function Form({ isLogin, setIsLogin, formData, setFormData, errors, setErrors }) {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState({password: false, confirmPassword: false});
  const [loading, setLoading] = useState(false);
  const [emailVerified, setEmailVerified] = useState(false);
  const [otpSent, setOtpSent] = useState(false);



  // Sends OTP to the user's email for verification during signup
  const handleEmailVerification = async () => {
    try {
      const response = await sendOtp(formData.email);

      if (response?.data?.success) {
        setOtpSent(true);
      }
      else if (!response?.data?.success) {
        setErrors({ email: response?.data?.message || 'something went wrong' });
      }
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        email: error.response?.data?.message || 'Failed to send OTP. Please try again.'
      }));
    }
  }



  // Verifies the OTP entered by the user during signup
  const handleOTPVerification = async () => {
    try {
      const response = await verifyOtp(formData.email, formData.otp);
      if (response?.data?.success) {
        setEmailVerified(true);
        setOtpSent(false);
      }
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        otp: error.response?.data?.message || "Invalid OTP"
      }));
    }
  };



  // Handles input changes for all form fields and clears errors for the specific field being edited
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };



  // Validates email format using a regular expression
  const validateEmailRegex = (email) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$/;
    return emailRegex.test(email);
  };



  // Validates the email field and checks if it's verified during signup
  const validateEmail = (email, newErrors) => {
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmailRegex(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    } else if (!isLogin && !emailVerified) {
      newErrors.email = 'Please verify your email';
    }
    return newErrors;
  }



  // Validates the password field and checks for minimum length requirement
  const validatePassword = (password, newErrors) => {
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    return newErrors;
  }



  const validateRegisterFields = (newErrors) => {
    if (formData.firstName === '') {
      newErrors.firstName = 'First name is required';
    }

    if (formData.lastName === '') {
      newErrors.lastName = 'Last name is required';
    }

    if (formData.confirmPassword === '') {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (formData.agreeTerms === false) {
      newErrors.agreeTerms = 'You must agree to the terms';
    }

    return newErrors;
  }


  // handles user registration
  const handleRegister = async () => {
    formData.fullName = formData.firstName + formData.lastName;
    const data = {
      email: formData.email,
      password: formData.password,
      username: formData.fullName,
      first_name: formData.firstName,
      last_name: formData.lastName,
    };

    try {
      const response = await registerUser(data);
      if (response?.data?.success) {
        setLoading(false);
        setIsLogin(true);
        setEmailVerified(false);
        setFormData({
          email: '',
          password: '',
          confirmPassword: '',
          firstName: '',
          lastName: '',
          agreeTerms: false,
          otp: ''
        });
        setErrors({});
      }
    }
    catch(error){
      setErrors({
        submit: error.response?.data?.message || 'Something went wrong. Please try again.'
      });
    }
    finally{
      setLoading(false);
    }
  }


  // handles user login
  const handleLogin = async () => {
    try {
      const response = await loginUser({
        email: formData.email,
        password: formData.password
      });
      if (response?.data?.success) {
        localStorage.setItem('access_token', response.data.access_token);
        console.log("Login successful:", response.data);
        setLoading(false);
        navigate('/chatbot');
      }
      else {
        throw new Error(response?.data?.message);
      }
    }
    catch (error) {
      setErrors({
        submit: error.message || 'An error occurred. Please try again.'
      });
    }
    finally{
      setLoading(false);
    }
  }


  // Resets email verification and OTP status when the email field is changed
  const handleEmailChange = (e) => {
    handleInputChange(e)
    if (emailVerified) {
      setEmailVerified(false);
    }
    if (otpSent) {
      setOtpSent(false);
    }
  }


  // Handles form submission for both login and signup
  const handleSubmit = async (e) => {
    e.preventDefault();
    let newErrors = {};

    // Validation
    newErrors = validateEmail(formData.email, newErrors);
    newErrors = validatePassword(formData.password, newErrors);
    if (isLogin === false) {
      newErrors = validateRegisterFields(newErrors);
    }

    // If there are validation errors, set them in state and prevent form submission
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      // post request to backend API for signup
      setLoading(true);
      if (isLogin === false) {
        await handleRegister();
      }
      else {
        await handleLogin();
      }
    } catch (error) {
      setLoading(false);
      setErrors({
        submit: error.response?.data?.message || 'An error occurred. Please try again.'
      });
    }
  };

  
  return <form onSubmit={handleSubmit} className="space-y-3">
    {/* Full Name Field (Signup only) */}
    {!isLogin && (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="firstName" className="block text-sm font-medium text-slate-300 mb-2">
            First Name
          </label>
          <div className="relative">
            <User className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
            <input
              type="text"
              name="firstName"
              value={formData.firstName}
              onChange={handleInputChange}
              placeholder="John Doe"
              className={`w-full pl-10 pr-4 py-2 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition ${errors.fullName == null ? 'border-slate-600' : 'border-red-500'}`}
            />
          </div>
          {errors.firstName && (
            <p className="text-red-400 text-sm mt-1">{errors.firstName}</p>
          )}
        </div>

        <div>
          <label htmlFor="lastName" className="block text-sm font-medium text-slate-300 mb-2">
            Last Name
          </label>
          <div className="relative">
            <User className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
            <input
              type="text"
              name="lastName"
              value={formData.lastName}
              onChange={handleInputChange}
              placeholder="John Doe"
              className={`w-full pl-10 pr-4 py-2 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition ${errors.fullName ? 'border-red-500' : 'border-slate-600'
                }`}
            />
          </div>
          {errors.lastName && (
            <p className="text-red-400 text-sm mt-1">{errors.lastName}</p>
          )}
        </div>

      </div>
    )}



    {/* Email Field */}
    <EmailInput data={formData} errors={errors} handleInputChange={handleEmailChange} otpSent={otpSent} emailVerified={emailVerified} isLogin={isLogin} handleEmailVerification={handleEmailVerification}>
      {otpSent && !emailVerified && (
        <p className="text-yellow-400 text-sm mt-1">
          Please check your email for the OTP.
        </p>
      )}
      {emailVerified && (
        <p className="text-yellow-400 text-sm mt-1">
          Email verified successfully.
        </p>
      )}
      {errors.email && (
        <p className="text-red-400 text-sm mt-1">{errors.email}</p>
      )}
    </EmailInput>



    {/* OTP Field */}
    {(!isLogin && otpSent) && <OtpInput data={formData} errors={errors} handleInputChange={handleInputChange} isLogin={isLogin} emailVerified={emailVerified} handleOTPVerification={handleOTPVerification}>
      {errors.otp && (
        <p className="text-red-400 text-sm mt-1">{errors.otp}</p>
      )}
      </OtpInput>}



    {/* Password Field */}
    <PasswordInput data={formData} errors={errors} handleInputChange={handleInputChange} showPassword={showPassword} setShowPassword={setShowPassword} />


    {/* Confirm Password Field (Signup only) */}
    {!isLogin && (
      <PasswordInput data={formData} errors={errors} handleInputChange={handleInputChange} showPassword={showPassword} setShowPassword={setShowPassword} confirmPassword={true}/>
    )}

    {/* Forgot Password Link (Login only) */}
    {isLogin && (
      <div className="flex justify-end">
        <Link
          to="/forgot-password"
          className="text-sm text-blue-400 hover:text-blue-300 transition"
        >
          Forgot password?
        </Link>
      </div>
    )}

    {/* Terms & Conditions (Signup only) */}
    {!isLogin && (
      <div className="flex items-start gap-2">
        <input
          type="checkbox"
          name="agreeTerms"
          checked={formData.agreeTerms}
          onChange={handleInputChange}
          className="w-4 h-4 rounded border-slate-600 text-blue-600 focus:ring-2 focus:ring-blue-500 mt-1 cursor-pointer"
        />
        <label className="text-sm text-slate-300">
          I agree to the{' '}
          <a href="/terms-of-service" className="text-blue-400 hover:text-blue-300">
            Terms of Service
          </a>{' '}
          and{' '}
          <a href="/privacy-policy" className="text-blue-400 hover:text-blue-300">
            Privacy Policy
          </a>
        </label>
      </div>
    )}
    {errors.agreeTerms && (
      <p className="text-red-400 text-sm">{errors.agreeTerms}</p>
    )}

    {/* Submit Error */}
    {errors.submit && (
      <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm">
        {errors.submit}
      </div>
    )}

    {/* Submit Button */}
    <button
      type="submit"
      disabled={loading}
      className="w-full bg-linear-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-2 rounded-lg transition-all duration-300 flex items-center justify-center gap-2"
    >
      {loading ? (
        <>
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          Signing In...
        </>
      ) : (
        <>
          {isLogin ? 'Login' : 'Create Account'}
          <ArrowRight className="w-4 h-4" />
        </>
      )}
    </button>
  </form>
}
