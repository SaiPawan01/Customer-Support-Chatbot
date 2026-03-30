import React from "react";

export default function Oauth() {
    return < div className = "grid grid-cols-2 gap-3" >
            <button
              type="button"
              className="border border-slate-600 hover:border-slate-500 text-slate-300 py-2 rounded-lg transition hover:bg-slate-700/30"
            >
              Google
            </button>
            <button
              type="button"
              className="border border-slate-600 hover:border-slate-500 text-slate-300 py-2 rounded-lg transition hover:bg-slate-700/30"
            >
              GitHub
            </button>
        </div >
}