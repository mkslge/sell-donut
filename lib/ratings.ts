import { headers } from "next/headers";
import { RatingOutcome, TradeCategory } from "@prisma/client";
import { z } from "zod";

export const minecraftUsernameSchema = z
  .string()
  .trim()
  .regex(/^[A-Za-z0-9_]{3,16}$/, "Use a valid Minecraft username.");

export const ratingSchema = z.object({
  minecraftUsername: minecraftUsernameSchema,
  outcome: z.nativeEnum(RatingOutcome),
  tradeCategory: z.nativeEnum(TradeCategory),
  tradeDescription: z
    .string()
    .trim()
    .min(3, "Describe the trade in at least 3 characters.")
    .max(120, "Keep the trade description under 120 characters."),
  evidenceUrl: z
    .string()
    .trim()
    .optional()
    .transform((value) => (value ? value : undefined))
    .pipe(z.string().url("Use a valid URL.").optional()),
  reviewText: z
    .string()
    .trim()
    .min(10, "Write at least 10 characters about what happened.")
    .max(1000, "Keep reviews under 1000 characters."),
});

export type RatingInput = z.infer<typeof ratingSchema>;

export function normalizeUsername(username: string) {
  return username.trim().toLowerCase();
}

export function formatOutcome(outcome: RatingOutcome) {
  if (outcome === "LEGIT") return "Legit";
  if (outcome === "SCAM") return "Scam";
  return "Mixed";
}

export function formatCategory(category: TradeCategory) {
  if (category === "SPAWNER") return "Spawner";
  if (category === "GEAR") return "Gear";
  if (category === "MONEY") return "Money";
  return "Other";
}

export function trustLabel(counts: {
  legit: number;
  scam: number;
  mixed: number;
  total: number;
}) {
  if (counts.total === 0) return "No reports yet";
  if (counts.scam >= 3 && counts.scam >= counts.legit) return "High scam risk";
  if (counts.legit >= 3 && counts.legit > counts.scam * 2) return "Mostly legit reports";
  if (counts.scam > counts.legit) return "Scam reports present";
  return "Mixed community reports";
}

export async function submitterFingerprint() {
  const headerList = await headers();
  const forwardedFor = headerList.get("x-forwarded-for") ?? "";
  const realIp = headerList.get("x-real-ip") ?? "";
  const userAgent = headerList.get("user-agent") ?? "";

  return `${forwardedFor.split(",")[0] || realIp || "unknown"}:${userAgent.slice(
    0,
    120,
  )}`;
}
