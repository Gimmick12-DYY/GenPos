"use client";

import { useState, useRef, useEffect, type FormEvent } from "react";
import { Send, Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface NotePackageFromApi {
  id: string;
  ranking_score?: number | null;
  style_family?: string | null;
  compliance_status: string;
  review_status: string;
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
  const [authReady, setAuthReady] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    ensureAuth()
      .then(() => setAuthReady(true))
      .catch((e) => setAuthError(e.message));
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isTyping]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || !authReady) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);
    setAuthError(null);

    try {
      const merchantId = getMerchantId();
      if (!merchantId) throw new Error("未获取到商户信息，请刷新重试");

      const data = await api.post<{
        response: string;
        intent?: string | null;
        note_packages?: Array<NotePackageFromApi & { id: string }> | null;
      }>("/chat/message", { merchant_id: merchantId, message: text });

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response || "请求已处理。",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);

      // If we had note_packages we could render them inline; API returns list or null
      if (data.note_packages?.length) {
        // Optional: append a system message or render cards below
        // For now we just show the text response.
      }
    } catch (err) {
      let msg = err instanceof Error ? err.message : "请求失败，请重试";
      if (/failed to fetch|network error/i.test(msg)) {
        msg = "无法连接后端（可能是请求超时或 API 暂时不可用）。请检查 Railway 上 API 是否运行正常、OPENAI_API_KEY 是否已配置，或稍后重试。";
      }
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `生成过程遇到问题：${msg}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  if (authError && !authReady) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center text-sm text-red-800">
          <p className="font-medium">无法连接后端</p>
          <p className="mt-1">{authError}</p>
          <p className="mt-2 text-stone-500">
            请确认已创建商户并已启动 API 服务。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
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
            disabled={!input.trim() || isTyping || !authReady}
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
