
import React, { useState, useRef, useEffect } from "react";
import MessageBubble from "./components/MessageBubble";
import { motion, AnimatePresence } from "framer-motion";

export default function ChatApp() {
  const [text, setText] = useState("");
  const [messages, setMessages] = useState([
    { id: 0, from: "bot", text: "Hello! I'm ReyMini. How can I help today?" }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const containerRef = useRef(null);
  const idRef = useRef(1);

  useEffect(() => {
    if (containerRef.current)
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
  }, [messages, isTyping]);

  const sendMessage = async () => {
    const raw = text.trim();
    if (!raw) return;

    const userMsg = { id: idRef.current++, from: "user", text: raw };
    setMessages((m) => [...m, userMsg]);
    setText("");
    setIsTyping(true);

    try {
      // <<< REPLACED URL: use your Render backend URL here >>>
      const res = await fetch("https://simplechatbot-chnk.onrender.com/reply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: raw })
      });
      const data = await res.json();

      // remove artificial delay to speed responses
      // await new Promise((r) => setTimeout(r, 300 + Math.min(700, Math.random() * 700)));

      setIsTyping(false);
      setMessages((m) => [
        ...m,
        { id: idRef.current++, from: "bot", text: data.answer || "No answer returned." }
      ]);
    } catch (err) {
      setIsTyping(false);
      setMessages((m) => [
        ...m,
        { id: idRef.current++, from: "bot", text: "Server unreachable — check backend." }
      ]);
      console.error("Reply fetch error:", err);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-dark-900 text-white flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
        className="w-full max-w-3xl rounded-2xl shadow-2xl bg-gradient-to-b from-neutral-900/70 to-neutral-950/60 border border-neutral-800 backdrop-blur-md overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-800">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full flex items-center justify-center bg-gradient-to-br from-indigo-500 via-cyan-400 to-pink-500 text-lg shadow">
              🤖
            </div>
            <div>
              <div className="text-lg font-semibold">ReyMini</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-xs text-neutral-400">Status</div>
            <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-sm" />
          </div>
        </div>

        {/* Chat area */}
        <main ref={containerRef} className="h-[68vh] overflow-auto px-6 py-5 space-y-3">
          <AnimatePresence initial={false}>
            {messages.map((m) => (
              <MessageBubble key={m.id} m={m} />
            ))}

            {isTyping && (
              <motion.div
                key="typing"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 6 }}
                transition={{ duration: 0.2 }}
                className="mb-2 flex justify-start"
              >
                <div className="flex-none mr-3">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center text-white">
                    🤖
                  </div>
                </div>

                <div className="rounded-2xl p-3 bg-neutral-800/80 text-neutral-100 max-w-md">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <motion.span animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 0.8 }} className="w-2 h-2 rounded-full bg-neutral-300 inline-block" />
                      <motion.span animate={{ y: [0, -8, 0] }} transition={{ repeat: Infinity, duration: 0.8, delay: 0.12 }} className="w-2 h-2 rounded-full bg-neutral-300 inline-block" />
                      <motion.span animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 0.8, delay: 0.24 }} className="w-2 h-2 rounded-full bg-neutral-300 inline-block" />
                    </div>
                    <div className="text-xs text-neutral-300">ReyMini is typing…</div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* Input */}
        <div className="px-6 py-4 border-t border-neutral-800 bg-gradient-to-t from-black/20 to-transparent">
          <div className="flex items-center gap-3">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={onKeyDown}
              rows={1}
              placeholder="Ask ReyMini..."
              className="flex-1 resize-none rounded-xl bg-neutral-900/60 border border-neutral-800 px-4 py-3 text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 transition"
            />

            <motion.button
              whileTap={{ scale: 0.97 }}
              whileHover={{ scale: 1.03 }}
              onClick={sendMessage}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-400 text-black font-semibold shadow-md"
            >
              Send
            </motion.button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
