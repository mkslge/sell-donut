import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-10 border-b bg-background/90 backdrop-blur">
      <nav
        className="mx-auto flex min-h-16 w-[min(1120px,calc(100%-2rem))] items-center justify-between gap-4"
        aria-label="Main navigation"
      >
        <Link className="text-lg font-bold tracking-normal" href="/">
          SellDonut
        </Link>
        <div className="flex items-center gap-2">
          <Button asChild variant="ghost">
            <Link href="/">Search</Link>
          </Button>
          <Button asChild>
            <Link href="/rate">Rate seller</Link>
          </Button>
        </div>
      </nav>
    </header>
  );
}
