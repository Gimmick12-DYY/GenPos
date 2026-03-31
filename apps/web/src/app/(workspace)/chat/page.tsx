"use client";

import { useState, useRef, useEffect, type FormEvent } from "react";
import { Send, Bot, User, Trash2, Sparkles } from "lucide-react";
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
  const [clearing, setClearing] = useState(false);
  const [chatNotice, setChatNotice] = useState<string | null>(null);
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

  async function handleClearChat() {
    if (!authReady || clearing || isTyping) return;
    if (
      !window.confirm(
        "确定清空当前对话？服务器上的本条会话记录也会被删除，且无法恢复。"
      )
    ) {
      return;
    }
    const merchantId = getMerchantId();
    const sid = sessionIdRef.current || ensureSessionId();
    if (!merchantId) return;
    setClearing(true);
    setChatNotice(null);
    try {
      await api.delete<{ deleted: number }>(
        `/chat/session?merchant_id=${merchantId}&session_id=${sid}`
      );
      setMessages([welcomeMessage]);
    } catch (e) {
      setChatNotice(e instanceof Error ? e.message : "清空失败");
    } finally {
      setClearing(false);
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
        <div className="rounded-2xl border border-red-200/80 bg-red-50 p-8 text-center text-sm text-red-900 shadow-sm">
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
    <div className="flex h-full min-h-0 flex-col bg-gradient-to-b from-stone-100/50 via-surface to-surface">
      {/* Session chrome: title + context + clear — one card, not a floating orphan button */}
      <div className="shrink-0 px-4 pb-2 pt-4 sm:px-6">
        <div className="mx-auto max-w-3xl overflow-hidden rounded-2xl border border-stone-200/70 bg-white/95 shadow-sm ring-1 ring-stone-100/80">
          <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
            <div className="flex min-w-0 gap-3">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 ring-1 ring-primary/10">
                <Sparkles className="h-5 w-5 text-primary" aria-hidden />
              </div>
              <div className="min-w-0">
                <h2 className="text-base font-semibold tracking-tight text-stone-900">
                  营销助手
                </h2>
                <p className="mt-0.5 text-xs leading-relaxed text-stone-500">
                  结合「我的产品库」与你对话；内容按商户隔离并同步保存。
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => void handleClearChat()}
              disabled={clearing || !authReady || isTyping}
              className="inline-flex shrink-0 items-center justify-center gap-2 self-start rounded-xl border border-stone-200/80 bg-stone-50/80 px-3 py-2 text-xs font-medium text-stone-600 transition-colors hover:border-stone-300 hover:bg-stone-100 hover:text-stone-900 disabled:cursor-not-allowed disabled:opacity-50 sm:self-center"
            >
              <Trash2 className="h-3.5 w-3.5" aria-hidden />
              {clearing ? "清空中…" : "清空会话"}
            </button>
          </div>
          {chatNotice && (
            <div className="border-t border-amber-100 bg-amber-50/90 px-4 py-2.5 text-center text-xs text-amber-950">
              {chatNotice}
            </div>
          )}
        </div>
      </div>

      <div
        ref={scrollRef}
        className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 sm:px-6"
      >
        <div className="mx-auto max-w-3xl space-y-5 pb-8 pt-2">
          {messages
            .filter(
              (m) =>
                !(m.role === "assistant" && m.content === "" && isTyping),
            )
            .map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "group flex gap-3",
                msg.role === "user" ? "flex-row-reverse" : "flex-row",
              )}
            >
              <div
                className={cn(
                  "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full shadow-sm ring-2 ring-white",
                  msg.role === "assistant"
                    ? "bg-gradient-to-br from-primary to-primary-light"
                    : "bg-gradient-to-br from-stone-200 to-stone-300",
                )}
              >
                {msg.role === "assistant" ? (
                  <Bot className="h-4 w-4 text-white" />
                ) : (
                  <User className="h-4 w-4 text-stone-700" />
                )}
              </div>
              <div className="flex max-w-[min(85%,28rem)] flex-col gap-1.5">
                <div
                  className={cn(
                    "rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-md shadow-stone-900/[0.04]",
                    msg.role === "user"
                      ? "rounded-br-md bg-gradient-to-br from-primary to-primary-dark text-white"
                      : "rounded-bl-md border border-stone-200/90 bg-white text-stone-800",
                  )}
                >
                  {msg.content.split("\n").map((line, i) => (
                    <p key={i} className={cn(i > 0 && "mt-1.5")}>
                      {line || <br />}
                    </p>
                  ))}
                </div>
                {msg.notePackageId && (
                  <p className="px-1 text-[11px] text-stone-500">
                    已生成笔记包 →「待审核」
                    <span className="ml-1 font-mono text-stone-400">
                      {msg.notePackageId.slice(0, 8)}…
                    </span>
                  </p>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex gap-3">
              <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-light shadow-sm ring-2 ring-white">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="rounded-2xl rounded-bl-md border border-stone-200/90 bg-white px-4 py-3 shadow-md shadow-stone-900/[0.04]">
                <div className="flex gap-1.5">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:0ms]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-primary/50 [animation-delay:150ms]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-primary/40 [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="shrink-0 border-t border-stone-200/60 bg-white/90 px-4 pb-4 pt-3 backdrop-blur-md supports-[backdrop-filter]:bg-white/75 sm:px-6">
        <div className="mx-auto max-w-3xl">
          <form
            onSubmit={(ev) => void handleSubmit(ev)}
            className="flex flex-col gap-2 rounded-2xl border border-stone-200/80 bg-stone-50/80 p-2 shadow-lg shadow-stone-900/[0.06] ring-1 ring-stone-100 sm:flex-row sm:items-end"
          >
            <label className="sr-only" htmlFor="chat-input">
              消息内容
            </label>
            <textarea
              id="chat-input"
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="描述需求或 @ 产品…（Enter 发送，Shift+Enter 换行）"
              rows={1}
              className="input-surface max-h-36 min-h-[48px] flex-1 resize-none rounded-xl border-0 bg-white px-4 py-3 text-sm text-stone-900 shadow-inner shadow-stone-900/5 placeholder:text-stone-400 focus:ring-2 focus:ring-primary/20"
            />
            <button
              type="submit"
              disabled={!input.trim() || isTyping || !authReady}
              title="发送"
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-dark text-white shadow-md shadow-primary/20 transition-all hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-50 sm:h-[48px] sm:w-12"
            >
              <Send className="h-5 w-5" aria-hidden />
            </button>
          </form>
          <p className="mt-2.5 text-center text-[11px] leading-relaxed text-stone-400">
            生成结果可在「待审核」查看封面与配图；上方「清空会话」会删除本条对话的服务器记录。
          </p>
        </div>
      </div>
    </div>
  );
}
