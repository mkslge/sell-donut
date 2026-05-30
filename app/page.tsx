import Link from "next/link";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { minecraftUsernameSchema } from "@/lib/ratings";
import { RatingCard } from "@/components/RatingCard";

async function searchSeller(formData: FormData) {
  "use server";

  const username = minecraftUsernameSchema.safeParse(formData.get("username"));

  if (!username.success) {
    redirect("/");
  }

  redirect(`/seller/${encodeURIComponent(username.data.toLowerCase())}`);
}

export default async function Home() {
  const recentRatings = await prisma.rating.findMany({
    orderBy: { createdAt: "desc" },
    take: 8,
    include: {
      seller: {
        select: {
          minecraftUsername: true,
          normalizedUsername: true,
        },
      },
    },
  });

  return (
    <div className="container">
      <section className="hero">
        <h1>Check a DonutSMP seller before you trade.</h1>
        <p>
          SellDonut is a prototype community reputation board for Minecraft
          trades. Scamming may be allowed in-game, so this keeps a public memory
          of who players say traded cleanly and who they say scammed.
        </p>
        <form className="search" action={searchSeller}>
          <input
            className="field"
            name="username"
            placeholder="Minecraft username"
            required
            minLength={3}
            maxLength={16}
            pattern="[A-Za-z0-9_]{3,16}"
          />
          <button className="button primary" type="submit">
            Search
          </button>
        </form>
      </section>

      <section className="grid">
        <div className="panel">
          <h2 className="section-title">Recent ratings</h2>
          <div className="rating-list">
            {recentRatings.length ? (
              recentRatings.map((rating) => (
                <Link
                  key={rating.id}
                  href={`/seller/${rating.seller.normalizedUsername}`}
                >
                  <RatingCard rating={rating} />
                </Link>
              ))
            ) : (
              <p className="muted">
                No ratings yet. Submit the first report after a trade.
              </p>
            )}
          </div>
        </div>

        <aside className="panel stack">
          <h2 className="section-title">Prototype rules</h2>
          <p className="help">
            Ratings are anonymous community reports, not verified proof. Treat
            them as a warning signal and ask for evidence before high-value
            trades.
          </p>
          <Link className="button primary" href="/rate">
            Rate a seller
          </Link>
        </aside>
      </section>
    </div>
  );
}
