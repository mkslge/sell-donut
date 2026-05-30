import type { PropsWithChildren } from "react";

export function TwoColumnSection({ children }: PropsWithChildren) {
  return (
    <section className="grid gap-6 pb-12 lg:grid-cols-[1.1fr_0.9fr]">
      {children}
    </section>
  );
}
