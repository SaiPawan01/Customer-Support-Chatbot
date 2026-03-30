import React from 'react'
import {Send} from 'lucide-react'

function BotInput({handleSendMessage, inputValue, setInputValue, loading, activeConversation, conversationStatus }){

    return <>
     <div className="bg-slate-800 border-t border-slate-700 px-6 py-4">
          <form onSubmit={handleSendMessage} className="space-y-3">
            { (activeConversation && conversationStatus !== 'pending') && (<div className="flex gap-3 items-end">
              <div className="relative flex-1 flex items-center bg-slate-700 border border-slate-600 rounded-xl focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  disabled={activeConversation === null ? true : false}
                  placeholder={activeConversation === null ? "select a conversation" : "start asking questions"}
                  className="flex-1 bg-transparent text-white placeholder-slate-500 px-4 py-3 outline-none text-sm"
                />
              </div>

              {/* Send Button */}
              <button
                type="submit"
                disabled={!inputValue.trim() || loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white p-3 rounded-xl transition disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>)}

            {/* Info Text */}
            <p className="text-xs text-slate-500 text-center">
              SupportBot AI can help but for sensitive issues, contact our support team.
            </p>
          </form>
        </div>
    </>
}

export default BotInput;