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


export const createConversation = (data) => {
    const token = localStorage.getItem('access_token')
    if(token){
        return api.post("api/chatbot/create/conversation",{
            title: data.title,
        },{
            headers :{
                Authorization: `Bearer ${token}`
            }
        });
    }
}


export const deleteConversation = (id) => {
    const encoded_id = encodeURIComponent(id);
    const token = localStorage.getItem('access_token')
    if(token){
        return api.delete(`api/chatbot/delete/conversation/${encoded_id}`,{
            headers:{
                Authorization: `Bearer ${token}`
            }
        })
    }
}


export const escalateToAgent = (conversationId) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        return api.post(`api/chatbot/send/email`,{conversation_id:conversationId}, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });
    }
}