import type {
  BackendRatingResponse,
  BackendSellerRatingsResponse,
  BackendSellerSummaryResponse,
  RatingCardRating,
  TrustCounts,
} from "@/lib/types";
import type { RatingOutcome, TradeCategory } from "@/lib/ratings";
import { getBackendBaseUrl } from "@/lib/backend";

type RequestInitWithJson = RequestInit & {
  json?: unknown;
};

export class BackendError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function buildUrl(path: string) {
  return new URL(path, `${getBackendBaseUrl()}/`).toString();
}

async function readErrorMessage(response: Response) {
  try {
    const payload = (await response.json()) as { error?: string };
    return payload.error ?? response.statusText ?? "Backend request failed.";
  } catch {
    return response.statusText ?? "Backend request failed.";
  }
}

export async function fetchBackendJson<T>(
  path: string,
  init: RequestInitWithJson = {},
): Promise<T> {
  const { json, headers, ...rest } = init;
  const response = await fetch(buildUrl(path), {
    ...rest,
    headers: {
      ...(json ? { "Content-Type": "application/json" } : {}),
      ...(headers ?? {}),
    },
    body: json ? JSON.stringify(json) : rest.body,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new BackendError(response.status, await readErrorMessage(response));
  }

  return (await response.json()) as T;
}

export function toRatingCardRating(
  rating: BackendRatingResponse,
): RatingCardRating {
  return {
    id: rating.id,
    sellerUsername: rating.sellerUsername,
    verdict: rating.outcome,
    tradeCategory: rating.tradeCategory,
    tradeDescription: rating.tradeDescription,
    reviewText: rating.reviewText,
    quantity: rating.quantity,
    price: rating.price,
    currency: rating.currency,
    evidenceUrl: rating.evidenceUrl,
    reporterUsername: rating.reporterUsername,
    createdAt: new Date(rating.createdAt),
  };
}

export function summarizeCounts(ratings: RatingCardRating[]): TrustCounts {
  return ratings.reduce(
    (acc, rating) => {
      acc.total += 1;
      if (rating.verdict === "LEGIT") acc.legit += 1;
      if (rating.verdict === "SCAMMER") acc.scam += 1;
      if (rating.verdict === "MIXED") acc.mixed += 1;
      return acc;
    },
    { total: 0, legit: 0, scam: 0, mixed: 0 },
  );
}

export async function getRecentRatings(limit = 8): Promise<RatingCardRating[]> {
  const response = await fetchBackendJson<BackendRatingResponse[]>(
    `/rating/recent?limit=${limit}`,
  );
  return response.map(toRatingCardRating);
}

export async function getSellerRatings(
  username: string,
): Promise<{ sellerUsername: string; ratings: RatingCardRating[] }> {
  const response = await fetchBackendJson<BackendSellerRatingsResponse>(
    `/rating/${encodeURIComponent(username)}`,
  );

  return {
    sellerUsername: response.sellerUsername,
    ratings: response.ratings.map(toRatingCardRating),
  };
}

export async function getSellerSummary(username: string): Promise<{
  sellerUsername: string;
  totalRatings: number;
  legitCount: number;
  scammerCount: number;
  mixedCount: number;
  legitPercentage: number;
  reputation: BackendSellerSummaryResponse["reputation"];
}> {
  return fetchBackendJson<BackendSellerSummaryResponse>(
    `/rating/${encodeURIComponent(username)}/summary`,
  );
}

export type RatingCreatePayload = {
  outcome: RatingOutcome;
  tradeCategory: TradeCategory;
  tradeDescription: string;
  reviewText: string;
  evidenceUrl?: string;
};
