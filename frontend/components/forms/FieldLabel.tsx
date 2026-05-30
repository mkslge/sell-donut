import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";

type FieldLabelProps = {
  htmlFor?: string;
  children: ReactNode;
  required?: boolean;
  optional?: boolean;
  className?: string;
};

export function FieldLabel({
  htmlFor,
  children,
  required = false,
  optional = false,
  className,
}: FieldLabelProps) {
  return (
    <Label htmlFor={htmlFor} className={cn("flex items-center gap-1", className)}>
      <span>{children}</span>
      {required ? (
        <span className="text-destructive" aria-hidden="true">
          *
        </span>
      ) : null}
      {optional ? (
        <span className="text-xs font-normal text-muted-foreground">(optional)</span>
      ) : null}
    </Label>
  );
}
