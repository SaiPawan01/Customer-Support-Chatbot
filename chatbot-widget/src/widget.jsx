import React from "react";
import { createRoot } from "react-dom/client";
import ChatWidget from "./components/ChatWidget.jsx";
import "./index.css";

export function init(config = {}) {
  if (document.getElementById("chatbot-widget-root")) return;

  const container = document.createElement("div");
  container.id = "chatbot-widget-root";
  document.body.appendChild(container);

  const root = createRoot(container);
  root.render(<ChatWidget config={config} />);
}

if (typeof globalThis !== "undefined") {
  globalThis.ChatbotWidget = { init };
}