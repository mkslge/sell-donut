import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { VisitLogger } from "@/components/VisitLogger";

export const metadata: Metadata = {
  title: "DonutTrades",
  description: "Community seller ratings for DonutSMP trades.",
  icons: {
    icon: "/icon.jpg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-foreground">
        <div className="min-h-screen">
          <Navbar />
          <VisitLogger />
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
