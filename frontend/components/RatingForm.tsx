"use client";

import { useActionState } from "react";
import { createRating } from "@/app/actions";
import type { RatingFormProps, RatingFormState } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { FieldLabel } from "@/components/forms/FieldLabel";

const initialState: RatingFormState = {};

export function RatingForm({ defaultUsername = "" }: RatingFormProps) {
  const [state, formAction, pending] = useActionState(createRating, initialState);

  return (
    <form className="grid gap-4" action={formAction}>
      {state.message ? (
        <p className="rounded-lg border border-destructive/20 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {state.message}
        </p>
      ) : null}

      <div className="grid gap-2">
        <FieldLabel htmlFor="minecraftUsername" required>
          Seller Minecraft username
        </FieldLabel>
        <Input
          id="minecraftUsername"
          name="minecraftUsername"
          defaultValue={defaultUsername}
          placeholder="Example: DonutTrader"
          required
          minLength={3}
          maxLength={16}
          pattern="[A-Za-z0-9_]{3,16}"
        />
        {state.errors?.minecraftUsername ? (
          <span className="text-sm text-muted-foreground">
            {state.errors.minecraftUsername[0]}
          </span>
        ) : null}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-2">
          <FieldLabel required>Outcome</FieldLabel>
          <Select name="outcome" defaultValue="LEGIT">
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choose outcome" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="LEGIT">Legit</SelectItem>
              <SelectItem value="SCAMMER">Scam</SelectItem>
              <SelectItem value="MIXED">Mixed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid gap-2">
          <FieldLabel required>Trade category</FieldLabel>
          <Select name="tradeCategory" defaultValue="SPAWNER">
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choose category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="SPAWNER">Spawner</SelectItem>
              <SelectItem value="BASE">Base</SelectItem>
              <SelectItem value="GEAR">Gear</SelectItem>
              <SelectItem value="MONEY">Money</SelectItem>
              <SelectItem value="OTHER">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid gap-2">
        <FieldLabel htmlFor="tradeDescription" required>
          What was traded?
        </FieldLabel>
        <Input
          id="tradeDescription"
          name="tradeDescription"
          placeholder="Skeleton spawner or base for 3m"
          required
          maxLength={120}
        />
        {state.errors?.tradeDescription ? (
          <span className="text-sm text-muted-foreground">
            {state.errors.tradeDescription[0]}
          </span>
        ) : null}
      </div>

      <div className="grid gap-2">
        <FieldLabel htmlFor="evidenceUrl" optional>
          Evidence URL
        </FieldLabel>
        <Input
          id="evidenceUrl"
          name="evidenceUrl"
          placeholder="Optional screenshot or clip link"
          type="url"
        />
        {state.errors?.evidenceUrl ? (
          <span className="text-sm text-muted-foreground">
            {state.errors.evidenceUrl[0]}
          </span>
        ) : null}
      </div>

      <div className="grid gap-2">
        <FieldLabel htmlFor="reviewText" required>
          Review
        </FieldLabel>
        <Textarea
          id="reviewText"
          className="min-h-28"
          name="reviewText"
          placeholder="Describe what happened during the trade."
          required
          maxLength={1000}
        />
        {state.errors?.reviewText ? (
          <span className="text-sm text-muted-foreground">
            {state.errors.reviewText[0]}
          </span>
        ) : null}
      </div>

      <Button type="submit" disabled={pending} className="w-full sm:w-fit">
        {pending ? "Submitting..." : "Submit rating"}
      </Button>
    </form>
  );
}
