import { MessageCircle, Zap, Shield } from "lucide-react";

const feautres = [
    {
      icon: <MessageCircle className="w-8 h-8" />,
      title: "Natural Language Understanding",
      description: "Ask questions in plain English. Our AI understands context and provides accurate responses instantly."
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Instant Responses",
      description: "Get answers from your knowledge base in seconds. No more waiting for support tickets."
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Smart Escalation",
      description: "Uncertain questions are automatically routed to human experts for review and knowledge enhancement."
    }
];

export default feautres;