import { BASE_DATE } from "../data/seed";

function fmtClock(date: Date): string {
  const dd = String(date.getUTCDate()).padStart(2, "0");
  const mm = String(date.getUTCMonth() + 1).padStart(2, "0");
  const hh = String(date.getUTCHours()).padStart(2, "0");
  const mi = String(date.getUTCMinutes()).padStart(2, "0");
  return `${dd}/${mm} ${hh}:${mi}`;
}

export default function Header({ day }: { day: number }) {
  const clock = fmtClock(new Date(BASE_DATE.getTime() + day * 86400000));
  return (
    <header className="app-header">
      <div className="brand">NDOX BI</div>
      <div className="commune">Commune de Keur Massar</div>
      <div className="clock">{clock}</div>
    </header>
  );
}
