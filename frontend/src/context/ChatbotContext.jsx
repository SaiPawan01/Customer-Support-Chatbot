import { createContext, useState, useRef } from "react";

import { v4 as uuidv4 } from 'uuid';

import { fetchALLMessages } from '../api/sidebar.api'
import { getBotReply } from '../api/bot.api';

export const ChatbotContext = createContext({});

export function ChatbotContextProvider({ children }) {
    const [messages, setMessages] = useState({
        messagesData: [],
        conversationStatus: 'active',
    });
    const [conversations, setConversations] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [newConversation, setNewConversation] = useState(false);
    const [loading, setLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [showSettings, setShowSettings] = useState(false);
    const [activeConversation, setActiveConversation] = useState(null);
    const [escalationStatus, setEscalationStatus] = useState({ escalation: false, messageId: null });
    const messagesEndRef = useRef(null);


    // Fetch messages for a given conversation ID and update the state with the retrieved messages and conversation status
    const fetchMessages = async (id, status) => {
        try {
            const response = await fetchALLMessages(id);
            console.log(response)
            if (response.data && response.data.data) {
                setMessages({
                    messagesData: response.data.data,
                    conversationStatus: status
                });
            }
        }
        catch (error) {
            console.log(`error fetching message ${error}`);
        }
    }


    
    // Handle sending a message: create a user message object, update the messages state, clear the input, and fetch the bot's reply. If the bot's reply indicates escalation, update the escalation status.
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
        setEscalationStatus({ escalation: false, messageId: null });
        setMessages(prev => {
            return {
                ...prev,
                messagesData: [...prev.messagesData, userMessage]
            };
        });
        setInputValue('');
        setLoading(true);
        try {
            const response = await getBotReply(userMessage)
            console.log(response)
            if (response.data && response.data.data) {
                const botReply = {
                    id: response.data.data.id,
                    role: 'assistant',
                    content: response.data.data.message,
                    created_at: response.data.data.created_at,
                    source: response.data.data.source,
                    confidence: response.data.data.confidence,
                }
                if (response.data.data.escalation_status == true) {
                    setEscalationStatus({ escalation: true, messageId: botReply.id })
                }
                setMessages(prev => {
                    return {
                        ...prev,
                        messagesData: [...prev.messagesData, botReply]
                    };
                });
                setLoading(false);
            }
            else {
                console.log(response)
            }
        } catch (error) {
            setLoading(false);
            console.log("error occured while geting bot reply" + error)
        }

    };

    const value = {
        messages, setMessages,
        conversations, setConversations,
        inputValue, setInputValue,
        newConversation, setNewConversation,
        loading, setLoading,
        sidebarOpen, setSidebarOpen,
        showSettings, setShowSettings,
        activeConversation, setActiveConversation,
        escalationStatus, setEscalationStatus,

        messagesEndRef,

        fetchMessages,
        handleSendMessage,
    };
    return (
        <ChatbotContext.Provider value={value}>
            {children}
        </ChatbotContext.Provider>
    );
}