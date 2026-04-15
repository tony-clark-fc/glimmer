import type { Metadata } from "next";
import { Inter, Manrope } from "next/font/google";
import { Geist_Mono } from "next/font/google";
import "./globals.css";
import { WorkspaceNav } from "@/components/workspace-nav";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Glimmer",
  description: "Local-first AI project chief-of-staff",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${manrope.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        {/* Atmospheric background glows */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute top-[-10%] right-[-10%] w-[60%] h-[60%] bg-indigo-900/10 blur-[120px] rounded-full" />
          <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/5 blur-[100px] rounded-full" />
        </div>
        <WorkspaceNav />
        <main className="relative z-10 flex-1 w-full max-w-[960px] mx-auto px-6 md:px-0 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
