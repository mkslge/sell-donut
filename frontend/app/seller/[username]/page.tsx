import Link from "next/link";
import { notFound } from "next/navigation";
import { RatingCard } from "@/components/RatingCard";
import { RatingForm } from "@/components/RatingForm";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHero } from "@/components/layout/PageHero";
import { SectionHeader } from "@/components/layout/SectionHeader";
import { TwoColumnSection } from "@/components/layout/TwoColumnSection";
import { StatsGrid } from "@/components/StatsGrid";
import { SellerAvatar } from "@/components/profile/SellerAvatar";
import type { SellerPageProps } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { minecraftUsernameSchema, trustLabel } from "@/lib/ratings";
import { getSellerRatings, getSellerSummary, summarizeCounts } from "@/lib/api";

export default async function SellerPage({ params }: SellerPageProps) {
  const { username } = await params;
  const parsedUsername = minecraftUsernameSchema.safeParse(username);

  if (!parsedUsername.success) {
    notFound();
  }

  const normalizedUsername = parsedUsername.data.toLowerCase();
  const [sellerRatings, sellerSummary] = await Promise.all([
    getSellerRatings(normalizedUsername).catch(() => ({
      sellerUsername: parsedUsername.data,
      ratings: [],
    })),
    getSellerSummary(normalizedUsername).catch(() => ({
      sellerUsername: parsedUsername.data,
      totalRatings: 0,
      legitCount: 0,
      scammerCount: 0,
      mixedCount: 0,
      legitPercentage: 0,
      reputation: "NO_DATA",
    })),
  ]);

  const ratings = sellerRatings.ratings;
  const counts = summarizeCounts(ratings);
  const displayName = sellerSummary.sellerUsername ?? sellerRatings.sellerUsername;

  return (
    <PageContainer>
      <PageHero
        title={displayName}
        description="Community reputation summary for this DonutSMP seller. Anonymous reports can be wrong or abused, so use this with your own judgment."
        visual={
          <SellerAvatar
            username={displayName}
            alt={`${displayName} Minecraft skin`}
            size="lg"
          />
        }
        action={
          <Button asChild>
            <Link href={`/rate?username=${normalizedUsername}`}>Add rating</Link>
          </Button>
        }
      />

      <section className="grid gap-6 pb-12">
        <Card>
          <CardHeader>
            <CardTitle>Trust snapshot</CardTitle>
            <CardDescription>
              Aggregate community reports for this username.
            </CardDescription>
            <CardAction>
              <Badge variant="outline">{trustLabel(counts)}</Badge>
            </CardAction>
          </CardHeader>
          <CardContent>
            <StatsGrid
              stats={[
                { label: "Total", value: sellerSummary.totalRatings },
                { label: "Legit", value: sellerSummary.legitCount },
                { label: "Scam", value: sellerSummary.scammerCount },
                { label: "Mixed", value: sellerSummary.mixedCount },
              ]}
            />
          </CardContent>
        </Card>

        <TwoColumnSection>
          <section className="grid gap-4">
            <SectionHeader
              title="Ratings"
              description="Most recent reports are shown first."
            />
            <div className="grid gap-3">
              {ratings.length ? (
                ratings.map((rating) => (
                  <RatingCard key={rating.id} rating={rating} />
                ))
              ) : (
                <p className="text-sm leading-6 text-muted-foreground">
                  No one has rated this seller yet. A blank profile means no
                  community history, not guaranteed safety.
                </p>
              )}
            </div>
          </section>

          <Card>
            <CardHeader>
              <CardTitle>Rate {displayName}</CardTitle>
              <CardDescription>Add your report for this seller.</CardDescription>
            </CardHeader>
            <CardContent>
              <RatingForm defaultUsername={displayName} />
            </CardContent>
          </Card>
        </TwoColumnSection>
      </section>
    </PageContainer>
  );
}
