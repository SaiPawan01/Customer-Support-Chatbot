import { useState } from "react";
import { sendResetPasswordOtp, verifyResetPasswordOtp, resetPassword } from "../../api/auth.api.js";
import { useNavigate, Link } from "react-router-dom";
import { MessageCircle } from 'lucide-react';

import EmailInput from "../../elements/EmailInput.jsx";
import OtpInput from "../../elements/OtpInput.jsx";

export default function ForgotPassword() {
    const [data, setData] = useState({ "email": '', "otp": '', 'password': '', 'confirmPassword': '' });

    // formStaus 0 -> email verification, 1 -> otp verification, 2 -> password reset
    const [formStatus, setFormStatus] = useState(0);
    const [showPassword, setShowPassword] = useState({'password': false, 'confirmPassword': false});
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    const navigate = useNavigate();


    // handles Input change for all form fields and updates the corresponding state values
    function handleInputChange(e) {
        const { name, value } = e.target;
        setData(prev => ({ ...prev, [name]: value }))
        setErrors(prev => ({...prev, [name]:''}))
        if(name === 'email'){
            setFormStatus(0);
            setData({email : value, otp: '', password:'', confirmPassword: ''})
        }
    }


    // Validates email format using a regular expression
    const validateEmailRegex = (email) => {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$/;
        return emailRegex.test(email);
    };


    // sends OTP to the provided email if it's valid and updates the component state based on the response
    const sendOtp = async () => {
        if (validateEmailRegex(data.email) === false) {
            setErrors({ email: 'Please enter a valid email address' });
            return;
        }
        
        try{
            setLoading(true);
            const response = await sendResetPasswordOtp(data.email);
            if (response?.data?.success === true) {
                setFormStatus(1);
                setErrors({});
            }
        }catch(error){
            setErrors({ email: error?.response?.data?.message || 'Error sending OTP' });
        }
        finally{
            setLoading(false);
        }
    }


    // verifies the entered OTP and updates the component state to show password fields if OTP is correct
    const verifyOtp = async () => {
        if (data.otp === '' || data.otp.length !== 6) {
            setErrors({ otp: 'Enter valid 6-digit OTP' });
            return;
        }

        try{
            setLoading(true);
            const response = await verifyResetPasswordOtp(data.email, data.otp);
            console.log(response)
            if (response?.data?.success) {
                setFormStatus(2);
                setErrors({});
            }
        }catch(error){
            setErrors({ otp: error?.response?.data?.message || 'Error verifying OTP' });
        }
        finally{
            setLoading(false);
        }
    }


    // validates the new password and confirm password fields and sends a request to reset the password if validations pass
    const resetPasswordHandler = async () => {
        let newErrors = {};

        if (!data.password || data.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }

        if (data.password !== data.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        try{
            setLoading(true);
            const response = await resetPassword(data.email, data.password);
            if (response?.data?.success) {
                setErrors({});
                setLoading(false);
                setFormStatus(3);
                setTimeout(() => {
                    navigate('/login');
                }, 3000);
            }
        }
        catch(error){
            setErrors({password: error?.response?.data?.message || 'Error resetting password'})
        }
    }


    // handles form submission by determining which step of the password reset process the user is in and calling the appropriate function to handle that step
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if(formStatus === 0){
                await sendOtp();
            }
            else if (formStatus === 1) {
                await verifyOtp();
            }
            else {
                await resetPasswordHandler();
            }
        } catch (error) {
            console.log(error?.response?.data?.message);
        }
    };


    return (
        <div className="min-h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>

            <div className="w-full max-w-md relative z-10">
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center gap-2 mb-4">
                        <MessageCircle className="w-10 h-10 text-blue-500" />
                        <span className="text-2xl font-bold text-white">SupportBot AI</span>
                    </div>
                    <p className="text-slate-400">AI-Powered Customer Support</p>
                </div>

                {/* Card Container */}
                <div className="bg-slate-800/50 backdrop-blur-md border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
                    <form onSubmit={handleSubmit} className="space-y-3">

                        {/* Email Field */}
                        <EmailInput data={data} errors={errors} handleInputChange={handleInputChange}>
                            {errors.email && (
                                <p className="text-red-400 text-sm mt-1">{errors.email}</p>
                            )}
                            {formStatus === 2 && <p className="text-green-400 text-sm mt-1">OTP verified! Please enter your new password.</p>}
                        </EmailInput>


                        {/* OTP Field */}
                        {formStatus === 1 && <OtpInput data={data} errors={errors} handleInputChange={handleInputChange} isLogin={false} emailVerified={false} handleOTPVerification={verifyOtp}>
                            {errors.otp && (
                                <p className="text-red-400 text-sm mt-1">{errors.otp}</p>
                            )}
                            </OtpInput>}



                        {formStatus === 2 && <PasswordInput data={formData} errors={errors} handleInputChange={handleInputChange} showPassword={showPassword} setShowPassword={setShowPassword} />}


                        {formStatus === 2 && <PasswordInput data={formData} errors={errors} handleInputChange={handleInputChange} showPassword={showPassword} setShowPassword={setShowPassword} confirmPassword={true}/>}

                        {formStatus == 3 && <p className="text-green-400 text-sm mt-1">Password reset successful!</p>}


                        <div className="flex justify-end">
                            <Link
                                to="/login"
                                className="text-sm text-blue-400 hover:text-blue-300 transition"
                            >
                                Sign In Instead
                            </Link>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-linear-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-2 rounded-lg transition-all duration-300 flex items-center justify-center gap-2"
                        >
                            {formStatus == 0 && 'Send OTP'}
                            {formStatus == 1 && 'Verify OTP'}
                            {formStatus == 2 && 'Change Password'}
                            {formStatus == 3 && 'Redirecting to Login...'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}