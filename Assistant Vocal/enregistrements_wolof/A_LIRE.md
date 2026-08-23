# Enregistrements wolof — mode d'emploi

Enregistre les messages (téléphone, PC, peu importe) et **dépose tous les fichiers
dans ce dossier**. Je m'occupe de la conversion, du nettoyage et de l'installation.

## Nommage

Un fichier par message, nommé avec la **clé**. L'extension n'a aucune importance
(`.m4a`, `.mp3`, `.wav`, `.ogg`, `.opus`…). Un préfixe numérique est accepté et
ignoré — `01_intro.m4a` et `intro.m4a` sont équivalents.

---

## Structure de l'annonce — 6 clips

Ces six-là encadrent toutes les annonces. `intro` et `outro` seront entendus à
**chaque** appui sur le bouton bleu : ce sont les plus importants.

| Clé | À dire en wolof |
|---|---|
| `intro` | Bonjour. Voici les nouvelles de l'eau dans votre quartier. |
| `outro` | Merci. Revenez demain. |
| `offline` | Je n'ai pas de réseau. Voici les dernières nouvelles connues. |
| `press_to_report` | Appuyez sur le bouton rouge et parlez pour signaler de l'eau. |
| `thanks` | Merci. Votre message a été reçu. |
| `too_short` | Je n'ai pas entendu. Recommencez et parlez plus fort. |

## Phase 1 — Anticipation, la veille

| Clé | À dire en wolof |
|---|---|
| `weather_alert_24h` | Une forte pluie arrive demain. Préparez votre quartier maintenant. |
| `prevent_drain` | Dégagez les caniveaux et videz vos récipients avant ce soir. |

## Phase 2 — L'eau monte

| Clé | À dire en wolof |
|---|---|
| `flood_vigilance_50` | L'eau atteint 50 centimètres. Restez informés. |
| `flood_alert_65` | L'eau approche du seuil dangereux. Préparez-vous à agir. |
| `flood_urgent_70` | Il reste peu de temps. Évacuez les zones basses maintenant. |
| `flood_critical_80` | Alerte maximale. L'eau dépasse 80 centimètres. Cette zone est inondée. |

## Phase 2 bis — L'estimation prédictive

Ta version disait « dans environ **{N}** minutes ». Impossible à pré-enregistrer :
c'est justement le chiffre variable qui force les autres à utiliser du TTS. Je l'ai
transformé en **trois phrases complètes**, une par tranche. La borne calcule le
délai et choisit la bonne — aucun chiffre à assembler, la voix reste naturelle.

| Clé | À dire en wolof |
|---|---|
| `flood_predictive_15` | Au rythme actuel, l'eau atteindra le seuil critique dans moins d'un quart d'heure. |
| `flood_predictive_30` | Au rythme actuel, l'eau atteindra le seuil critique dans moins d'une demi-heure. |
| `flood_predictive_60` | Au rythme actuel, l'eau atteindra le seuil critique dans moins d'une heure. |

## Phase 3 — Sécurité immédiate

| Clé | À dire en wolof |
|---|---|
| `action_evacuate` | Évacuez immédiatement enfants et personnes âgées. |
| `action_no_wade` | Ne traversez jamais l'eau à pied, même peu profonde. |
| `action_electricity` | Coupez le courant si l'eau approche des installations électriques. |

## Phase 4 — Canal bouché

| Clé | À dire en wolof |
|---|---|
| `blockage_detected` | Ce canal semble bloqué. Un technicien a été prévenu. |
| `action_no_dump` | Ne jetez pas de déchets dans le canal. Ils bloquent l'écoulement. |

## Phase 5 — Décrue : l'âge de l'eau

| Clé | À dire en wolof |
|---|---|
| `stagnation_started` | La grosse eau est partie, mais une flaque reste. Nous la surveillons. |
| `stagnation_day4` | Cette eau est là depuis quatre jours. Même petite, elle devient dangereuse. |

## Phase 6 — Fenêtre d'or paludisme

Deux messages contenaient `{N}`. **Enregistre d'abord les versions sans chiffre**
(les deux premières lignes) — la borne les joue automatiquement tant que les
morceaux numérotés sont absents.

| Clé | À dire en wolof |
|---|---|
| `malaria_window_open` | Cette eau stagne depuis plusieurs jours. Les moustiques arrivent bientôt. |
| `malaria_emergence_countdown` | Il reste très peu de jours avant l'apparition des moustiques. Agissez maintenant. |
| `action_empty_now` | Videz cette eau tout de suite, avant qu'il ne soit trop tard. |

## Phase 7 — Seuil critique paludisme

| Clé | À dire en wolof |
|---|---|
| `malaria_critical` | Cette eau stagne depuis plus de sept jours. Le danger est maximum. |
| `action_net_now` | Dormez sous une moustiquaire imprégnée dès ce soir, sans exception. |

## Phase 8 — Résolution

| Clé | À dire en wolof |
|---|---|
| `treatment_done` | Ce point a été traité. Le risque est écarté. |

---

## FACULTATIF — les chiffres parlés

À faire **seulement si tu as le temps**, et **après** tout le reste. Ça permet à la
borne de dire le nombre exact de jours au lieu de « plusieurs ».

Il faut alors les deux moitiés de phrase **et** les nombres. Enregistre les moitiés
en enchaînant naturellement, comme si le chiffre était là.

| Clé | À dire en wolof |
|---|---|
| `malaria_window_open_a` | Cette eau stagne depuis… |
| `malaria_window_open_b` | …jours. Les moustiques arrivent bientôt. |
| `malaria_emergence_countdown_a` | Il reste… |
| `malaria_emergence_countdown_b` | …jours avant l'apparition des moustiques. Agissez maintenant. |
| `num_1` … `num_10` | un, deux, trois, quatre, cinq, six, sept, huit, neuf, dix |

Si une seule de ces pièces manque, la borne repasse toute seule sur la version sans
chiffre. Aucun risque à en faire la moitié.

---

## Conseils

- **Pièce silencieuse**, téléphone à ~20 cm de la bouche, jamais collé.
- **Laisse une demi-seconde de blanc** avant et après. Le nettoyage automatique
  les rognera proprement — c'est ce qui évite que la séquence sonne hachée.
- **Un fichier = un message.** La borne assemble elle-même 5 à 9 clips selon la
  situation ; ils doivent pouvoir s'enchaîner dans n'importe quel ordre.
- **Même voix, même distance, même débit** pour tous. Sinon l'enchaînement s'entend.
- **Le ton compte.** `flood_urgent_70`, `flood_critical_80`, `action_evacuate` et
  `malaria_critical` sont des messages d'urgence — mets-y l'urgence. C'est
  exactement ce qu'aucune synthèse ne sait faire (dossier §8.2).

## Tu n'es pas obligé de tout faire d'un coup

Les clés absentes gardent le placeholder français et la borne continue de tourner.

**Les huit prioritaires**, ceux qu'on entend dans la démo J0 :
`intro`, `flood_urgent_70`, `flood_predictive_30`, `action_evacuate`,
`action_electricity`, `action_no_wade`, `press_to_report`, `outro`.

Puis, pour le moment J4 de la fenêtre d'or : `malaria_window_open`,
`action_empty_now`. Et pour la punchline J6 : `treatment_done`.
