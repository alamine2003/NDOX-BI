import { useState } from "react";
import type { Point } from "../types";
import { requestReport, requestVoice } from "../lib/api";
import { textForPoint } from "../lib/simulate";
import { PhoneIcon, SignalIcon, UsersIcon } from "./icons";

const USSD_CODE = "*384*88#";

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

function menuFor(point: Point | undefined): string {
  if (!point) return "CON Chargement...";
  return `CON Bienvenue sur NDOX BI\n${point.name}\n\n1. Etat du quartier (voix)\n2. Signaler de l'eau\n3. Poste de sante proche`;
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
  const point = points.find((p) => p.id === selectedId);

  const [dialed, setDialed] = useState("");
  const [ussdText, setUssdText] = useState(menuFor(point));
  const [ended, setEnded] = useState(false);
  const [quorum, setQuorum] = useState({ current: 0, needed: 3 });

  function resetMenu() {
    setUssdText(menuFor(point));
    setEnded(false);
  }

  async function playVoice() {
    if (!point) return;
    setUssdText("CON Connexion à la voix NDOX BI...");
    const voice = await requestVoice(point.id);
    const textFr = voice?.text_fr ?? textForPoint(point);
    setUssdText(`END ${textFr}`);
    setEnded(true);

    const audio = new Audio(`/audio/${point.id}.mp3`);
    audio.play().catch(() => speak(textFr));
  }

  async function reportWater() {
    if (!point) return;
    setUssdText("CON Envoi du signalement...");
    const result = await requestReport(point.id, quorum.current);
    setQuorum({ current: result.quorum, needed: result.quorum_needed });
    setUssdText(`END Merci. Signalement transmis.\nQuorum ${result.quorum}/${result.quorum_needed} atteint pour valider.`);
    setEnded(true);
  }

  function showHealthPost() {
    if (!point) return;
    setUssdText(`END Poste de sante le plus proche de\n${point.name} : accessible.`);
    setEnded(true);
  }

  function press(key: string) {
    const next = (dialed + key).slice(-14);
    setDialed(next);

    if (key === "0") {
      resetMenu();
      return;
    }
    if (key === "1") return void playVoice();
    if (key === "2") return void reportWater();
    if (key === "3") return void showHealthPost();

    if (ended) return; // touche non reconnue apres fin de session
    setUssdText(menuFor(point) + "\n\n(Option invalide)");
  }

  return (
    <section className="screen">
      <div className="ivr-wrap">
        <div className="phone">
          <div className="phone-notch" />
          <div className="phone-status">
            <span>{USSD_CODE}</span>
            <span>NDOX BI Réseau</span>
          </div>

          <div className="ussd-screen">
            <div className="ussd-header">
              <span className="carrier-badge">
                <SignalIcon size={13} /> Africa's Talking
              </span>
              <span className="ussd-tag">{ended ? "END" : "USSD"}</span>
            </div>
            <div className="ussd-body">
              {ussdText.split("\n").map((line, i) => {
                const isPrefix = i === 0 && (line.startsWith("CON") || line.startsWith("END"));
                if (!isPrefix) return <div key={i}>{line || " "}</div>;
                const [prefix, ...rest] = line.split(" ");
                return (
                  <div key={i}>
                    <span className="ussd-prefix">{prefix}</span> {rest.join(" ")}
                  </div>
                );
              })}
            </div>
            <div className="ussd-footer">
              <button onClick={resetMenu}>Nouvelle session ↻</button>
              <button className="danger" onClick={() => setUssdText("END Session terminée.")}>
                Fin
              </button>
            </div>
          </div>

          <div className="dial-readout">{dialed || "— — — —"}</div>

          <div className="keypad">
            {[
              ["1", ""],
              ["2", "ABC"],
              ["3", "DEF"],
              ["4", "GHI"],
              ["5", "JKL"],
              ["6", "MNO"],
              ["7", "PQRS"],
              ["8", "TUV"],
              ["9", "WXYZ"],
            ].map(([num, sub]) => (
              <button key={num} onClick={() => press(num)}>
                <span className="kp-num">{num}</span>
                <span className="kp-sub">{sub}</span>
              </button>
            ))}
            <button className="zero" onClick={() => press("0")}>
              <span className="kp-num">0</span>
              <span className="kp-sub">MENU</span>
            </button>
          </div>
        </div>

        <div className="ivr-side card">
          <label htmlFor="ivr-point">
            <PhoneIcon size={15} /> Point appelé
          </label>
          <select
            id="ivr-point"
            value={selectedId}
            onChange={(e) => {
              onSelectPoint(e.target.value);
              setEnded(false);
              setUssdText(menuFor(points.find((p) => p.id === e.target.value)));
            }}
          >
            {points.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id} — {p.name}
              </option>
            ))}
          </select>

          <div className="ivr-help">
            <div className="ivr-help-row">
              <span className="key-chip">1</span> État vocal du quartier
            </div>
            <div className="ivr-help-row">
              <span className="key-chip">2</span> Signaler de l'eau (bouton rouge)
            </div>
            <div className="ivr-help-row">
              <span className="key-chip">3</span> Poste de santé le plus proche
            </div>
            <div className="ivr-help-row">
              <span className="key-chip">0</span> Retour au menu
            </div>
          </div>

          <div className="quorum-box">
            <UsersIcon size={18} />
            <span>Quorum signalements</span>
            <div className="quorum-track">
              <div
                className="quorum-fill"
                style={{ width: `${Math.min(100, (quorum.current / quorum.needed) * 100)}%` }}
              />
            </div>
            <span>
              {quorum.current}/{quorum.needed}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
