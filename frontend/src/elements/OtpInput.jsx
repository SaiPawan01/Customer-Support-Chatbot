import { Code } from 'lucide-react';

import PropTypes from 'prop-types';

OtpInput.propTypes = {
  data: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
  handleInputChange: PropTypes.func.isRequired,
  isLogin: PropTypes.bool,
  emailVerified: PropTypes.bool,
  handleOTPVerification: PropTypes.func,
  children: PropTypes.node
};

export default function OtpInput({data, errors, handleInputChange, isLogin=true, emailVerified=true, handleOTPVerification=null, children}){
    return <div>
      <label htmlFor="otp" className="block text-sm font-medium text-slate-300 mb-2">
        Enter OTP
      </label>
      <div className="relative">
        <Code className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
        <input
          type="text"
          name="otp"
          value={data.otp}
          onChange={handleInputChange}
          placeholder="Enter six digit OTP..."
          className={`${isLogin ? 'w-full' : 'w-[75%]'} pl-10 pr-4 py-2 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition ${errors.email ? 'border-red-500' : 'border-slate-600'
            }`}
        />
        {(!emailVerified && !isLogin) && (
          <button
            type="button"
            className="ml-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition"
            onClick={handleOTPVerification}
          >
            Verify
          </button>
        )}
      </div>
      {children}
    </div>
}