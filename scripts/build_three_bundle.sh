#!/usr/bin/env bash
# Rifà resources/js/pya_three_scene.min.js: three.js con GLTFLoader e
# OrbitControls in uno script classico (window.PYA_THREE), per la scena 3D
# dell'HTML della narrativa (modules/s3dgraphy/em_narrative_3d.py). Serve
# solo a chi sviluppa: npm ed esbuild in una cartella temporanea.
set -euo pipefail
THREE_VERSION="${THREE_VERSION:-0.186.1}"
ESBUILD_VERSION="${ESBUILD_VERSION:-0.28.2}"
QUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RADICE="$(dirname "$QUI")"
LAVORO="$(mktemp -d)"
trap 'rm -rf "$LAVORO"' EXIT
cp "$QUI/three_bundle_entry.js" "$LAVORO/entry.js"
cd "$LAVORO"
npm init -y >/dev/null
npm install --no-audit --no-fund --silent "three@$THREE_VERSION" "esbuild@$ESBUILD_VERSION"
mkdir -p "$RADICE/resources/js"
# la licenza MIT vuole la nota di copyright in ogni copia, anche nelle pagine
# esportate che portano il pacchetto: la stessa riga @license dei file di three
ANNI="$(grep -o '2010-[0-9][0-9][0-9][0-9]' node_modules/three/LICENSE | head -1)"
npx esbuild entry.js --bundle --minify --format=iife --target=es2020 --legal-comments=none \
  --banner:js="/*! three.js $THREE_VERSION — @license Copyright $ANNI three.js authors, SPDX-License-Identifier: MIT (https://threejs.org; il testo in THREE_LICENSE.txt) — con GLTFLoader e OrbitControls; pyArchInit, scripts/build_three_bundle.sh */" \
  --outfile="$RADICE/resources/js/pya_three_scene.min.js"
cp node_modules/three/LICENSE "$RADICE/resources/js/THREE_LICENSE.txt"
echo "fatto: $(wc -c < "$RADICE/resources/js/pya_three_scene.min.js") byte"
