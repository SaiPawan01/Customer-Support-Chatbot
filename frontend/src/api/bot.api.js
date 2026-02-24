import api from "./axios.js";


export const getBotReply = (userMessage) => {
    const token = localStorage.getItem('access_token');

    if (token) {
        return api.post("api/chatbot/create/message",{
            conversation_id: userMessage.conversation_id,
            message: userMessage.content
        }, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });
    }
};