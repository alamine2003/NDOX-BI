type IconProps = { size?: number; className?: string };

const base = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

export function DropletIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <path d="M12 2.5C12 2.5 5.5 11 5.5 15.5a6.5 6.5 0 0 0 13 0C18.5 11 12 2.5 12 2.5z" />
    </svg>
  );
}

export function MapPinIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <path d="M12 21s-7-7.2-7-12a7 7 0 1 1 14 0c0 4.8-7 12-7 12z" />
      <circle cx="12" cy="9" r="2.5" />
    </svg>
  );
}

export function PhoneIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <rect x="6" y="2.5" width="12" height="19" rx="2.5" />
      <line x1="10.5" y1="18.3" x2="13.5" y2="18.3" />
    </svg>
  );
}

export function ChartIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <line x1="5" y1="21" x2="5" y2="12" />
      <line x1="12" y1="21" x2="12" y2="7" />
      <line x1="19" y1="21" x2="19" y2="15" />
      <line x1="3" y1="21" x2="21" y2="21" />
    </svg>
  );
}

export function PulseIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <polyline points="2.5,13 8,13 10,7 14,19 16,13 21.5,13" />
    </svg>
  );
}

export function ShieldCheckIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <path d="M12 2.5l7.5 3v6c0 5-3.2 8.4-7.5 10-4.3-1.6-7.5-5-7.5-10v-6l7.5-3z" />
      <polyline points="8.5,12.2 11,14.7 15.7,9.7" />
    </svg>
  );
}

export function ShieldXIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <path d="M12 2.5l7.5 3v6c0 5-3.2 8.4-7.5 10-4.3-1.6-7.5-5-7.5-10v-6l7.5-3z" />
      <line x1="9.3" y1="9.3" x2="14.7" y2="14.7" />
      <line x1="14.7" y1="9.3" x2="9.3" y2="14.7" />
    </svg>
  );
}

export function WifiOffIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <line x1="2.5" y1="2.5" x2="21.5" y2="21.5" />
      <path d="M8.5 16.3a5 5 0 0 1 7 0" />
      <path d="M5.2 12.8a10 10 0 0 1 3.9-2.5" />
      <path d="M14.9 10.3a10 10 0 0 1 4 2.5" />
      <path d="M2 8.8a15 15 0 0 1 5.6-3.4" />
      <path d="M18.4 6.3A15 15 0 0 1 22 8.8" />
      <line x1="12" y1="19.5" x2="12.01" y2="19.5" />
    </svg>
  );
}

export function ClockIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <circle cx="12" cy="12" r="9.5" />
      <polyline points="12,6.5 12,12 16,14.5" />
    </svg>
  );
}

export function GaugeIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <path d="M4 15a8 8 0 1 1 16 0" />
      <line x1="12" y1="15" x2="15.5" y2="10" />
      <line x1="12" y1="15" x2="12" y2="15" />
    </svg>
  );
}

export function UsersIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <circle cx="9" cy="8" r="3.2" />
      <path d="M2.8 20c0-3.4 2.8-6 6.2-6s6.2 2.6 6.2 6" />
      <path d="M15.5 6a3.2 3.2 0 0 1 0 6.2" />
      <path d="M17.5 14.3c2.4 .5 4.1 2.6 4.1 5.7" />
    </svg>
  );
}

export function CheckCircleIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <circle cx="12" cy="12" r="9.5" />
      <polyline points="7.5,12.5 10.3,15.3 16.5,9" />
    </svg>
  );
}

export function SignalIcon({ size = 20, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} {...base}>
      <line x1="4" y1="19" x2="4" y2="15" />
      <line x1="9.3" y1="19" x2="9.3" y2="11" />
      <line x1="14.6" y1="19" x2="14.6" y2="7" />
      <line x1="20" y1="19" x2="20" y2="3.5" />
    </svg>
  );
}
