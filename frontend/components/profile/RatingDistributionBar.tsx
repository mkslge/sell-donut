import type { TrustCounts } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type Segment = {
  key: "legit" | "scam" | "mixed";
  label: string;
  count: number;
  colorClass: string;
};

type RatingDistributionBarProps = {
  counts: TrustCounts;
};

export function RatingDistributionBar({ counts }: RatingDistributionBarProps) {
  const total = counts.total;
  const segments: Segment[] = [
    {
      key: "legit",
      label: "Legit",
      count: counts.legit,
      colorClass: "bg-emerald-200",
    },
    {
      key: "scam",
      label: "Scam",
      count: counts.scam,
      colorClass: "bg-rose-200",
    },
    {
      key: "mixed",
      label: "Mixed",
      count: counts.mixed,
      colorClass: "bg-amber-200",
    },
  ];

  return (
    <Card className="border-border/60 bg-card/80 shadow-sm backdrop-blur-sm">
      <CardHeader>
        <CardTitle>Rating distribution</CardTitle>
        <CardDescription>
          Every rating in this profile, grouped by outcome.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="grid gap-2">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>All ratings</span>
            <span>{total} total</span>
          </div>
          <div className="flex h-4 overflow-hidden rounded-full bg-muted ring-1 ring-foreground/10">
            {total ? (
              segments.map((segment) => {
                const width = `${(segment.count / total) * 100}%`;
                return (
                  <div
                    key={segment.key}
                    aria-label={`${segment.label}: ${segment.count} ratings`}
                    className={cn(
                      "h-full transition-[width] duration-300",
                      segment.colorClass,
                    )}
                    style={{ width }}
                  />
                );
              })
            ) : (
              <div className="h-full w-full bg-muted/60" />
            )}
          </div>
          <div className="grid gap-2 pt-1 sm:grid-cols-3">
            {segments.map((segment) => {
              const percent = total ? Math.round((segment.count / total) * 100) : 0;

              return (
                <div
                  key={segment.key}
                  className="rounded-xl border bg-background/80 p-3 shadow-sm"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={cn("h-2.5 w-2.5 rounded-full", segment.colorClass)}
                    />
                    <span className="text-sm font-medium">{segment.label}</span>
                  </div>
                  <div className="mt-2 flex items-end justify-between gap-3">
                    <strong className="text-2xl font-semibold">{segment.count}</strong>
                    <span className="text-sm text-muted-foreground">{percent}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        {!total ? (
          <p className="text-sm text-muted-foreground">
            No ratings yet, so the distribution is empty.
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}
