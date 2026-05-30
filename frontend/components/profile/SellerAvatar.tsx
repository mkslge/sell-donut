/* eslint-disable @next/next/no-img-element */
import { getAvatarUrl } from "@/lib/backend";
import { cn } from "@/lib/utils";

type SellerAvatarProps = {
  username: string;
  alt?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
};

const sizeClasses = {
  sm: "h-10 w-10",
  md: "h-20 w-20",
  lg: "h-28 w-28",
};

export function SellerAvatar({
  username,
  alt,
  size = "md",
  className,
}: SellerAvatarProps) {
  return (
    <img
      src={getAvatarUrl(username)}
      alt={alt ?? `${username} avatar`}
      width={112}
      height={112}
      loading="lazy"
      decoding="async"
      className={cn(
        "shrink-0 rounded-xl border bg-card object-cover",
        sizeClasses[size],
        className,
      )}
    />
  );
}
