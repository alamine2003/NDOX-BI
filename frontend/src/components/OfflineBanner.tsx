export default function OfflineBanner({ offline }: { offline: boolean }) {
  if (!offline) return null;
  return <div className="offline-banner">Hors ligne — dernières données connues</div>;
}
