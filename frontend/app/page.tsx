import { redirect } from "next/navigation";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, Search, ShieldCheck } from "lucide-react";
import { minecraftUsernameSchema } from "@/lib/ratings";
import { getRatingStats, getRecentRatings } from "@/lib/api";
import { RatingCard } from "@/components/RatingCard";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHero } from "@/components/layout/PageHero";
import { SectionHeader } from "@/components/layout/SectionHeader";
import { TwoColumnSection } from "@/components/layout/TwoColumnSection";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

async function searchSeller(formData: FormData) {
  "use server";

  const username = minecraftUsernameSchema.safeParse(formData.get("username"));

  if (!username.success) {
    redirect("/");
  }

  redirect(`/seller/${encodeURIComponent(username.data.toLowerCase())}`);
}

export default async function Home() {
  const [recentRatings, ratingStats] = await Promise.all([
    getRecentRatings().catch(() => []),
    getRatingStats().catch(() => ({ totalRatings: 0 })),
  ]);
  const totalRatingsLabel = ratingStats.totalRatings.toLocaleString();
  const ratingNoun = ratingStats.totalRatings === 1 ? "rating" : "ratings";

  return (
    <PageContainer>
      <PageHero
        title="Check a DonutSMP trader before you /pay."
        description={`Search ${totalRatingsLabel} community ${ratingNoun} for spawner, base, item, money, and service trades before you risk your balance.`}
        eyebrow={
          <Badge variant="secondary" className="h-7 px-3 text-sm">
            DonutSMP community reputation
          </Badge>
        }
        visual={
          <div className="grid w-full max-w-sm gap-3 rounded-xl border bg-card p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-muted-foreground">
                  Live report count
                </p>
                <strong className="text-3xl font-bold">
                  {totalRatingsLabel}
                </strong>
              </div>
              <div className="grid size-12 place-items-center rounded-lg bg-accent text-accent-foreground">
                <ShieldCheck className="size-6" aria-hidden="true" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="rounded-lg border bg-background px-3 py-2">
                <CheckCircle2
                  className="mb-1 size-4 text-primary"
                  aria-hidden="true"
                />
                Legit reports
              </div>
              <div className="rounded-lg border bg-background px-3 py-2">
                <AlertTriangle
                  className="mb-1 size-4 text-destructive"
                  aria-hidden="true"
                />
                Scam warnings
              </div>
            </div>
          </div>
        }
      >
        <form
          className="mt-8 flex max-w-2xl flex-col gap-2 rounded-xl border bg-card p-2 shadow-sm sm:flex-row"
          action={searchSeller}
        >
          <Input
            className="h-11 border-transparent bg-transparent px-3 text-base focus-visible:ring-0"
            name="username"
            placeholder="Search Minecraft username"
            required
            minLength={1}
            maxLength={16}
            pattern="[A-Za-z0-9_]{3,16}"
          />
          <Button type="submit" className="h-11 sm:w-32">
            <Search data-icon="inline-start" />
            Search
          </Button>
        </form>
        <div className="mt-3 flex flex-wrap gap-2 text-sm text-muted-foreground">
          <span className="rounded-md border bg-background px-2 py-1">
            Skeleton spawners
          </span>
          <span className="rounded-md border bg-background px-2 py-1">
            Kelp farms
          </span>
          <span className="rounded-md border bg-background px-2 py-1">
            Bases
          </span>
          <span className="rounded-md border bg-background px-2 py-1">
            Gambling rooms
          </span>
        </div>
      </PageHero>

      <TwoColumnSection>
        <section className="grid gap-4">
          <SectionHeader
            title="Recent ratings"
            description="Newest community reports across sellers."
          />
          <div className="grid gap-3">
            {recentRatings.length ? (
              recentRatings.map((rating) => (
              <RatingCard key={rating.id} rating={rating} />
              ))
            ) : (
              <p className="text-sm text-muted-foreground">
                No ratings yet. Submit the first report after a trade.
              </p>
            )}
          </div>
        </section>

        <Card>
          <CardHeader>
            <CardTitle>Trade smarter</CardTitle>
            <CardDescription>Ratings are signal, not proof.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div className="grid gap-3 text-sm leading-6">
              <p className="rounded-lg border bg-accent px-3 py-2 text-accent-foreground">
                Check recent reports before going first, especially on expensive
                spawners, bases, and casino payouts.
              </p>
              <p className="rounded-lg border bg-background px-3 py-2 text-muted-foreground">
                If a deal looks risky, ask for screenshots, use smaller
                batches, or walk away.
              </p>
            </div>
            <Button asChild className="w-fit">
              <Link href="/rate">Rate a seller</Link>
            </Button>
          </CardContent>
        </Card>
      </TwoColumnSection>
    </PageContainer>
  );
}
