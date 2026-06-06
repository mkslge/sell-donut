import type { PropsWithChildren, ReactNode } from "react";

type PageHeroProps = PropsWithChildren<{
  title: string;
  description: string;
  eyebrow?: ReactNode;
  action?: ReactNode;
  visual?: ReactNode;
}>;

export function PageHero({
  title,
  description,
  eyebrow,
  action,
  visual,
  children,
}: PageHeroProps) {
  return (
    <section className="py-12 sm:py-16">
      <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-4xl space-y-5">
          {eyebrow}
          <h1 className="max-w-3xl text-4xl font-bold leading-tight tracking-normal sm:text-6xl">
            {title}
          </h1>
          <p className="max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">
            {description}
          </p>
        </div>
        {visual ? <div className="w-full shrink-0 lg:w-auto">{visual}</div> : null}
      </div>
      {action ? <div className="mt-7">{action}</div> : null}
      {children}
    </section>
  );
}
