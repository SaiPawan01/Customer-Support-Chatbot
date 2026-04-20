import { useContext, useEffect, useCallback } from 'react';

import SidebarWindow from '../components/ChatbotPage/SidebarWindow';
import BotHeader from '../components/ChatbotPage/BotHeader';
import BotInput from '../components/ChatbotPage/BotInput';
import MessageArea from '../components/ChatbotPage/MessageArea';
import { ChatbotContext } from '../context/Context.jsx';

export default function ChatbotInterface() {
  const { messages, messagesEndRef  } = useContext(ChatbotContext)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  },[messagesEndRef]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return (
    <div className="flex h-screen bg-slate-900">
      <SidebarWindow />
      <div className="flex-1 flex flex-col">
        <BotHeader />
        <MessageArea />
        <BotInput />
      </div>
    </div>
  );
}