import { Trash2, X } from "lucide-react";
import { deleteConversation } from "../../api/bot.api";



export default function Modal({ isOpen, activeConversation, modalState, setModalState, conversation, setConversation }) {
    
    const handleClose = () => {
        setModalState(!modalState)
    }
    const handleconform = async () => {
        try{
            await deleteConversation(activeConversation);
            setModalState(prev => !prev)
            // const arr = conversation.filter((conversation) => conversation.id !== activeConversation)
            // console.log(arr)
            // console.log(activeConversation)
            // setConversation(arr)
        }
        catch(error){ 
            console.log(`something went wrong while deleting the conversation ${error}`)
        }
        
    }
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">

            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={handleClose}
            />

            {/* Modal */}
            <div className="relative w-80 rounded-2xl shadow-2xl p-6
                      bg-slate-800 border border-slate-700
                      animate-in fade-in zoom-in-95 duration-200">

                {/* Close */}
                <button
                    onClick={handleClose}
                    className="absolute top-3 right-3 text-slate-400 hover:text-slate-200 transition"
                >
                    <X size={18} />
                </button>

                {/* Icon */}
                <div className="flex justify-center mb-4">
                    <div className="p-3 rounded-full bg-red-500/10">
                        <Trash2 size={22} className="text-red-500" />
                    </div>
                </div>

                {/* Title */}
                <h2 className="text-lg font-semibold text-slate-200 text-center mb-2">
                    Delete Conversation?
                </h2>

                {/* Description */}
                <p className="text-sm text-slate-400 text-center mb-6">
                    This action cannot be undone.
                </p>

                {/* Actions */}
                <div className="flex gap-3">
                    <button
                        onClick={handleClose}
                        className="flex-1 py-2 rounded-xl border border-slate-600
                       text-slate-300 text-sm
                       hover:bg-slate-700 transition"
                    >
                        Cancel
                    </button>

                    <button
                        onClick={handleconform}
                        className="flex-1 py-2 rounded-xl bg-red-500
                       text-white text-sm
                       hover:bg-red-600 active:scale-95
                       transition"
                    >
                        Delete
                    </button>
                </div>
            </div>
        </div>
    );
}