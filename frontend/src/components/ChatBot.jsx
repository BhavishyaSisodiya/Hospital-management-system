import { useState, useRef, useEffect } from "react";

import { sendChatMessage } from "../api/chat";
import { useAuth } from "../context/AuthContext";

function ChatBot() {
    const { accountType } = useAuth();
    const isPatient = accountType === "patient";

    const [open, setOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            role: "assistant",
            content: isPatient
                ? "Hello! I can help you find doctors, check schedules, book or cancel appointments."
                : "Hello! I'm the internal assistant. I can look up patients, doctors, bed occupancy, stock and today's schedule.",
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const bodyRef = useRef(null);

    useEffect(() => {
        if (bodyRef.current) {
            bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
        }
    }, [messages, open]);

    useEffect(() => {
        setMessages([
            {
                role: "assistant",
                content: isPatient
                    ? "Hello! I can help you find doctors, check schedules, book or cancel appointments."
                    : "Hello! I'm the internal assistant. I can look up patients, doctors, bed occupancy, stock and today's schedule.",
            },
        ]);
    }, [isPatient]);

    const handleSend = async () => {
        const text = input.trim();
        if (!text || loading) return;

        const updated = [...messages, { role: "user", content: text }];
        setMessages(updated);
        setInput("");
        setLoading(true);

        try {
            const { reply } = await sendChatMessage(updated);
            setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content:
                        error.response?.data?.detail ||
                        "Sorry, I could not reach the AI service.",
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chatbot">
            {open && (
                <div className="chatbot-window">
                    <div className="chatbot-header">
                        <h3>{isPatient ? "HMS Support" : "Staff Assistant"}</h3>
                        <button className="chatbot-close" onClick={() => setOpen(false)}>
                            ×
                        </button>
                    </div>
                    <div className="chatbot-body" ref={bodyRef}>
                        {messages.map((msg, index) => (
                            <div key={index} className={`chatbot-msg chatbot-${msg.role}`}>
                                {msg.content}
                            </div>
                        ))}
                        {loading && <div className="chatbot-msg chatbot-assistant">Thinking...</div>}
                    </div>
                    <div className="chatbot-input">
                        <input
                            type="text"
                            placeholder="Ask me anything..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") handleSend();
                            }}
                        />
                        <button onClick={handleSend} disabled={loading}>
                            Send
                        </button>
                    </div>
                </div>
            )}

            <button
                className="chatbot-toggle"
                onClick={() => setOpen((prev) => !prev)}
                title={isPatient ? "HMS Support" : "Staff Assistant"}
            >
                {open ? "✕" : "💬"}
            </button>
        </div>
    );
}

export default ChatBot;