"use client";

import { useState, useRef, useEffect, type FormEvent } from "react";
import { Send, Bot, User, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const welcomeMessage: Message = {
  id: "welcome",
  role: "assistant",
  content:
    "你好！我是你的小红书营销AI助手。告诉我你想创建什么内容吧！\n\n我可以帮你：\n• 🎯 分析目标人群和热门趋势\n• ✍️ 生成小红书笔记文案\n• 🎨 推荐最佳视觉风格\n• 📊 优化内容投放策略",
  timestamp: new Date(),
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isTyping]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    // Simulated AI response
    setTimeout(() => {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "收到！让我分析一下你的需求...\n\n基于当前小红书的热门趋势，我建议使用「治愈系插画」风格，搭配温柔种草的语气来呈现。这种组合在目标人群中的互动率最高。\n\n需要我直接生成完整的笔记方案吗？",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setIsTyping(false);
    }, 1500);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  return (
    <div className="flex h-full flex-col">
      {/* Messages area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-4 py-6 space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "flex gap-3",
                msg.role === "user" ? "flex-row-reverse" : "flex-row",
              )}
            >
              {/* Avatar */}
              <div
                className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                  msg.role === "assistant"
                    ? "bg-gradient-to-br from-primary to-primary-light"
                    : "bg-stone-200",
                )}
              >
                {msg.role === "assistant" ? (
                  <Bot className="h-4 w-4 text-white" />
                ) : (
                  <User className="h-4 w-4 text-stone-600" />
                )}
              </div>

              {/* Bubble */}
              <div
                className={cn(
                  "max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                  msg.role === "user"
                    ? "bg-primary text-white rounded-br-md"
                    : "bg-surface-raised border border-stone-200 text-stone-800 rounded-bl-md",
                )}
              >
                {msg.content.split("\n").map((line, i) => (
                  <p key={i} className={cn(i > 0 && "mt-1.5")}>
                    {line || <br />}
                  </p>
                ))}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-light">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="rounded-2xl rounded-bl-md border border-stone-200 bg-surface-raised px-4 py-3">
                <div className="flex gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-stone-400 [animation-delay:0ms]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-stone-400 [animation-delay:150ms]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-stone-400 [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-stone-200 bg-surface-raised px-4 py-4">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex max-w-3xl items-end gap-3"
        >
          <div className="relative flex-1">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入你的需求，Shift+Enter换行..."
              rows={1}
              className="max-h-32 min-h-[44px] w-full resize-none rounded-xl border border-stone-300 bg-white px-4 py-3 pr-12 text-sm text-stone-900 placeholder:text-stone-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary text-white shadow-sm transition-all hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-4.5 w-4.5" />
          </button>
        </form>
        <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-stone-400">
          AI助手基于品牌规则生成内容，请审核后再发布
        </p>
      </div>
    </div>
  );
}
