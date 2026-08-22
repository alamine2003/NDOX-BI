import { useEffect, useRef, useState } from "react";
import type { CurageResponse, Point, ScreenId } from "./types";
import { SEED_POINTS } from "./data/seed";
import { computeLocalStateForDay } from "./lib/simulate";
import { fetchPoints, requestCurage, simulateDay } from "./lib/api";
import OfflineBanner from "./components/OfflineBanner";
import Header from "./components/Header";
import TabBar from "./components/TabBar";
import DashboardScreen from "./components/DashboardScreen";
import IvrScreen from "./components/IvrScreen";
import CompareScreen from "./components/CompareScreen";

const AUTOREFRESH_MS = 5000;

export default function App() {
  const [screen, setScreen] = useState<ScreenId>("dashboard");
  const [points, setPoints] = useState<Point[]>(SEED_POINTS);
  const [day, setDay] = useState(0);
  const [selectedId, setSelectedId] = useState("P07");
  const [offline, setOffline] = useState(false);
  const [curagedP02, setCuragedP02] = useState(false);
  const [curageResult, setCurageResult] = useState<CurageResponse | null>(null);

  const curagedP02Ref = useRef(curagedP02);
  curagedP02Ref.current = curagedP02;
  const dayRef = useRef(day);
  dayRef.current = day;

  async function refreshFromApi(): Promise<boolean> {
    const apiPoints = await fetchPoints();
    if (apiPoints) {
      setPoints(apiPoints);
      setOffline(false);
      return true;
    }
    setOffline(true);
    return false;
  }

  async function handleDayChange(nextDay: number) {
    setDay(nextDay);
    await simulateDay(nextDay);
    const ok = await refreshFromApi();
    if (!ok) {
      setPoints(computeLocalStateForDay(nextDay, curagedP02Ref.current));
    }
  }

  async function handleCurage() {
    const result = await requestCurage();
    setCuragedP02(true);
    setCurageResult(result);
    setPoints((prev) => prev.map((p) => (p.id === "P02" ? { ...p, drain_rate_cmh: result.after_cmh } : p)));
  }

  useEffect(() => {
    refreshFromApi();
    const timer = setInterval(async () => {
      const ok = await refreshFromApi();
      if (!ok) {
        setPoints(computeLocalStateForDay(dayRef.current, curagedP02Ref.current));
      }
    }, AUTOREFRESH_MS);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <OfflineBanner offline={offline} />
      <Header day={day} />
      <TabBar active={screen} onChange={setScreen} />

      {screen === "dashboard" && (
        <DashboardScreen
          points={points}
          day={day}
          selectedId={selectedId}
          onSelect={setSelectedId}
          onDayChange={handleDayChange}
          onCurage={handleCurage}
          curageResult={curageResult}
        />
      )}

      {screen === "ivr" && (
        <IvrScreen points={points} selectedId={selectedId} onSelectPoint={setSelectedId} />
      )}

      {screen === "compare" && <CompareScreen />}

      <footer className="note">
        NDOX BI — « L'eau qui parle ». Nous ne mesurons pas la hauteur de l'eau, nous mesurons son âge.
      </footer>
    </>
  );
}
