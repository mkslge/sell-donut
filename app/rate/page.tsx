import { RatingForm } from "@/components/RatingForm";
import { minecraftUsernameSchema } from "@/lib/ratings";

type RatePageProps = {
  searchParams: Promise<{
    username?: string;
  }>;
};

export default async function RatePage({ searchParams }: RatePageProps) {
  const { username } = await searchParams;
  const parsedUsername = minecraftUsernameSchema.safeParse(username ?? "");
  const defaultUsername = parsedUsername.success ? parsedUsername.data : "";

  return (
    <div className="container">
      <section className="hero">
        <h1>Rate a seller.</h1>
        <p>
          Submit what happened in a DonutSMP trade. Keep it specific: what was
          traded, whether the seller followed through, and any evidence you
          have.
        </p>
      </section>

      <section className="grid">
        <div className="panel">
          <h2 className="section-title">New rating</h2>
          <RatingForm defaultUsername={defaultUsername} />
        </div>
        <aside className="panel stack">
          <h2 className="section-title">Why these fields?</h2>
          <p className="muted">
            A useful report needs both the outcome and context. For example,
            a vague scam claim is weaker than a specific report that the seller
            took payment for a blaze spawner and logged out.
          </p>
          <p className="help">
            This prototype has no login, so one browser can only submit once
            every 15 minutes.
          </p>
        </aside>
      </section>
    </div>
  );
}
