import Link from "next/link";
import { notFound } from "next/navigation";
import { RatingOutcome } from "@prisma/client";
import { RatingCard } from "@/components/RatingCard";
import { RatingForm } from "@/components/RatingForm";
import { prisma } from "@/lib/prisma";
import { minecraftUsernameSchema, trustLabel } from "@/lib/ratings";

type SellerPageProps = {
  params: Promise<{
    username: string;
  }>;
};

export default async function SellerPage({ params }: SellerPageProps) {
  const { username } = await params;
  const parsedUsername = minecraftUsernameSchema.safeParse(username);

  if (!parsedUsername.success) {
    notFound();
  }

  const normalizedUsername = parsedUsername.data.toLowerCase();
  const seller = await prisma.seller.findUnique({
    where: { normalizedUsername },
    include: {
      ratings: {
        orderBy: { createdAt: "desc" },
      },
    },
  });

  const ratings = seller?.ratings ?? [];
  const counts = ratings.reduce(
    (acc, rating) => {
      acc.total += 1;
      if (rating.outcome === RatingOutcome.LEGIT) acc.legit += 1;
      if (rating.outcome === RatingOutcome.SCAM) acc.scam += 1;
      if (rating.outcome === RatingOutcome.MIXED) acc.mixed += 1;
      return acc;
    },
    { total: 0, legit: 0, scam: 0, mixed: 0 },
  );

  const displayName = seller?.minecraftUsername ?? parsedUsername.data;

  return (
    <div className="container">
      <section className="hero">
        <h1>{displayName}</h1>
        <p>
          Community reputation summary for this DonutSMP seller. Anonymous
          reports can be wrong or abused, so use this with your own judgment.
        </p>
        <Link className="button primary" href={`/rate?username=${normalizedUsername}`}>
          Add rating
        </Link>
      </section>

      <section className="stack" style={{ paddingBottom: 48 }}>
        <div className="panel stack">
          <div className="rating-head">
            <h2 className="section-title" style={{ margin: 0 }}>
              Trust snapshot
            </h2>
            <span className="badge">{trustLabel(counts)}</span>
          </div>
          <div className="stats">
            <div className="stat">
              <strong>{counts.total}</strong>
              <span className="muted">Total</span>
            </div>
            <div className="stat">
              <strong>{counts.legit}</strong>
              <span className="muted">Legit</span>
            </div>
            <div className="stat">
              <strong>{counts.scam}</strong>
              <span className="muted">Scam</span>
            </div>
            <div className="stat">
              <strong>{counts.mixed}</strong>
              <span className="muted">Mixed</span>
            </div>
          </div>
        </div>

        <div className="grid">
          <div className="panel">
            <h2 className="section-title">Ratings</h2>
            <div className="rating-list">
              {ratings.length ? (
                ratings.map((rating) => (
                  <RatingCard key={rating.id} rating={rating} />
                ))
              ) : (
                <p className="muted">
                  No one has rated this seller yet. A blank profile means no
                  community history, not guaranteed safety.
                </p>
              )}
            </div>
          </div>

          <aside className="panel">
            <h2 className="section-title">Rate {displayName}</h2>
            <RatingForm defaultUsername={displayName} />
          </aside>
        </div>
      </section>
    </div>
  );
}
