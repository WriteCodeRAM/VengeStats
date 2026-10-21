const VARIANTS: Record<string, { label: string; style: string }> = {
  RELEASED: { label: "Released", style: "bg-venge-red/20 text-red-300 border-venge-red/40" },
  WAIVED: { label: "Waived", style: "bg-venge-red/20 text-red-300 border-venge-red/40" },
  TRADED: { label: "Traded", style: "bg-amber-500/15 text-amber-300 border-amber-500/40" },
  TRADE: { label: "Traded", style: "bg-amber-500/15 text-amber-300 border-amber-500/40" },
  "FREE AGENT": { label: "Free Agent", style: "bg-white/5 text-text-secondary border-borderDefault" },
  "F/A": { label: "Free Agent", style: "bg-white/5 text-text-secondary border-borderDefault" },
};

export function DepartureBadge({
  method,
  className = "",
}: {
  method?: string | null;
  className?: string;
}) {
  const variant = method ? VARIANTS[method.trim().toUpperCase()] : undefined;
  if (!variant) return null;
  return (
    <span
      className={`inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide whitespace-nowrap ${variant.style} ${className}`}
    >
      {variant.label}
    </span>
  );
}
