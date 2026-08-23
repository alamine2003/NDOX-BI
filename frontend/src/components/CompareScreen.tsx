import { useState } from "react";
import { ChartIcon } from "./icons";

export default function CompareScreen() {
  const [launched, setLaunched] = useState(false);

  function launch() {
    setLaunched(false);
    requestAnimationFrame(() => setTimeout(() => setLaunched(true), 50));
  }

  return (
    <section className="screen">
      <table className="compare-table">
        <thead>
          <tr>
            <th>Jour</th>
            <th>Sans NDOX BI</th>
            <th>Avec NDOX BI</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>J-30</td>
            <td>—</td>
            <td>Caniveau curé (priorité 3)</td>
          </tr>
          <tr>
            <td>J-1</td>
            <td>—</td>
            <td>Pré-pompage de 25 cm</td>
          </tr>
          <tr>
            <td>J0</td>
            <td className="big sans">45 cm dans les maisons</td>
            <td className="big avec">18 cm dans la rue, 0 dans les maisons</td>
          </tr>
          <tr>
            <td>J+5</td>
            <td>3 gîtes actifs</td>
            <td>0 émergence</td>
          </tr>
        </tbody>
      </table>

      <button className="compare-launch" onClick={launch}>
        <ChartIcon size={18} />
        Lancer la comparaison
      </button>

      <div className="bars-card">
        <div className="bars">
          <div className="bar-col sans">
            <div className="bar-value">45 cm</div>
            <div className="bar" style={{ height: launched ? 220 : 0 }} />
            <div className="bar-label">Sans NDOX BI</div>
          </div>
          <div className="bar-col avec">
            <div className="bar-value">18 cm</div>
            <div className="bar" style={{ height: launched ? 88 : 0 }} />
            <div className="bar-label">Avec NDOX BI</div>
          </div>
        </div>
      </div>
    </section>
  );
}
