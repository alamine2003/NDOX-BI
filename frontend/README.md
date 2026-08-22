# NDOX BI — Frontend (Dashboard & Simulateur IVR)

Application React + TypeScript (Vite) implémentant la fiche de poste P4 du
cahier des charges : écran mairie, simulateur de téléphone IVR, comparatif
« avec / sans NDOX BI ».

## Démarrer

```bash
npm install
npm run dev
```

Ouvre http://localhost:5173.

## Build de production

```bash
npm run build
npm run preview
```

## Structure

- `src/data/seed.ts` — les 8 points de démonstration (Partie A.6) + le
  scénario scripté J0→J10 de P07, le point vedette de la démo (Partie A.7).
- `src/lib/api.ts` — appels au backend (`http://localhost:8000/api/v1`),
  chaque fonction a un repli silencieux si l'API est injoignable.
- `src/lib/simulate.ts` — simulation locale (mode hors ligne) : le curseur
  temporel reste pilotable même si le backend est down (Partie B.8).
- `src/components/` — un composant par bloc d'écran (carte, liste, détail,
  curseur, téléphone IVR, comparatif).
- `public/audio/` — dépôt attendu des clips wolof de P3 (`{point_id}.mp3`).
  Tant qu'un clip n'existe pas, l'IVR utilise la synthèse vocale du
  navigateur sur le texte français (pas de wolof approximatif inventé ici,
  cf. Partie D du cahier des charges).
- `public/mock.json` — exemple de réponse `GET /points` au format exact du
  contrat d'API (Partie A.5), pour référence par l'équipe backend.

## Dépendance bloquante (Partie B.12)

Le dashboard fonctionne dès maintenant contre les données de seed
embarquées. Dès que le backend expose `/points`, il prend automatiquement
le relais (bandeau « hors ligne » affiché sinon).

## Écart au cahier des charges

La consigne P4 imposait du HTML/CSS/JS vanilla sans build, pour limiter le
risque en hackathon. Ce frontend utilise React + TypeScript + Vite à la
demande explicite du porteur du projet — build vérifié (`npm run build`)
et flux testés (curseur temporel, IVR, certificat de vidange, comparatif).
