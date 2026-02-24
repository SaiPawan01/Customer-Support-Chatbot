import api from "./axios.js";


export const fetchALLConversations = () => {
    const token = localStorage.getItem('access_token');

    if (token) {
        return api.get("api/chatbot/fetch/conversations", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });
    }
};


export const fetchALLMessages = (id) => {
    const token = localStorage.getItem('access_token')

    if(token){
        return api.post("api/chatbot/fetch/message-history",{
            conversation_id : id
        }, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });
    }
}

