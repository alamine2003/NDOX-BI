import type { ScreenId } from "../types";

const TABS: { id: ScreenId; label: string }[] = [
  { id: "dashboard", label: "Écran mairie" },
  { id: "ivr", label: "Téléphone (IVR)" },
  { id: "compare", label: "Avec / Sans" },
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
      {TABS.map((tab) => (
        <button
          key={tab.id}
          className={active === tab.id ? "active" : ""}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
