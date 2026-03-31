import type { Metadata } from "next";
import { Inter, Noto_Sans_SC } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const notoSansSC = Noto_Sans_SC({
  subsets: ["latin"],
  variable: "--font-noto-sans-sc",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "GenPos - 小红书AI广告工作台",
  description: "小红书AI广告创意工作台 - 每日自动生成笔记，按需定制内容",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className={`${inter.variable} ${notoSansSC.variable}`}>
      <body className="min-h-screen bg-surface font-sans text-stone-900 antialiased [font-feature-settings:'cv02','cv03','cv04','cv11']">
        {children}
      </body>
    </html>
  );
}
