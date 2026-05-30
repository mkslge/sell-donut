import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "SellDonut",
  description: "Community seller ratings for DonutSMP trades.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header className="topbar">
            <nav className="container nav" aria-label="Main navigation">
              <Link className="brand" href="/">
                SellDonut
              </Link>
              <div className="navlinks">
                <Link href="/">Search</Link>
                <Link href="/rate">Rate seller</Link>
              </div>
            </nav>
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
