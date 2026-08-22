import type { CurageResponse, Point } from "../types";
import MapView from "./MapView";
import PointList from "./PointList";
import PointDetail from "./PointDetail";
import DaySlider from "./DaySlider";

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
          {nbFlood} alerte{nbFlood > 1 ? "s" : ""} inondation
        </div>
        <div className="alert-pill gite">
          {nbGite} gîte{nbGite > 1 ? "s" : ""} en fenêtre d'or
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
