import type { CurageResponse, Point } from "../types";
import MapView from "./MapView";
import PointList from "./PointList";
import PointDetail from "./PointDetail";
import DaySlider from "./DaySlider";
import { DropletIcon, PulseIcon } from "./icons";

export default function DashboardScreen({
  points,
  day,
  selectedId,
  onSelect,
  onDayChange,
  onCurage,
  curageResult,
}: {
  points: Point[];
  day: number;
  selectedId: string;
  onSelect: (id: string) => void;
  onDayChange: (day: number) => void;
  onCurage: () => void;
  curageResult: CurageResponse | null;
}) {
  const nbFlood = points.filter((p) => p.flood_level === "rouge").length;
  const nbGite = points.filter((p) => p.days_to_emergence !== null && p.days_to_emergence <= 5).length;
  const selected = points.find((p) => p.id === selectedId);

  return (
    <section className="screen">
      <div className="alerts-bar">
        <div className="alert-pill flood">
          <span className="icon-badge">
            <DropletIcon size={22} />
          </span>
          <span className="alert-figures">
            <span className="alert-num">{nbFlood}</span>
            <span className="alert-label">alerte{nbFlood > 1 ? "s" : ""} inondation</span>
          </span>
        </div>
        <div className="alert-pill gite">
          <span className="icon-badge">
            <PulseIcon size={22} />
          </span>
          <span className="alert-figures">
            <span className="alert-num">{nbGite}</span>
            <span className="alert-label">gîte{nbGite > 1 ? "s" : ""} en fenêtre d'or</span>
          </span>
        </div>
      </div>

      <div className="main-row">
        <div className="card map-col">
          <MapView points={points} onSelect={onSelect} />
          <PointList points={points} selectedId={selectedId} onSelect={onSelect} />
        </div>

        <PointDetail point={selected} onCurage={onCurage} curageResult={curageResult} />
      </div>

      <DaySlider day={day} onChange={onDayChange} />
    </section>
  );
}
