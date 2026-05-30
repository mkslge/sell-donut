import { ExternalLink } from "lucide-react";
import Link from "next/link";
import { formatCategory, formatOutcome } from "@/lib/ratings";
import type { RatingCardProps } from "@/lib/types";
import { SellerAvatar } from "@/components/profile/SellerAvatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function RatingCard({ rating }: RatingCardProps) {
  const badgeVariant =
    rating.outcome === "SCAM"
      ? "destructive"
      : rating.outcome === "MIXED"
        ? "secondary"
        : "default";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          {rating.seller ? (
            <SellerAvatar
              username={rating.seller.minecraftUsername}
              alt={`${rating.seller.minecraftUsername} avatar`}
              size="sm"
              className="mt-0.5"
            />
          ) : null}
          <div className="min-w-0 flex-1">
            <CardTitle>
              {rating.seller ? (
                <Link href={`/seller/${rating.seller.normalizedUsername}`}>
                  {rating.seller.minecraftUsername}
                </Link>
              ) : (
                `${formatCategory(rating.tradeCategory)} trade`
              )}
            </CardTitle>
            <CardDescription>
              {formatCategory(rating.tradeCategory)} ·{" "}
              {rating.createdAt.toLocaleDateString()}
            </CardDescription>
          </div>
          <Badge variant={badgeVariant}>
            {formatOutcome(rating.outcome)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="grid gap-3">
        <p className="font-medium">{rating.tradeDescription}</p>
        <p className="text-sm leading-6 text-muted-foreground">
          {rating.reviewText}
        </p>
        {rating.evidenceUrl ? (
          <Button asChild variant="outline" size="sm" className="w-fit">
            <a href={rating.evidenceUrl} target="_blank" rel="noreferrer">
              View evidence
              <ExternalLink data-icon="inline-end" />
            </a>
          </Button>
        ) : null}
      </CardContent>
    </Card>
  );
}
