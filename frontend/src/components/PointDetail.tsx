import type { Point } from "../types";
import { COLOR, CURAGE_UTILE, TYPE_LABEL } from "../data/seed";
import type { CurageResponse } from "../types";
import {
  ClockIcon,
  DropletIcon,
  GaugeIcon,
  PulseIcon,
  ShieldCheckIcon,
  ShieldXIcon,
  UsersIcon,
} from "./icons";

export default function PointDetail({
  point,
  onCurage,
  curageResult,
}: {
  point: Point | undefined;
  onCurage: () => void;
  curageResult: CurageResponse | null;
}) {
  if (!point) return <div className="card detail-col" />;

  const utile = CURAGE_UTILE[point.type];

  return (
    <div className="card detail-col">
      <h2>
        {point.name}
        <span className="badge">
          Type {point.type} — {TYPE_LABEL[point.type]}
        </span>
      </h2>

      <div className="indice-block">
        <div className="indice-label">
          <DropletIcon size={15} /> Indice I (inondation)
        </div>
        <div className="indice-bar">
          <div style={{ width: `${Math.round(point.flood_index * 100)}%`, background: COLOR[point.flood_level] }} />
        </div>
        <div className={`indice-value level-${point.flood_level}`}>
          {point.flood_index.toFixed(2)} — {point.flood_level.toUpperCase()}
        </div>
      </div>

      <div className="indice-block">
        <div className="indice-label">
          <PulseIcon size={15} /> Indice P (paludisme)
        </div>
        <div className="indice-bar">
          <div style={{ width: `${Math.round(point.malaria_index * 100)}%`, background: COLOR[point.malaria_level] }} />
        </div>
        <div className={`indice-value level-${point.malaria_level}`}>
          {point.malaria_index.toFixed(2)} — {point.malaria_level.toUpperCase()}
        </div>
      </div>

      {point.days_to_emergence !== null ? (
        <div className="emergence">
          <ClockIcon size={30} />
          Émergence dans <span className="emergence-num">{point.days_to_emergence}</span> jours
        </div>
      ) : (
        <div className="emergence none">Pas de gîte actif</div>
      )}

      <div className="meta-row">
        <GaugeIcon size={16} /> Eau : <b>{point.water_cm} cm</b> · Stagnation : <b>{point.stagnation_days} j</b>
      </div>
      <div className="meta-row">
        <UsersIcon size={16} /> Population exposée : <b>{point.population_exposee.toLocaleString("fr-FR")}</b>
      </div>

      <div className={`curage-note ${utile ? "ok" : "ko"}`}>
        {utile ? <ShieldCheckIcon size={18} /> : <ShieldXIcon size={18} />}
        Curage {utile ? "utile [OK]" : "inutile [X]"}
        {!utile && ` — ${point.type === "D" ? "nappe phréatique" : "cuvette sans exutoire"}`}
      </div>

      {point.id === "P02" && (
        <>
          <button className="curage-btn" onClick={onCurage}>
            Certificat de vidange
          </button>
          {curageResult && (
            <div className={`curage-result ${curageResult.verdict === "CONFORME" ? "conforme" : "nonconforme"}`}>
              {curageResult.verdict === "CONFORME" ? <ShieldCheckIcon size={26} /> : <ShieldXIcon size={26} />}
              {curageResult.verdict}
            </div>
          )}
        </>
      )}
    </div>
  );
}
