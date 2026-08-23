# Addendum au contrat d'API — champs requis par la borne vocale

À valider collectivement (règle A.8 : personne ne modifie le contrat seul).
Demandé par **P3** à **P2**. Quatre champs à ajouter à chaque objet de `GET /points`.

## Ce qui manque aujourd'hui

Les 8 phases de messages ne sont pas toutes déclenchables avec les champs actuels.
Trois phases sur huit n'ont aucune source de donnée :

| Phase | Message | Champ manquant |
|---|---|---|
| 1 — Anticipation | `weather_alert_24h`, `prevent_drain` | `rain_forecast_24h_mm` |
| 2 bis — Prédictif | `flood_predictive_*` | `rise_rate_cmh` |
| 4 — Blocage | `blockage_detected` | `blockage_confirmed` |
| 8 — Résolution | `treatment_done` | `treated` |

## Les quatre champs

```jsonc
{
  "id": "P07",
  // ... champs existants inchangés ...

  "rain_forecast_24h_mm": 55.0,   // mm de pluie prévus sous 24 h (Open-Meteo)
  "rise_rate_cmh": 18.0,          // vitesse de montée en cm/h, négative si décrue
  "blockage_confirmed": false,    // canal bouché confirmé (facultatif, voir plus bas)
  "treated": false                // curage ou larvicidage effectué sur ce point
}
```

### `rain_forecast_24h_mm` — obligatoire

Cumul de précipitations prévu sur 24 h, en mm. Vient d'Open-Meteo, déjà utilisé
pour l'indice I. Sans lui, **la phase 1 n'existe pas** : la borne ne peut jamais
dire « préparez-vous, la pluie arrive demain », et le projet perd son horizon
« ANTICIPER » (dossier §9.2).

La borne déclenche au-delà de **40 mm**, seuil repris de la règle de pré-pompage
du dossier §9.2.

### `rise_rate_cmh` — recommandé

Vitesse de montée en cm/h. C'est la même grandeur que le `vitesse_montee_cmh` déjà
présent dans `indice_inondation()` (§7.2) — il suffit de l'exposer.

**Non bloquant** : la borne la recalcule elle-même à partir de ses relevés
successifs sur 10 minutes. Mais elle sonde toutes les 30 s, donc après un
redémarrage il lui faut une minute avant de pouvoir estimer quoi que ce soit.
Le champ du backend est prioritaire quand il est présent.

### `blockage_confirmed` — facultatif

Booléen. **Non bloquant** : en son absence la borne déduit le blocage de
`type == "B"` et `drain_rate_cmh < 0.5 × drain_rate_baseline_cmh`, ce qui est
exactement la règle de détection d'anomalie du dossier §7.6.

À fournir seulement si le backend applique une règle plus fine, ou si un
technicien a confirmé — le message dit « un technicien a été prévenu », donc
mieux vaut que ce soit vrai.

### `treated` — obligatoire pour la démo

Booléen, passe à `true` après un curage ou un larvicidage. C'est le **J6** du
scénario, la punchline « les moustiques ne sont jamais nés ». Quand il est vrai,
la borne ne dit plus que `treatment_done` et se tait sur le reste.

Naturellement piloté par `POST /simulate` et `POST /curage`.

## Point de désaccord à trancher en équipe

**Les seuils vocaux ne correspondent pas au seed de démo.**

Les messages de la phase 2 se déclenchent à **50 / 65 / 70 / 80 cm**. Or l'exemple
du contrat (A.5) et le scénario J0 (A.7) mettent P07 à **42,5 cm** en `flood_level:
"rouge"`. Avec ces valeurs, **aucun message d'inondation ne sortirait** pendant la
démo : 42,5 est sous le premier seuil.

Trois sorties possibles, à choisir ensemble :

1. **Monter le seed** — P07 à 72 cm au lieu de 42,5. C'est ce que fait le
   `cache.json` de la borne aujourd'hui. Le plus simple, aucun code à changer.
2. **Descendre les seuils vocaux** à 30 / 40 / 45 / 50 cm. Cohérent avec un
   quartier où 42 cm est déjà grave, mais il faut réenregistrer `flood_vigilance_50`
   et `flood_critical_80` qui **citent les chiffres dans le texte**.
3. **Découpler** : `flood_level` pilote le dashboard, `water_cm` pilote la voix.
   C'est déjà le cas techniquement, mais il faut assumer qu'un point puisse être
   rouge à l'écran et muet à la borne — mauvaise idée devant un jury.

**Recommandation : l'option 1.** C'est la seule qui ne demande ni de recoder ni de
réenregistrer, et 72 cm rend le scénario J0 plus spectaculaire — la borne enchaîne
alors `flood_urgent_70`, l'estimation prédictive, puis les trois consignes de sécurité.

## Ce qui ne change pas

`GET /points/{id}/voice` reste la source prioritaire : quand le backend répond, sa
`audio_sequence` est jouée telle quelle. Le moteur local des 8 phases n'est utilisé
que hors ligne — c'est-à-dire pendant la démo du coupe-WiFi, et tant que le backend
n'existe pas.

Autrement dit : **P3 n'est bloqué par personne**, et ces champs améliorent la borne
sans jamais l'empêcher de fonctionner.
