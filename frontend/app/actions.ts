"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";
import type { RatingFormState } from "@/lib/types";
import { minecraftUsernameSchema, ratingSchema } from "@/lib/ratings";
import { BackendError, fetchBackendJson, type RatingCreatePayload } from "@/lib/api";
import { normalizeUsername } from "@/lib/ratings";

function fieldValue(formData: FormData, name: string) {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

function optionalFieldValue(formData: FormData, name: string) {
  const value = formData.get(name);
  return typeof value === "string" && value.length ? value : undefined;
}

export async function createRating(
  _previousState: RatingFormState,
  formData: FormData,
): Promise<RatingFormState> {
  const raw = {
    minecraftUsername: fieldValue(formData, "minecraftUsername"),
    outcome: fieldValue(formData, "outcome"),
    tradeCategory: fieldValue(formData, "tradeCategory"),
    tradeDescription: fieldValue(formData, "tradeDescription"),
    evidenceUrl: optionalFieldValue(formData, "evidenceUrl"),
    reviewText: fieldValue(formData, "reviewText"),
  };

  const parsed = ratingSchema.safeParse(raw);

  if (!parsed.success) {
    return {
      message: "Please fix the highlighted fields.",
      errors: parsed.error.flatten().fieldErrors,
    };
  }

  const username = minecraftUsernameSchema.safeParse(parsed.data.minecraftUsername);
  if (!username.success) {
    return {
      message: "Please fix the highlighted fields.",
      errors: { minecraftUsername: ["Use a valid Minecraft username."] },
    };
  }

  const incomingHeaders = await headers();
  const backendHeaders = {
    "x-forwarded-for": incomingHeaders.get("x-forwarded-for") ?? "",
    "x-real-ip": incomingHeaders.get("x-real-ip") ?? "",
    "user-agent": incomingHeaders.get("user-agent") ?? "",
  };

  const payload: RatingCreatePayload = {
    outcome: parsed.data.outcome,
    tradeCategory: parsed.data.tradeCategory,
    tradeDescription: parsed.data.tradeDescription,
    reviewText: parsed.data.reviewText,
    evidenceUrl: parsed.data.evidenceUrl,
  };

  try {
    await fetchBackendJson(`/rating/${encodeURIComponent(username.data)}`, {
      method: "POST",
      json: payload,
      headers: backendHeaders,
    });
  } catch (error) {
    if (error instanceof BackendError) {
      return { message: error.message };
    }

    return { message: "Could not submit the rating right now." };
  }

  redirect(`/seller/${encodeURIComponent(normalizeUsername(username.data))}`);
}
