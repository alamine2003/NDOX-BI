import { CircleMarker, MapContainer, TileLayer, Tooltip } from "react-leaflet";
import type { Point } from "../types";
import { COLOR } from "../data/seed";

export default function MapView({
  points,
  onSelect,
}: {
  points: Point[];
  onSelect: (id: string) => void;
}) {
  return (
    <MapContainer center={[14.775, -17.352]} zoom={12.5} className="leaflet-map">
      <TileLayer
        attribution="&copy; OpenStreetMap"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {points.map((p) => (
        <CircleMarker
          key={p.id}
          center={[p.lat, p.lng]}
          radius={6 + Math.sqrt(p.population_exposee) / 6}
          color={COLOR.bleu}
          weight={2}
          fillColor={COLOR[p.flood_level]}
          fillOpacity={0.85}
          eventHandlers={{ click: () => onSelect(p.id) }}
        >
          <Tooltip>{p.name}</Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
