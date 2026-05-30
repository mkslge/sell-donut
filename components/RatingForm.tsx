"use client";

import { useActionState } from "react";
import { createRating, type RatingFormState } from "@/app/actions";

type RatingFormProps = {
  defaultUsername?: string;
};

const initialState: RatingFormState = {};

export function RatingForm({ defaultUsername = "" }: RatingFormProps) {
  const [state, formAction, pending] = useActionState(createRating, initialState);

  return (
    <form className="form" action={formAction}>
      {state.message ? <p className="error">{state.message}</p> : null}

      <label className="label">
        Seller Minecraft username
        <input
          className="field"
          name="minecraftUsername"
          defaultValue={defaultUsername}
          placeholder="Example: DonutTrader"
          required
          minLength={3}
          maxLength={16}
          pattern="[A-Za-z0-9_]{3,16}"
        />
        {state.errors?.minecraftUsername ? (
          <span className="muted">{state.errors.minecraftUsername[0]}</span>
        ) : null}
      </label>

      <div className="form-row">
        <label className="label">
          Outcome
          <select className="select" name="outcome" defaultValue="LEGIT">
            <option value="LEGIT">Legit</option>
            <option value="SCAM">Scam</option>
            <option value="MIXED">Mixed</option>
          </select>
        </label>

        <label className="label">
          Trade category
          <select className="select" name="tradeCategory" defaultValue="SPAWNER">
            <option value="SPAWNER">Spawner</option>
            <option value="GEAR">Gear</option>
            <option value="MONEY">Money</option>
            <option value="OTHER">Other</option>
          </select>
        </label>
      </div>

      <label className="label">
        What was traded?
        <input
          className="field"
          name="tradeDescription"
          placeholder="Skeleton spawner for 3m"
          required
          maxLength={120}
        />
        {state.errors?.tradeDescription ? (
          <span className="muted">{state.errors.tradeDescription[0]}</span>
        ) : null}
      </label>

      <label className="label">
        Evidence URL
        <input
          className="field"
          name="evidenceUrl"
          placeholder="Optional screenshot or clip link"
          type="url"
        />
        {state.errors?.evidenceUrl ? (
          <span className="muted">{state.errors.evidenceUrl[0]}</span>
        ) : null}
      </label>

      <label className="label">
        Review
        <textarea
          className="textarea"
          name="reviewText"
          placeholder="Describe what happened during the trade."
          required
          maxLength={1000}
        />
        {state.errors?.reviewText ? (
          <span className="muted">{state.errors.reviewText[0]}</span>
        ) : null}
      </label>

      <button className="button primary" type="submit" disabled={pending}>
        {pending ? "Submitting..." : "Submit rating"}
      </button>
    </form>
  );
}
