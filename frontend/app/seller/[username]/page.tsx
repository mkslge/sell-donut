import Link from "next/link";
import { notFound } from "next/navigation";
import { RatingOutcome } from "@prisma/client";
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
import { prisma } from "@/lib/prisma";
import { minecraftUsernameSchema, trustLabel } from "@/lib/ratings";

export default async function SellerPage({ params }: SellerPageProps) {
  const { username } = await params;
  const parsedUsername = minecraftUsernameSchema.safeParse(username);

  if (!parsedUsername.success) {
    notFound();
  }

  const normalizedUsername = parsedUsername.data.toLowerCase();
  const seller = await prisma.seller.findUnique({
    where: { normalizedUsername },
    include: {
      ratings: {
        orderBy: { createdAt: "desc" },
      },
    },
  });

  const ratings = seller?.ratings ?? [];
  const counts = ratings.reduce(
    (acc, rating) => {
      acc.total += 1;
      if (rating.outcome === RatingOutcome.LEGIT) acc.legit += 1;
      if (rating.outcome === RatingOutcome.SCAM) acc.scam += 1;
      if (rating.outcome === RatingOutcome.MIXED) acc.mixed += 1;
      return acc;
    },
    { total: 0, legit: 0, scam: 0, mixed: 0 },
  );

  const displayName = seller?.minecraftUsername ?? parsedUsername.data;

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
            <CardDescription>Aggregate community reports for this username.</CardDescription>
            <CardAction>
              <Badge variant="outline">{trustLabel(counts)}</Badge>
            </CardAction>
          </CardHeader>
          <CardContent>
            <StatsGrid
              stats={[
                { label: "Total", value: counts.total },
                { label: "Legit", value: counts.legit },
                { label: "Scam", value: counts.scam },
                { label: "Mixed", value: counts.mixed },
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
