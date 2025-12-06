// frontend/src/components/MessageBubble.jsx
import React from "react";
import { motion } from "framer-motion";

export default function MessageBubble({ m }) {
  const isUser = m.from === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="flex-none mr-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 text-white flex items-center justify-center shadow">
            🤖
          </div>
        </div>
      )}

      <div
        className={`max-w-[78%] px-4 py-3 rounded-2xl text-sm ${
          isUser
            ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none"
            : "bg-neutral-800/75 text-neutral-100 rounded-bl-none"
        }`}
      >
        {m.text}
      </div>

      {isUser && (
        <div className="flex-none ml-3">
          <div className="w-10 h-10 rounded-full bg-neutral-700 flex items-center justify-center text-white">
            🙋
          </div>
        </div>
      )}
    </motion.div>
  );
}
