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
    rating.verdict === "SCAMMER"
      ? "destructive"
      : rating.verdict === "MIXED"
        ? "secondary"
        : "default";
  const cardTone =
    rating.verdict === "SCAMMER"
      ? "border-destructive/25 bg-destructive/5"
      : rating.verdict === "MIXED"
        ? "border-secondary bg-secondary/45"
        : "border-primary/20 bg-card";

  return (
    <Card className={cardTone}>
      <CardHeader>
        <div className="flex items-start gap-3">
          <SellerAvatar
            username={rating.sellerUsername}
            alt={`${rating.sellerUsername} avatar`}
            size="sm"
            className="mt-0.5"
          />
          <div className="min-w-0 flex-1">
            <CardTitle>
              <Link
                className="hover:text-primary"
                href={`/seller/${rating.sellerUsername.toLowerCase()}`}
              >
                {rating.sellerUsername}
              </Link>
            </CardTitle>
            <CardDescription>
              {formatCategory(rating.tradeCategory)} ·{" "}
              {rating.createdAt.toLocaleDateString()}
            </CardDescription>
          </div>
          <Badge className="shrink-0" variant={badgeVariant}>
            {formatOutcome(rating.verdict)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="grid gap-3">
        <p className="font-semibold">{rating.tradeDescription}</p>
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
