
import { Lock, Eye, EyeOff } from 'lucide-react';
import PropTypes from 'prop-types';

PasswordInput.propTypes = {
    data: PropTypes.object.isRequired,
    errors: PropTypes.object.isRequired,
    handleInputChange: PropTypes.func.isRequired,
    showPassword: PropTypes.object.isRequired,
    setShowPassword: PropTypes.func.isRequired,
    confirmPassword: PropTypes.bool
}

export default function PasswordInput({data, errors, handleInputChange, showPassword, setShowPassword, confirmPassword=false}) {

    const passwordToggleState = confirmPassword ? showPassword.confirmPassword : showPassword.password;
    const passwordValue = confirmPassword ? data.confirmPassword : data.password;
    const fieldName = confirmPassword ? 'confirmPassword' : 'password';

    return <div>
      <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
        Password
      </label>
      <div className="relative">
        <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
        <input
          type={passwordToggleState ? 'text' : 'password'}
          name={fieldName}
          value={passwordValue}
          onChange={handleInputChange}
          placeholder="••••••••"
          className={`w-full pl-10 pr-10 py-2 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition ${errors.password ? 'border-red-500' : 'border-slate-600'
            }`}
        />
        <button
          type="button"
          onClick={() => setShowPassword(prev => ({...prev, [fieldName]: !prev[fieldName]}))}
          className="absolute right-3 top-3 text-slate-500 hover:text-slate-300 transition"
        >
          {passwordToggleState ? (
            <EyeOff className="w-5 h-5" />
          ) : (
            <Eye className="w-5 h-5" />
          )}
        </button>
      </div>
      {errors.password && (
        <p className="text-red-400 text-sm mt-1">{errors.password}</p>
      )}
    </div>
}