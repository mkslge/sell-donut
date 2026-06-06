import Link from "next/link";
import { AlertTriangle, CheckCircle2, Trophy } from "lucide-react";
import { getLeaderboard } from "@/lib/api";
import type { BackendLeaderboardEntry } from "@/lib/types";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHero } from "@/components/layout/PageHero";
import { SellerAvatar } from "@/components/profile/SellerAvatar";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type LeaderboardBoardProps = {
  title: string;
  description: string;
  entries: BackendLeaderboardEntry[];
  countKey: "scamCount" | "legitCount";
  emptyText: string;
};

function countLabel(count: number, noun: string) {
  return `${count.toLocaleString()} ${noun}${count === 1 ? "" : "s"}`;
}

function LeaderboardBoard({
  title,
  description,
  entries,
  countKey,
  emptyText,
}: LeaderboardBoardProps) {
  const targetNoun = countKey === "scamCount" ? "scam report" : "legit report";

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3">
        {entries.length ? (
          entries.map((entry, index) => (
            <Link
              key={`${countKey}-${entry.minecraftUuid}`}
              href={`/seller/${entry.normalizedUsername}`}
              className="grid grid-cols-[auto_auto_1fr] items-center gap-3 rounded-lg border bg-background p-3 transition-colors hover:bg-muted/60"
            >
              <span className="grid size-8 place-items-center rounded-md bg-muted text-sm font-semibold text-muted-foreground">
                {index + 1}
              </span>
              <SellerAvatar
                username={entry.sellerUsername}
                size="sm"
                alt={`${entry.sellerUsername} avatar`}
              />
              <span className="min-w-0">
                <span className="block truncate font-semibold">
                  {entry.sellerUsername}
                </span>
                <span className="mt-1 flex flex-wrap gap-2 text-xs text-muted-foreground">
                  <span>{countLabel(entry[countKey], targetNoun)}</span>
                  {countKey === "legitCount" ? (
                    <span>{countLabel(entry.scamCount, "scam report")}</span>
                  ) : (
                    <span>{countLabel(entry.legitCount, "legit report")}</span>
                  )}
                  {entry.mixedCount ? (
                    <span>{countLabel(entry.mixedCount, "mixed report")}</span>
                  ) : null}
                </span>
              </span>
            </Link>
          ))
        ) : (
          <p className="rounded-lg border bg-background p-3 text-sm text-muted-foreground">
            {emptyText}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

export default async function LeaderboardPage() {
  const leaderboard = await getLeaderboard().catch(() => ({
    scam: [],
    legit: [],
  }));

  return (
    <PageContainer>
      <PageHero
        title="DonutTrades leaderboard"
        description="See which DonutSMP sellers have the most scam reports and the most legit reports from the community."
        eyebrow={
          <Badge variant="secondary" className="h-7 px-3 text-sm">
            Top 10 community reports
          </Badge>
        }
        visual={
          <div className="grid w-full max-w-sm gap-3 rounded-xl border bg-card p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-muted-foreground">
                  Ranking signal
                </p>
                <strong className="text-3xl font-bold">Top 10</strong>
              </div>
              <div className="grid size-12 place-items-center rounded-lg bg-accent text-accent-foreground">
                <Trophy className="size-6" aria-hidden="true" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="rounded-lg border bg-background px-3 py-2">
                <AlertTriangle
                  className="mb-1 size-4 text-destructive"
                  aria-hidden="true"
                />
                Scam reports
              </div>
              <div className="rounded-lg border bg-background px-3 py-2">
                <CheckCircle2
                  className="mb-1 size-4 text-primary"
                  aria-hidden="true"
                />
                Legit reports
              </div>
            </div>
          </div>
        }
      />

      <section className="grid gap-4 pb-10 lg:grid-cols-2">
        <LeaderboardBoard
          title="Most scam reports"
          description="Players with the highest number of scam reports."
          entries={leaderboard.scam}
          countKey="scamCount"
          emptyText="No scam reports yet."
        />
        <LeaderboardBoard
          title="Most legit reports"
          description="Players with the highest number of legit reports."
          entries={leaderboard.legit}
          countKey="legitCount"
          emptyText="No legit reports yet."
        />
      </section>
    </PageContainer>
  );
}
