import React, {useContext, useState} from 'react'
import { Paperclip, FileText, ThumbsUp, ThumbsDown, Copy } from 'lucide-react'
import { createConversation } from '../../api/bot.api';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatbotContext } from '../../context/ChatbotContext';

function MessageArea() {
    const { messages,
    setMessages,
    loading,
    messagesEndRef,
    newConversation,
    setNewConversation,
    setConversations,
    setActiveConversation,
    activeConversation,
    escalationStatus,
    fetchMessages,
} = useContext(ChatbotContext);

    const [error, setError] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if(e.target.title.value.trim() === ""){
            setError("Title cannot be empty");
            return;
        }
        setError(false);

        const data = {
            title: e.target.title.value.trim()
        }

        try {
            const response = await createConversation(data);
            console.log(response.data.data)
            if (response.data && response.data.data) {
                setConversations(prev => [response.data.data, ...prev])
                setActiveConversation(response.data.data.id)
                setNewConversation(false);
                await fetchMessages(response.data.data.id,'active');
            }
        }
        catch (error) {
            setActiveConversation(null);
            setNewConversation(false);
            console.log(`Error creating conversation: ${error}`);
        }
    }
    if (activeConversation == null && newConversation == false) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-center space-y-4">
                    <h2 className="text-xl font-semibold text-slate-300">
                        No Conversation Selected
                    </h2>

                    <p className="text-slate-400 text-sm">
                        Select a conversation from the sidebar or start a new one.
                    </p>
                </div>
            </div>
        );
    }

    // Determine the text color based on the confidence level of the bot's response: green for high confidence, yellow for medium confidence, and red for low confidence.
      const getConfidenceColor = (confidence) => {
        if (confidence >= 0.7) return 'text-green-400';
        if (confidence >= 0.5) return 'text-yellow-400';
        return 'text-red-400';
      };
    
    return <>
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
            {newConversation ? (<div className="flex justify-center items-center h-full">
                <div className="w-full max-w-xl bg-slate-700 rounded-3xl px-6 py-6 space-y-4 shadow-lg">
                    <p className="text-slate-300 text-sm">
                        Start a new conversation
                    </p>

                    <form
                        onSubmit={handleSubmit}
                        className="flex gap-3"
                    >
                        <input
                            type="text"
                            name="title"
                            placeholder="Enter conversation title..."
                            className="flex-1 bg-slate-600 text-slate-100 placeholder-slate-400 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />

                        <button
                            type="submit"
                            className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-3 rounded-2xl text-sm font-medium transition"
                        >
                            Create Conversation
                        </button>
                    </form>
                    {error && <p className="text-red-400 text-sm">{error}</p>}
                </div>
            </div>) : (messages.messagesData || []).map((message, idx) => (
                <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    <div
                        className={`max-w-xs lg:max-w-2xl ${message.role === 'user'
                            ? 'bg-slate-600 text-white rounded-3xl rounded-tr-none'
                            : 'bg-slate-700 text-slate-100 rounded-3xl rounded-tl-none'
                            } px-6 py-4 space-y-3`}
                    >
                        {/* Message Text */}
                        <div className="text-sm leading-relaxed [&>p]:my-2 
                                                            [&>h1]:my-3 
                                                            [&>h2]:my-3 
                                                            [&>ul]:my-2 ">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {message.content}
                            </ReactMarkdown>
                        </div>

                        {(escalationStatus.escalation == true && message.role == 'assistant' && escalationStatus.messageId === message.id) && <p>Need help from a human? Click the "Escalate Issue" button in the header to proceed.</p>}

                        {/* Confidence Score & Sources (Bot only) */}
                        {message.role === 'assistant' &&
                            message.confidence !== null &&
                            message.confidence !== undefined &&
                            (
                                <div className="space-y-2 pt-2 border-t border-slate-600">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-slate-400">Confidence:</span>
                                        <span className={`text-xs font-semibold ${getConfidenceColor(message.confidence)}`}>
                                            {(message.confidence * 100).toFixed(0)}%
                                        </span>
                                    </div>

                                    {/* Sources */}
                                    {(message.source && message.source.length) > 0 && (
                                        <div className="space-y-1">
                                            <p className="text-xs text-slate-400">Source:</p>
                                            {message.source.map((item, srcIdx) => (
                                                <h6
                                                    key={srcIdx}
                                                    className="text-xs text-blue-300 hover:text-blue-200 flex items-center gap-1 transition"
                                                >
                                                    {item}
                                                </h6>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}


                        {/* Timestamp */}
                        <p className="text-xs text-slate-400 pt-1">
                            {new Date(message.created_at).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                                month: '2-digit',
                                day: '2-digit'
                            })}
                        </p>
                    </div>
                </div>
            ))}

            {(messages.conversationStatus === 'pending' && activeConversation) && (
                <div className="bg-amber-400/10 border border-amber-400/30 text-amber-300 px-4 py-3 rounded-md font-medium flex items-center justify-center gap-2">

                    {/* <span className="text-lg">⚠️</span> */}

                    <p className="text-sm leading-relaxed">
                        This conversation has been escalated. Please check your email—our support team will contact you shortly.

                        <span className="text-amber-400 font-semibold ml-1">
                            Conversation ID: {activeConversation}
                        </span>
                    </p>

                </div>
            )}
            {/* Loading Indicator */}
            {loading && (
                <div className="flex justify-start">
                    <div className="bg-slate-700 text-slate-100 rounded-3xl rounded-tl-none px-6 py-4">
                        <div className="flex gap-2">
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                    </div>
                </div>
            )}

            <div ref={messagesEndRef} />
        </div>
    </>
}


export default MessageArea;