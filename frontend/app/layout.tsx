import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import Header from "@/components/Header";
import { Toaster } from "@/components/ui/toaster";
import { SidebarProvider } from "@/components/ui/sidebar";
import AppSidebar from "@/components/AppSidebar";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Dive Finder",
  description: "Find the best dive locations around the world",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased h-dvh flex flex-col dark`}
      >
        <SidebarProvider
          className={`${geistSans.variable} ${geistMono.variable} antialiased h-dvh flex flex-row dark`}
          defaultOpen={false}
        >
          <AppSidebar />
          <div className="flex flex-col w-full h-full">
            <Header />
            <main className="bg-gradient-to-r from-slate-900 via-cyan-700 to-slate-900 animate-gradient-x flex-1 flex flex-col items-center">
              {children}
            </main>
          </div>
          <Toaster />
        </SidebarProvider>
      </body>
    </html>
  );
}
