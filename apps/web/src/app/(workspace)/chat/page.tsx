"use client";

import { useState, useRef, useEffect, type FormEvent } from "react";
import { Send, Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, postSse } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

const SESSION_KEY = "genpos_chat_session_id";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  notePackageId?: string | null;
}

interface ChatHistoryRow {
  id: string;
  role: string;
  content: string;
  created_at: string;
  metadata_json?: { note_package_id?: string } | null;
}

function ensureSessionId(): string {
  if (typeof window === "undefined") return "";
  let s = sessionStorage.getItem(SESSION_KEY);
  if (!s) {
    s = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, s);
  }
  return s;
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
  const sessionIdRef = useRef<string>("");

  useEffect(() => {
    sessionIdRef.current = ensureSessionId();
  }, []);

  useEffect(() => {
    ensureAuth()
      .then(() => setAuthReady(true))
      .catch((e) => setAuthError(e.message));
  }, []);

  useEffect(() => {
    if (!authReady) return;
    const merchantId = getMerchantId();
    const sid = sessionIdRef.current || ensureSessionId();
    if (!merchantId || !sid) return;
    api
      .get<ChatHistoryRow[]>(
        `/chat/messages?merchant_id=${merchantId}&session_id=${sid}&limit=80`
      )
      .then((rows) => {
        if (!rows.length) {
          setMessages([welcomeMessage]);
          return;
        }
        setMessages(
          rows.map((r) => ({
            id: r.id,
            role: r.role === "user" ? "user" : "assistant",
            content: r.content,
            timestamp: new Date(r.created_at),
            notePackageId: r.metadata_json?.note_package_id ?? null,
          }))
        );
      })
      .catch(() => {
        setMessages([welcomeMessage]);
      });
  }, [authReady]);

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

    const merchantId = getMerchantId();
    if (!merchantId) {
      setAuthError("未获取到商户信息，请刷新重试");
      return;
    }
    const sid = sessionIdRef.current || ensureSessionId();

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    const streamAssistantId = (Date.now() + 1).toString();
    const assistantShell: Message = {
      id: streamAssistantId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg, assistantShell]);
    setInput("");
    setIsTyping(true);
    setAuthError(null);

    try {
      await postSse(
        "/chat/stream",
        {
          merchant_id: merchantId,
          session_id: sid,
          message: text,
          objective: "seeding",
        },
        (ev) => {
          if (ev.type === "token" && typeof ev.text === "string") {
            const t = ev.text;
            setMessages((prev) => {
              const next = [...prev];
              const i = next.findIndex((m) => m.id === streamAssistantId);
              if (i === -1) return prev;
              next[i] = {
                ...next[i],
                content: next[i].content + t,
              };
              return next;
            });
          }
          if (ev.type === "done") {
            const response = typeof ev.response === "string" ? ev.response : "";
            const np =
              typeof ev.note_package_id === "string" ? ev.note_package_id : null;
            setMessages((prev) => {
              const next = [...prev];
              const i = next.findIndex((m) => m.id === streamAssistantId);
              if (i === -1) return prev;
              next[i] = {
                ...next[i],
                content: response || next[i].content || "完成。",
                notePackageId: np,
              };
              return next;
            });
          }
          if (ev.type === "error") {
            const msg =
              typeof ev.message === "string" ? ev.message : "生成失败";
            setMessages((prev) => {
              const next = [...prev];
              const i = next.findIndex((m) => m.id === streamAssistantId);
              if (i === -1) return prev;
              next[i] = { ...next[i], content: `出错：${msg}` };
              return next;
            });
          }
        }
      );
    } catch (err) {
      let msg = err instanceof Error ? err.message : "请求失败，请重试";
      if (/failed to fetch|network error/i.test(msg)) {
        msg =
          "无法连接后端（可能是请求超时或 API 暂时不可用）。请检查服务是否运行、OPENAI_API_KEY 是否已配置。";
      }
      setMessages((prev) => {
        const next = [...prev];
        const i = next.findIndex((m) => m.id === streamAssistantId);
        if (i === -1)
          return [
            ...prev,
            {
              id: String(Date.now()),
              role: "assistant",
              content: `生成过程遇到问题：${msg}`,
              timestamp: new Date(),
            },
          ];
        next[i] = { ...next[i], content: `生成过程遇到问题：${msg}` };
        return next;
      });
    } finally {
      setIsTyping(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSubmit(e);
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
        <div className="mx-auto max-w-3xl space-y-6 px-4 py-6">
          {messages
            .filter(
              (m) =>
                !(m.role === "assistant" && m.content === "" && isTyping),
            )
            .map((msg) => (
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
              <div className="flex max-w-[75%] flex-col gap-2">
                <div
                  className={cn(
                    "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                    msg.role === "user"
                      ? "rounded-br-md bg-primary text-white"
                      : "rounded-bl-md border border-stone-200 bg-surface-raised text-stone-800",
                  )}
                >
                  {msg.content.split("\n").map((line, i) => (
                    <p key={i} className={cn(i > 0 && "mt-1.5")}>
                      {line || <br />}
                    </p>
                  ))}
                </div>
                {msg.notePackageId && (
                  <p className="text-xs text-stone-500">
                    已生成笔记包，可前往「待审核」查看（ID 前缀{" "}
                    {msg.notePackageId.slice(0, 8)}…）
                  </p>
                )}
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
          onSubmit={(ev) => void handleSubmit(ev)}
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
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary text-white shadow-sm transition-all hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send className="h-4.5 w-4.5" />
          </button>
        </form>
        <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-stone-400">
          对话会保存于此浏览器会话；生成完成后可在「待审核」查看封面与文案
        </p>
      </div>
    </div>
  );
}
