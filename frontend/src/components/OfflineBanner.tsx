import { WifiOffIcon } from "./icons";

export default function OfflineBanner({ offline }: { offline: boolean }) {
  if (!offline) return null;
  return (
    <div className="offline-banner">
      <WifiOffIcon size={18} />
      Hors ligne — dernières données connues
    </div>
  );
}
