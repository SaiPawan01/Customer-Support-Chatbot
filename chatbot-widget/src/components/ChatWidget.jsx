import { useState, useEffect, useRef } from "react";
import { generateResponse } from "../api/api.js";


import propTypes from "prop-types";

ChatWidget.propTypes = {
  config: propTypes.shape({
    apiUrl: propTypes.string.isRequired,
    clientId: propTypes.string.isRequired,
    theme: propTypes.shape({
      primary: propTypes.string,
      background: propTypes.string,
      surface: propTypes.string,
      userBubble: propTypes.string,
      botBubble: propTypes.string,
      text: propTypes.string,
    }),
  }),
}

export default function ChatWidget({ config = {} }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState(() => {
    const saved = sessionStorage.getItem("chat_messages");
    return saved ? JSON.parse(saved) : [];
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  // 🎨 Default Theme
  const defaultTheme = {
    primary: "#2563eb",
    background: "#334155",
    surface: "#1e293b",
    userBubble: "#475569",
    botBubble: "#1e293b",
    text: "#f1f5f9",
  };

  const theme = {
    ...defaultTheme,
    ...(config.theme || {})
  };

  // Save chat
  useEffect(() => {
    sessionStorage.setItem("chat_messages", JSON.stringify(messages));
  }, [messages]);


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = input;
    const updated = [...messages, { role: "user", text: userMsg }];

    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const response = await generateResponse(userMsg);
      console.log(response)

      if (response.data.success){
        setMessages([
          ...updated,
          { role: "bot", text: response.data.data.reply || "No response" }
        ]);
      } else {
        throw new Error("Invalid response");
      }

    } catch (error) {
      console.error(error);

      const errorMessage =
        error?.response?.data?.message ||
        "⚠️ Something went wrong. Please try again.";

      setMessages([
        ...updated,
        { role: "bot", text: errorMessage }
      ]);
    }

    setLoading(false);
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-8 right-8 z-9999 rounded-full p-3 shadow-xl text-white text-lg transition"
        style={{ backgroundColor: theme.primary }}
      >
        💬
      </button>

      {/* Chat Window */}
      {open && (
        <div
          className="fixed bottom-24 right-6 z-9999 w-120 h-140 rounded-2xl shadow-2xl flex flex-col border"
          style={{
            backgroundColor: theme.background,
            color: theme.text,
            borderColor: "#475569"
          }}
        >

          {/* Header */}
          <div
            className="p-4 font-semibold text-lg rounded-t-2xl border-b"
            style={{
              backgroundColor: theme.surface,
              borderColor: "#475569"
            }}
          >
            Support Bot AI
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto no-scrollbar space-y-3 text-[15px] scroll-smooth">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className="max-w-[75%] px-4 py-3 rounded-xl"
                style={{
                  marginLeft: msg.role === "user" ? "auto" : "0",
                  backgroundColor:
                    msg.role === "user"
                      ? theme.userBubble
                      : theme.botBubble,
                  color: theme.text
                }}
              >
                {msg.text}
              </div>
            ))}

            {loading && (
              <div
                className="px-4 py-3 rounded-xl w-fit text-[15px]"
                style={{ backgroundColor: theme.userBubble }}
              >
                Typing...
              </div>
            )}

            {/* Auto-scroll anchor */}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-2">
            <div
              className="flex border-t rounded-2xl"
              style={{
                backgroundColor: theme.surface,
                borderColor: "#475569"
              }}
            >
              <input
                className="flex-1 px-4 py-3 outline-none text-[15px] bg-transparent"
                style={{ color: theme.text }}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type a message..."
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              />
              <button
                onClick={sendMessage}
                className="px-5 text-white text-[15px] rounded-tr-2xl rounded-br-2xl"
                style={{ backgroundColor: theme.primary }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}