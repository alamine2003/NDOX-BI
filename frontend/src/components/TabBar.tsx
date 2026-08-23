import type { ScreenId } from "../types";
import { ChartIcon, MapPinIcon, PhoneIcon } from "./icons";

const TABS: { id: ScreenId; label: string; Icon: typeof MapPinIcon }[] = [
  { id: "dashboard", label: "Écran mairie", Icon: MapPinIcon },
  { id: "ivr", label: "Téléphone (IVR)", Icon: PhoneIcon },
  { id: "compare", label: "Avec / Sans", Icon: ChartIcon },
];

export default function TabBar({
  active,
  onChange,
}: {
  active: ScreenId;
  onChange: (id: ScreenId) => void;
}) {
  return (
    <nav className="tabbar">
      {TABS.map(({ id, label, Icon }) => (
        <button key={id} className={active === id ? "active" : ""} onClick={() => onChange(id)}>
          <Icon size={19} />
          {label}
        </button>
      ))}
    </nav>
  );
}
