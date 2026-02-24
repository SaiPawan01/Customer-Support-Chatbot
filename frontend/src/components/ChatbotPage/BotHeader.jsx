import React from 'react';
import {Settings, Menu} from 'lucide-react'

function BotHeader({setShowSettings, setSidebarOpen, sidebarOpen, showSettings}){
    return <>
    <div className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden text-slate-400 hover:text-white"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div>
              <h2 className="text-white font-semibold">Support Assistant</h2>
              <p className="text-sm text-slate-400">Always ready to help</p>
            </div>
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-700 transition"
          >
            <Settings className="w-6 h-6" />
          </button>
        </div>
    </>
}

export default BotHeader;