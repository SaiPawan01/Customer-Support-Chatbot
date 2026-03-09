import { useState, useRef, useEffect } from 'react';

import SidebarWindow from '../components/ChatbotPage/SidebarWindow';
import BotHeader from '../components/ChatbotPage/BotHeader';
import BotInput from '../components/ChatbotPage/BotInput';
import MessageArea from '../components/ChatbotPage/MessageArea';

import { v4 as uuidv4 } from 'uuid';

import {fetchALLMessages} from '../api/sidebar.api'
import { getBotReply } from '../api/bot.api';

export default function ChatbotInterface() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "Hello! I'm SupportBot AI. How can I help you today?",
      role:'assistant',
      timestamp: new Date()
    }
  ]);
  const [conversations, setConversations] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [newConversation, setNewConversation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [activeConversation, setActiveConversation] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };


  const fetchMessages = async (id) => {
    try {
      const response = await fetchALLMessages(id);
      if (response.data && response.data.data) {
        setMessages(response.data.data)
      }
    }
    catch (error) {
      console.log(`error fetching message ${error}`);
    }
  }


  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = {
      id: uuidv4(),
      role: 'user',
      content: inputValue,
      conversation_id: activeConversation,
      created_at: new Date().toLocaleString()
    } 

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);
    try{
      const response = await getBotReply(userMessage)
      console.log(response)
      if(response.data && response.data.data){
        const botReply = {
          id: response.data.data.id,
          role:'assistant',
          content: response.data.data.message,
          created_at: response.data.data.created_at,
          source: response.data.data.source,
        }
        setMessages(prev => [...prev, botReply])
        setLoading(false);
      }
      else{
        console.log(response)
      }
    }catch(error){
      console.log("error occured while geting bot reply"+ error)
    }

  };

  

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-400';
    if (confidence >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };


  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Sidebar */}
      <SidebarWindow sidebarOpen={sidebarOpen} fetchMessages={fetchMessages} activeConversation={activeConversation} setActiveConversation={setActiveConversation} setNewConversation={setNewConversation} conversations={conversations} setConversations={setConversations} />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <BotHeader setShowSettings={setShowSettings} setSidebarOpen={setSidebarOpen} showSetting={showSettings} activeConversation={activeConversation} setActiveConversation={setActiveConversation} setConversations={setConversations} />

        {/* Messages Area */}
        <MessageArea messages={messages} loading={loading} messagesEndRef={messagesEndRef} getConfidenceColor={getConfidenceColor} newConversation={newConversation} setConversations={setConversations} setNewConversation={setNewConversation} setActiveConversation={setActiveConversation} activeConversation={activeConversation} />

        {/* Inpuzxsxt Area */}
        <BotInput handleSendMessage={handleSendMessage} inputValue={inputValue} setInputValue={setInputValue} loading={loading} activeConversation={activeConversation} />
      </div>
    </div>
  );
}