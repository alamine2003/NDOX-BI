import { useState } from "react";
import type { Point } from "../types";
import { requestReport, requestVoice } from "../lib/api";
import { textForPoint } from "../lib/simulate";

/**
 * Pas de wolof pré-enregistré ici : selon la Partie D du cahier des charges,
 * un wolof approximatif fait perdre des points. La voix wolof officielle
 * (P3, livrée à T+3:00) doit être déposée dans public/audio/{point_id}.mp3.
 * En attendant / à défaut, on affiche le texte français et on utilise la
 * synthèse vocale du navigateur pour que "le simulateur joue vraiment du son".
 */
function speak(text: string) {
  if (!("speechSynthesis" in window)) return;
  try {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "fr-FR";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  } catch {
    /* environnement sans synthèse vocale : on ignore silencieusement */
  }
}

export default function IvrScreen({
  points,
  selectedId,
  onSelectPoint,
}: {
  points: Point[];
  selectedId: string;
  onSelectPoint: (id: string) => void;
}) {
  const [dialed, setDialed] = useState("");
  const [lcd, setLcd] = useState("Composez un code : #221#");
  const [quorumMsg, setQuorumMsg] = useState("Aucun signalement pour l'instant.");
  const [localQuorum, setLocalQuorum] = useState(0);

  const point = points.find((p) => p.id === selectedId);

  async function playVoice() {
    if (!point) return;
    const voice = await requestVoice(point.id);
    const textFr = voice?.text_fr ?? textForPoint(point);
    setLcd(`${point.id} — ${textFr}`);

    const audio = new Audio(`/audio/${point.id}.mp3`);
    audio.play().catch(() => speak(textFr));
  }

  async function reportWater() {
    if (!point) return;
    const result = await requestReport(point.id, localQuorum);
    setLocalQuorum(result.quorum);
    setQuorumMsg(`Signalement enregistré — quorum ${result.quorum}/${result.quorum_needed}`);
    setLcd("Merci. Signalement transmis.");
  }

  function showHealthPost() {
    if (!point) return;
    setLcd(`Poste de santé le plus proche de ${point.name} : accessible.`);
  }

  function press(key: string) {
    const next = (dialed + key).slice(-12);
    setDialed(next);
    if (key === "1") playVoice();
    else if (key === "2") reportWater();
    else if (key === "3") showHealthPost();
    else setLcd("Code composé : " + next);
  }

  return (
    <section className="screen">
      <div className="ivr-wrap">
        <div className="phone">
          <div className="carrier">Orange · Simulateur IVR</div>
          <div className="screen-lcd">{lcd}</div>
          <div className="keypad">
            {["1", "2", "3", "4", "5", "6", "7", "8", "9"].map((k) => (
              <button key={k} onClick={() => press(k)}>
                {k}
              </button>
            ))}
            <button className="zero" onClick={() => press("0")}>
              0
            </button>
          </div>
        </div>

        <div className="ivr-side card">
          <label htmlFor="ivr-point">Point appelé</label>
          <select id="ivr-point" value={selectedId} onChange={(e) => onSelectPoint(e.target.value)}>
            {points.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id} — {p.name}
              </option>
            ))}
          </select>
          <div className="ivr-help">
            <p>
              <b>1</b> — État vocal du quartier
            </p>
            <p>
              <b>2</b> — Signaler de l'eau (bouton rouge)
            </p>
            <p>
              <b>3</b> — Poste de santé le plus proche
            </p>
          </div>
          <div className="quorum-box">{quorumMsg}</div>
        </div>
      </div>
    </section>
  );
}
