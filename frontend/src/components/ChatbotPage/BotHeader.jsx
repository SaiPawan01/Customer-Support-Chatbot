import React, { useState } from 'react';
import { Menu, Trash2} from 'lucide-react'

import Modal from './Modal';

function BotHeader({setShowSettings, setSidebarOpen, sidebarOpen, showSettings, activeConversation, conversations, setConversations}){
    const [modalState, setModalState] = useState(false);

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
            <Trash2 onClick={() => setModalState(!modalState)} className="w-6 h-6" />
          </button>
        </div>


         <Modal isOpen={modalState} activeConversation={activeConversation} modalState={modalState} setModalState={setModalState} conversations={conversations} setConversations={setConversations} />
        
    </>
}

export default BotHeader;