#!/usr/bin/env bash
# Prépare les images intégrées dans la page (ImageMagick 6 requis), sur le modèle du dépôt « Chaîne fonctionnelle ».
#   - src/images/originaux/*.png|jpg : figures d'origine (cours, exercices, études), conservées telles quelles
#   - src/images/*.png               : versions quantifiées (PNG 8 bits) intégrées en data URI
#   - src/images/*.jpg               : photos réduites pour la page
#   - src/images/carte-*.png|jpg     : images des cartes de l'accueil, tirées des contenus (480 × 270)
#   - src/images/accueil.svg         : dessin de l'accueil, intégré tel quel (pas de traitement)
# Usage : bash outils/preparer-images.sh   (depuis la racine du dépôt), puis python3 src/generer.py
set -euo pipefail
shopt -s nullglob
cd "$(dirname "$0")/.."
SRC=src/images/originaux
OUT=src/images

# 1. Figures reprises telles quelles : PNG quantifiés sur fond blanc, photos réduites
for f in "$SRC"/*.png; do
  b=$(basename "$f")
  case "$b" in carte-*) continue ;; esac  # sources des cartes de l'accueil : voir 2.
  convert "$f" -background white -alpha remove -alpha off -strip -colors 256 "PNG8:$OUT/$b"
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

images=("$OUT"/*.png "$OUT"/*.jpg)
if [ ${#images[@]} -gt 0 ]; then
  ls -l "${images[@]}" | awk '{s += $5} END {print NR " images, " int(s / 1024) " Kio"}'
else
  echo "aucune image à intégrer pour l'instant"
fi
