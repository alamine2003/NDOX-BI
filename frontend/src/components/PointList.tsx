import type { Point } from "../types";
import { COLOR } from "../data/seed";
import { UsersIcon } from "./icons";

const ORDER: Record<string, number> = { rouge: 0, jaune: 1, vert: 2 };

export default function PointList({
  points,
  selectedId,
  onSelect,
}: {
  points: Point[];
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  const sorted = [...points].sort((a, b) => ORDER[a.flood_level] - ORDER[b.flood_level]);
  return (
    <div className="point-list">
      {sorted.map((p) => (
        <div
          key={p.id}
          className={`point-row ${p.id === selectedId ? "selected" : ""}`}
          onClick={() => onSelect(p.id)}
        >
          <span className="dot" style={{ background: COLOR[p.flood_level] }} />
          <span className="pname">{p.name}</span>
          <span className="ppop">
            <UsersIcon size={13} />
            {p.population_exposee.toLocaleString("fr-FR")}
          </span>
        </div>
      ))}
    </div>
  );
}
