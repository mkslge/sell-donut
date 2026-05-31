import type { z } from "zod";
import type { ratingSchema } from "@/lib/ratings";
import type { RatingOutcome, TradeCategory } from "@/lib/ratings";

export type RatingInput = z.infer<typeof ratingSchema>;

export type RatingFormState = {
  message?: string;
  errors?: Record<string, string[]>;
};

export type RatingFormProps = {
  defaultUsername?: string;
};

export type RatingCardRating = {
  id: string;
  sellerUsername: string;
  verdict: RatingOutcome;
  tradeCategory: TradeCategory;
  tradeDescription: string;
  reviewText: string;
  quantity: number | null;
  price: number | null;
  currency: string | null;
  evidenceUrl: string | null;
  reporterUsername: string | null;
  createdAt: Date;
};

export type BackendRatingResponse = {
  id: string;
  sellerUsername: string;
  outcome: RatingOutcome;
  tradeCategory: TradeCategory;
  tradeDescription: string;
  quantity: number | null;
  price: number | null;
  currency: string | null;
  reviewText: string;
  evidenceUrl: string | null;
  reporterUsername: string | null;
  createdAt: string;
};

export type BackendSellerRatingsResponse = {
  sellerUsername: string;
  ratings: BackendRatingResponse[];
};

export type BackendSellerSummaryResponse = {
  sellerUsername: string;
  totalRatings: number;
  legitCount: number;
  scammerCount: number;
  mixedCount: number;
  legitPercentage: number;
  reputation: string;
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
