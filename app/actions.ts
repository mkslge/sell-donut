"use server";

import { RatingOutcome, TradeCategory } from "@prisma/client";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import {
  normalizeUsername,
  ratingSchema,
  submitterFingerprint,
} from "@/lib/ratings";

export type RatingFormState = {
  message?: string;
  errors?: Record<string, string[]>;
};

const FIFTEEN_MINUTES = 15 * 60 * 1000;

export async function createRating(
  _previousState: RatingFormState,
  formData: FormData,
): Promise<RatingFormState> {
  const raw = {
    minecraftUsername: formData.get("minecraftUsername"),
    outcome: formData.get("outcome") || RatingOutcome.MIXED,
    tradeCategory: formData.get("tradeCategory") || TradeCategory.OTHER,
    tradeDescription: formData.get("tradeDescription"),
    evidenceUrl: formData.get("evidenceUrl"),
    reviewText: formData.get("reviewText"),
  };

  const parsed = ratingSchema.safeParse(raw);

  if (!parsed.success) {
    return {
      message: "Please fix the highlighted fields.",
      errors: parsed.error.flatten().fieldErrors,
    };
  }

  const fingerprint = await submitterFingerprint();
  const recentSubmission = await prisma.rating.findFirst({
    where: {
      submitterFingerprint: fingerprint,
      createdAt: {
        gte: new Date(Date.now() - FIFTEEN_MINUTES),
      },
    },
    select: { id: true },
  });

  if (recentSubmission) {
    return {
      message: "You can submit one rating every 15 minutes in this prototype.",
    };
  }

  const { minecraftUsername, ...rating } = parsed.data;
  const normalizedUsername = normalizeUsername(minecraftUsername);

  await prisma.seller.upsert({
    where: { normalizedUsername },
    update: {
      minecraftUsername,
      ratings: {
        create: {
          ...rating,
          submitterFingerprint: fingerprint,
        },
      },
    },
    create: {
      minecraftUsername,
      normalizedUsername,
      ratings: {
        create: {
          ...rating,
          submitterFingerprint: fingerprint,
        },
      },
    },
  });

  redirect(`/seller/${encodeURIComponent(normalizedUsername)}`);
}
