import React, { useState, useContext } from 'react';
import { Menu, Trash2} from 'lucide-react'

import Modal from './Modal';
import { escalateToAgent,deleteConversation } from '../../api/bot.api.js';

import { ChatbotContext } from '../../context/Context.jsx';


function BotHeader() {
    const {setShowSettings, setSidebarOpen, showSettings, activeConversation, setActiveConversation, setConversations, escalationStatus, setEscalationStatus, setMessages} = useContext(ChatbotContext);
    const [modalState, setModalState] = useState(false);
    const [convEscalationModalStatus, setConvEscalationModalStatus] = useState(false);


    const handleEscalationModalClose = () => {
      setConvEscalationModalStatus(prev => !prev)
    }

    const handleEscalationModalConfirm = () => {
      handleEscalation(activeConversation);
      setConvEscalationModalStatus(prev => !prev)
      setEscalationStatus({ escalation: false, messageId: null });
      setMessages(prev => {
        return {
          ...prev, conversationStatus: 'pending'
        }
      })
    }

    const handleEscalation = (conversationId) => {
      try{
        const response = escalateToAgent(conversationId);
        if(response.success === true){
          alert("Issue escalated to human agent successfully.")
        }
      }
      catch(error){
        console.log(`Something went wrong while escalating the issue: ${error}`)
      }
    }

    const handleDeleteModalClose = () => {
        setModalState(prev => !prev)
    }
    const handleDeleteModalConfirm = async () => {
        try{
            await deleteConversation(activeConversation);
            setModalState(prev => !prev)
            setConversations(prevConversations =>
            prevConversations.filter(
                (conversation) => conversation.id !== activeConversation
            ));
            setActiveConversation(null);
        }
        catch(error){ 
            console.log(`something went wrong while deleting the conversation ${error}`)
        }
    }
    return <>
    <div className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(prev => !prev)}
              className="lg:hidden text-slate-400 hover:text-white"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div>
              <h2 className="text-white font-semibold">Support Assistant</h2>
              <p className="text-sm text-slate-400">Always ready to help</p>
            </div>
          </div>
          <div className='flex items-center justify-center gap-3'>
            {escalationStatus.escalation && (
              <button onClick={() => setConvEscalationModalStatus(prev => !prev)} className="ml-4 w-30 h-10 bg-white text-red-600 px-3 py-1 rounded-md text-sm font-medium hover:bg-red-50">
                Escalate Issue
              </button>
            )}
            <button
            onClick={() => setShowSettings(!showSettings)}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-700 transition"
          >
            {activeConversation != null && <Trash2 onClick={() => setModalState(prev => !prev)} className="w-6 h-6" /> }
          </button>
          </div>
          
        </div>


         <Modal btnDisplayMessage="Delete" displayMessage="Are you sure you want to delete this conversation?" isOpen={modalState} setModalState={setModalState} setConversations={setConversations} handleModalClose={handleDeleteModalClose} handleModalConfirm={handleDeleteModalConfirm} />
         <Modal btnDisplayMessage="Escalate" displayMessage="Are you sure you want to escalate this issue?" isOpen={convEscalationModalStatus} setModalState={setConvEscalationModalStatus} handleModalClose={handleEscalationModalClose} handleModalConfirm={handleEscalationModalConfirm} />
    </>
}

export default BotHeader;