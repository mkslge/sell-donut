type StatItem = {
  label: string;
  value: number;
};

type StatsGridProps = {
  stats: StatItem[];
};

export function StatsGrid({ stats }: StatsGridProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-4">
      {stats.map((stat) => (
        <div key={stat.label} className="rounded-lg border bg-background p-4">
          <strong className="block text-2xl font-semibold">{stat.value}</strong>
          <span className="text-sm text-muted-foreground">{stat.label}</span>
        </div>
      ))}
    </div>
  );
}
