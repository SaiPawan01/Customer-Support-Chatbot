import { Mail } from 'lucide-react';

import PropTypes from 'prop-types';


EmailInput.propTypes = {
  data: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
  handleInputChange: PropTypes.func.isRequired,
  otpSent: PropTypes.bool,
  emailVerified: PropTypes.bool,
  isLogin: PropTypes.bool,
  handleEmailVerification: PropTypes.func,
  children: PropTypes.node
};


export default function EmailInput({data, errors, handleInputChange, otpSent=true, emailVerified=true, isLogin=true, handleEmailVerification=null, children}){
    const emailFieldSize = emailVerified ? 'w-full' : 'w-[75%]'
    return <div>
      <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
        Email Address
      </label>
      <div className="relative">
        <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
        <input
          type="email"
          name="email"
          value={data.email}
          onChange={handleInputChange}
          placeholder="you@example.com"
          className={`${isLogin ? 'w-full' : emailFieldSize} pl-10 pr-4 py-2 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition ${errors.email ? 'border-red-500' : 'border-slate-600'
            }`}
        />
        {(!emailVerified && !otpSent && !isLogin) && (
          <button
            type="button"
            className="ml-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition"
            onClick={handleEmailVerification}
          >
            Verify
          </button>
        )}
      </div>
      {children}
    </div>
}