import React from 'react'
import { Paperclip, FileText, ThumbsUp, ThumbsDown, Copy } from 'lucide-react'
import { createConversation } from '../../api/bot.api';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";


function MessageArea({ messages,
    setMessages,
    loading,
    messagesEndRef,
    getConfidenceColor,
    newConversation,
    setNewConversation,
    setConversations,
    setActiveConversation,
    activeConversation }) {


    const handleSubmit = async (e) => {
        e.preventDefault();

        const data = {
            title: e.target.title.value.trim()
        }

        try {
            const response = await createConversation(data);
            console.log(response.data.data)
            if (response.data && response.data.data) {
                setConversations(prev => [response.data.data, ...prev])
                setActiveConversation(response.data.data.id)
                setNewConversation(false)
                setMessages([])
            }
        }
        catch (error) {
            console.log("FULL ERROR:", error.response?.data);
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
                            Send
                        </button>
                    </form>
                </div>
            </div>) : (messages || []).map((message, idx) => (
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