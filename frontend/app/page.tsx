import { redirect } from "next/navigation";
import Link from "next/link";
import { Search } from "lucide-react";
import { prisma } from "@/lib/prisma";
import { minecraftUsernameSchema } from "@/lib/ratings";
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
  const recentRatings = await prisma.rating.findMany({
    orderBy: { createdAt: "desc" },
    take: 8,
    include: {
      seller: {
        select: {
          minecraftUsername: true,
          normalizedUsername: true,
        },
      },
    },
  });

  return (
    <PageContainer>
      <PageHero
        title="Know who you are trading with before you /pay."
        description="SellDonut keeps a searchable record of community trade reports, so spawner, item, money, and service deals have a public reputation trail."
        eyebrow={
          <Badge variant="secondary" className="h-7 px-3 text-sm">
            Community seller reports for DonutSMP
          </Badge>
        }
      >
        <form
          className="mt-8 flex max-w-2xl flex-col gap-2 rounded-xl border bg-card p-2 shadow-sm sm:flex-row"
          action={searchSeller}
        >
          <Input
            className="h-11 border-transparent bg-transparent px-3 text-base focus-visible:ring-0"
            name="username"
            placeholder="Search username (e.g. Marlowww)"
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
            <CardTitle>Prototype rules</CardTitle>
            <CardDescription>Use ratings as signal, not proof.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <p className="rounded-lg border bg-accent px-3 py-2 text-sm leading-6 text-accent-foreground">
              Ratings are anonymous community reports, not verified proof. Treat
              them as a warning signal and ask for evidence before high-value
              trades.
            </p>
            <Button asChild className="w-fit">
              <Link href="/rate">Rate a seller</Link>
            </Button>
          </CardContent>
        </Card>
      </TwoColumnSection>
    </PageContainer>
  );
}
