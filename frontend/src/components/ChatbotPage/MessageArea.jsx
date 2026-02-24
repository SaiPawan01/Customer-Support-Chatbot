import React from 'react'
import { Paperclip, FileText, ThumbsUp, ThumbsDown, Copy } from 'lucide-react'

function MessageArea({ messages,
    loading,
    messagesEndRef,
    handleFeedback,
    feedbackGiven,
    handleCopyMessage,
    getConfidenceColor }) {

    return <>
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
            {(messages || []).map((message, idx) => (
                <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    <div
                        className={`max-w-xs lg:max-w-2xl ${message.role === 'user'
                            ? 'bg-blue-600 text-white rounded-3xl rounded-tr-none'
                            : 'bg-slate-700 text-slate-100 rounded-3xl rounded-tl-none'
                            } px-6 py-4 space-y-3`}
                    >
                        {/* Message Text */}
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

                        {/* File Attachment (if any) */}
                        {message.file && (
                            <div className="bg-slate-600/50 rounded px-3 py-2 flex items-center gap-2 text-xs">
                                <Paperclip className="w-4 h-4" />
                                {message.file.name} ({message.file.size}KB)
                            </div>
                        )}

                        {/* Confidence Score & Sources (Bot only) */}
                        {message.role === 'assistant' &&
                            message.confidence !== null &&
                            message.confidence !== undefined && (
                                <div className="space-y-2 pt-2 border-t border-slate-600">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-slate-400">Confidence:</span>
                                        <span className={`text-xs font-semibold ${getConfidenceColor(message.confidence)}`}>
                                            {(message.confidence * 100).toFixed(0)}%
                                        </span>
                                    </div>

                                    {/* Sources */}
                                    {message.sources && message.sources.length > 0 && (
                                        <div className="space-y-1">
                                            <p className="text-xs text-slate-400">Sources:</p>
                                            {message.sources.map((source, srcIdx) => (
                                                <a
                                                    key={srcIdx}
                                                    href={source.url}
                                                    className="text-xs text-blue-300 hover:text-blue-200 flex items-center gap-1 transition"
                                                >
                                                    <FileText className="w-3 h-3" />
                                                    {source.title}
                                                </a>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                        {/* Feedback & Actions (Bot only) */}
                        {message.sender === 'bot' && idx > 0 && (
                            <div className="flex items-center gap-2 pt-2 border-t border-slate-600">
                                <button
                                    onClick={() => handleFeedback(message.id, true)}
                                    className={`p-1.5 rounded transition ${feedbackGiven?.[message.id] === 'positive'
                                        ? 'bg-green-500/30 text-green-400'
                                        : 'text-slate-400 hover:text-slate-200'
                                        }`}
                                    title="This was helpful"
                                >
                                    <ThumbsUp className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => handleFeedback(message.id, false)}
                                    className={`p-1.5 rounded transition ${feedbackGiven?.[message.id] === 'negative'
                                        ? 'bg-red-500/30 text-red-400'
                                        : 'text-slate-400 hover:text-slate-200'
                                        }`}
                                    title="This wasn't helpful"
                                >
                                    <ThumbsDown className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => handleCopyMessage(message.text)}
                                    className="p-1.5 rounded text-slate-400 hover:text-slate-200 transition"
                                    title="Copy message"
                                >
                                    <Copy className="w-4 h-4" />
                                </button>
                            </div>
                        )}

                        {/* Timestamp */}
                        <p className="text-xs text-slate-400 pt-1">
                            {new Date(message.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit'
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