import axios from "axios";

const VITE_API_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: VITE_API_URL,
  headers: {
    "Content-Type": "application/json"
  }
});


export const generateResponse = (message) => {
    return api.post('api/chatbot/widget/response', { message });
}

export const generateSuggestions = (history) => {
    return api.post('api/widget/suggestions', { history });
}