import type { RatingOutcome, TradeCategory } from "@prisma/client";
import Link from "next/link";
import { formatCategory, formatOutcome } from "@/lib/ratings";

type RatingCardProps = {
  rating: {
    outcome: RatingOutcome;
    tradeCategory: TradeCategory;
    tradeDescription: string;
    evidenceUrl: string | null;
    reviewText: string;
    createdAt: Date;
    seller?: {
      minecraftUsername: string;
      normalizedUsername: string;
    };
  };
};

export function RatingCard({ rating }: RatingCardProps) {
  const outcomeClass = rating.outcome.toLowerCase();

  return (
    <article className="card">
      <div className="rating-head">
        <div>
          {rating.seller ? (
            <Link href={`/seller/${rating.seller.normalizedUsername}`}>
              <strong>{rating.seller.minecraftUsername}</strong>
            </Link>
          ) : (
            <strong>{formatCategory(rating.tradeCategory)} trade</strong>
          )}
          <div className="muted">
            {formatCategory(rating.tradeCategory)} ·{" "}
            {rating.createdAt.toLocaleDateString()}
          </div>
        </div>
        <span className={`badge ${outcomeClass}`}>
          {formatOutcome(rating.outcome)}
        </span>
      </div>
      <p>
        <strong>{rating.tradeDescription}</strong>
      </p>
      <p className="muted">{rating.reviewText}</p>
      {rating.evidenceUrl ? (
        <a className="button" href={rating.evidenceUrl} target="_blank" rel="noreferrer">
          View evidence
        </a>
      ) : null}
    </article>
  );
}
