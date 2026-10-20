#!/usr/bin/env bash
# Prépare les images intégrées dans la page (ImageMagick 6 requis), sur le modèle du dépôt « Chaîne fonctionnelle ».
#   - src/images/originaux/*.png|jpg : figures d'origine (cours, exercices, études), conservées telles quelles
#   - src/images/*.png               : versions quantifiées (PNG 8 bits) intégrées en data URI
#   - src/images/*.jpg               : photos réduites pour la page
#   - src/images/carte-*.png|jpg     : images des cartes de l'accueil, tirées des contenus (480 × 270)
#   - src/images/accueil.svg         : dessin de l'accueil, intégré tel quel (pas de traitement)
#   - originaux/ch-*                 : figures et photos du cours « Habitat durable » (Word) ; ch-ph-* : photos
#   - originaux/lp-*                 : pages du dossier de plans de l'exercice 1.1 (lecture de plan)
# Usage : bash outils/preparer-images.sh   (depuis la racine du dépôt), puis python3 src/generer.py
set -euo pipefail
shopt -s nullglob
cd "$(dirname "$0")/.."
SRC=src/images/originaux
OUT=src/images

# 1. Figures reprises telles quelles : PNG quantifiés sur fond blanc (au plus 1100 px de large), photos en JPEG
for f in "$SRC"/*.png; do
  b=$(basename "$f")
  case "$b" in
    carte-*) continue ;;  # sources des cartes de l'accueil : voir 2.
    # figures redessinées en SVG et rendues interactives (src/cours_habitat.py) : les originaux restent la référence
    ch-fig01-*|ch-fig02-*|ch-fig05-*|ch-fig06-*|ch-fig11-*|ch-fig15-*|ch-fig-resistances.png) continue ;;
    lp-dp1-page.png) continue ;;  # page d'origine du DP1 : la perspective en est extraite (lp-perspective.png)
    *-ph-*) convert "$f" -background white -alpha remove -alpha off -resize '900x900>' -quality 82 -strip \
              "$OUT/${b%.png}.jpg"; continue ;;
  esac
  convert "$f" -background white -alpha remove -alpha off -resize '1100x>' -strip -colors 256 "PNG8:$OUT/$b"
done
for f in "$SRC"/*.jpg; do
  b=$(basename "$f")
  case "$b" in carte-*) continue ;; esac
  convert "$f" -resize '900x900>' -quality 78 -strip "$OUT/$b"
done

# 2. Images des cartes de l'accueil, tirées des contenus : toutes au même format 480 × 270.
#    remplir : l'image couvre la carte (recadrée) ; entiere : l'image entière sur fond blanc (figures très allongées).
#    Exemples (dépôt « Chaîne fonctionnelle ») :
#      remplir "$SRC/ex1-rav4.jpg"      carte-ex11.jpg  "-quality 80"
#      remplir "$SRC/ex1-ascenseur.png" carte-etude.png "-colors 256" north
#      entiere "$SRC/schema-large.png"  carte-cours-2.png
remplir() { convert "$1" -background white -alpha remove -alpha off -resize 480x270^ -gravity "${4:-center}" \
  -extent 480x270 -strip $3 "$OUT/$2"; }
entiere() { convert "$1" -background "${3:-white}" -alpha remove -alpha off -resize 456x250 -gravity center \
  -extent 480x270 -strip -colors 256 "PNG8:$OUT/$2"; }
remplir "$SRC/ch-fig08-vmc-double-flux.png" carte-cours-1.jpg "-quality 82"   # cours 1 : maison et VMC double flux
remplir "$SRC/lp-perspective.png"          carte-ex11.png    "-colors 256"     # exercice 1.1 : le pavillon

images=("$OUT"/*.png "$OUT"/*.jpg)
if [ ${#images[@]} -gt 0 ]; then
  ls -l "${images[@]}" | awk '{s += $5} END {print NR " images, " int(s / 1024) " Kio"}'
else
  echo "aucune image à intégrer pour l'instant"
fi
