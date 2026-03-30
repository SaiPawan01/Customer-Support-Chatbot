import React, { useEffect } from "react";
import { useState } from "react";
import {Plus, MessageCircle, LogOut, Search, Settings} from 'lucide-react'
import { useNavigate } from "react-router-dom";

import { logoutUser } from '../../api/auth.api.js'
import { fetchALLConversations } from "../../api/sidebar.api.js";

function SidebarWindow({sidebarOpen, fetchMessages, activeConversation, setActiveConversation, setNewConversation, conversations, setConversations, setEscalationStatus}) {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const response = await logoutUser();
            if (response.status === 200) {
                localStorage.removeItem('access_token');
                navigate('/login');
            }
        } catch (error) {
            console.error("Logout error:", error);
        }
    }

    const fetchConversations = async ()=>{
       try{
         const response = await fetchALLConversations();
         console.log(response)
         if(response.data && response.data.data){
            setConversations(response.data.data)
         }
         else{
            console.log("no data field")
         }
       }
       catch(error){
         console.log(`Something went wrong when fetching conversations: ${error}`)
       }
    }

    useEffect(() => {
        fetchConversations()
    }, []);

    return <>
        <div
            className={`${sidebarOpen ? 'w-64' : 'w-0'
                } bg-slate-800 border-r border-slate-700 transition-all duration-300 overflow-hidden flex flex-col`}
        >
            {/* Logo */}
            <div className="p-4 border-b border-slate-700 flex items-center gap-2">
                <MessageCircle className="w-6 h-6 text-blue-500" />
                <span className="text-white font-bold hidden sm:inline">SupportBot AI</span>
            </div>

            {/* New Chat Button */}
            <button
                onClick={()=>setNewConversation(true)}
                className="m-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-2 px-4 flex items-center justify-center gap-2 transition"
            >
                <Plus className="w-5 h-5" />
                New Chat
            </button>

            {/* Search */}
            <div className="px-4 mb-4">
                <div className="relative">
                    <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Search chats..."
                        className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                    />
                </div>
            </div>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto px-2">
                <p className="text-xs text-slate-400 px-2 py-2 uppercase font-semibold">Recent</p>
                {conversations.map(conv => (
                    <button
                        key={conv.id}
                        onClick={() =>{ 
                            setActiveConversation(conv.id),
                            setNewConversation(false);
                            fetchMessages(conv.id, conv.status);
                            setEscalationStatus({escalation: false, messageId: null});
                        }}
                        className={`w-full text-left px-4 py-3 rounded-lg mb-2 transition ${activeConversation === conv.id
                                ? 'bg-blue-600 text-white'
                                : 'text-slate-300 hover:bg-slate-700'
                            }`}
                    >
                        <p className="text-sm font-medium truncate">{conv.title}</p>
                        <p className="text-xs text-slate-400">{conv.date}</p>
                    </button>
                ))}
            </div>

            {/* Bottom Actions */}
            <div className="border-t border-slate-700 p-4 space-y-2">
                <button onClick={handleLogout} className="w-full flex items-center gap-3 text-slate-300 hover:text-white px-4 py-2 rounded-lg hover:bg-slate-700 transition">
                    <LogOut className="w-5 h-5" />
                    <span className="text-sm">Logout</span>
                </button>
            </div>
        </div>
    </>
}


export default SidebarWindow;