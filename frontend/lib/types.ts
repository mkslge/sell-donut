import type { RatingOutcome, TradeCategory } from "@prisma/client";
import type { z } from "zod";
import type { ratingSchema } from "@/lib/ratings";

export type RatingInput = z.infer<typeof ratingSchema>;

export type RatingFormState = {
  message?: string;
  errors?: Record<string, string[]>;
};

export type RatingFormProps = {
  defaultUsername?: string;
};

export type RatingCardRating = {
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

export type RatingCardProps = {
  rating: RatingCardRating;
};

export type TrustCounts = {
  legit: number;
  scam: number;
  mixed: number;
  total: number;
};

export type RatePageProps = {
  searchParams: Promise<{
    username?: string;
  }>;
};

export type SellerPageProps = {
  params: Promise<{
    username: string;
  }>;
};
