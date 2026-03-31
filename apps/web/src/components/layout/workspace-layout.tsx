"use client";

import { Sidebar } from "./sidebar";
import { Header } from "./header";

export function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      <Sidebar />
      <div className="relative flex min-w-0 flex-1 flex-col overflow-hidden">
        <div
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_90%_50%_at_50%_-10%,rgba(232,115,74,0.07),transparent)]"
          aria-hidden
        />
        <Header />
        <main className="relative flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
