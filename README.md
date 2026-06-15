# Taxi 487 — Carte GPS interactive

Carte du trajet taxi du 12 juin 2026 avec arrêts, vocales et filtre horaire.

**Mot de passe :** `487`

## Langues

Bouton **FR | عربي** en haut (écran de connexion et carte).

## Test local

```bash
npm run dev
```

Ouvrir http://localhost:3000 — mot de passe `487`

## Déploiement Netlify

1. Connecter ce repo sur [Netlify](https://netlify.com)
2. Build command : `node build-netlify.js`
3. Publish directory : `dist`

Ou glisser-déposer le dossier `dist/` après `npm run build`.

## Structure

| Fichier | Rôle |
|---------|------|
| `taxi-map.template.html` | Source de l'app |
| `build-netlify.js` | Génère `dist/` |
| `taxi.txt` | Données GPS |
| `487_vocales/` | Enregistrements audio |

Les données GPS sont **intégrées dans la page** — pas de chargement externe de `taxi.txt`.
