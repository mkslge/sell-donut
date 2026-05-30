import type { PropsWithChildren } from "react";

export function PageContainer({ children }: PropsWithChildren) {
  return <div className="mx-auto w-[min(1120px,calc(100%-2rem))]">{children}</div>;
}
