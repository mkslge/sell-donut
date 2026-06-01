import { RatingForm } from "@/components/RatingForm";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHero } from "@/components/layout/PageHero";
import { TwoColumnSection } from "@/components/layout/TwoColumnSection";
import type { RatePageProps } from "@/lib/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { minecraftUsernameSchema } from "@/lib/ratings";

export default async function RatePage({ searchParams }: RatePageProps) {
  const { username } = await searchParams;
  const parsedUsername = minecraftUsernameSchema.safeParse(username ?? "");
  const defaultUsername = parsedUsername.success ? parsedUsername.data : "";

  return (
    <PageContainer>
      <PageHero
        title="Rate a seller."
        description="Submit what happened in a DonutSMP trade. Keep it specific: what was traded, whether the seller followed through, and any evidence you have."
      />

      <TwoColumnSection>
        <Card>
          <CardHeader>
            <CardTitle>New rating</CardTitle>
            <CardDescription>Describe one trade with this seller.</CardDescription>
          </CardHeader>
          <CardContent>
            <RatingForm defaultUsername={defaultUsername} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Why these fields?</CardTitle>
            <CardDescription>Specific reports are easier to evaluate.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <p className="text-sm leading-6 text-muted-foreground">
              A useful report needs both the outcome and context. For example,
              a vague scam claim is weaker than a specific report that the seller
              took payment for a blaze spawner or base and logged out.
            </p>
            <p className="rounded-lg border bg-accent px-3 py-2 text-sm leading-6 text-accent-foreground">
              This prototype has no login, so one browser can only submit once
              every 15 minutes.
            </p>
          </CardContent>
        </Card>
      </TwoColumnSection>
    </PageContainer>
  );
}
