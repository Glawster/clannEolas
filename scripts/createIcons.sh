#!/usr/bin/env bash

set -euo pipefail

scriptDir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repoDir="$(cd -- "${scriptDir}/.." && pwd)"
src="${repoDir}/brand/icons/appIcon.png"
out="${repoDir}/output/icons/favicon"

confirm=false
if [[ "${1:-}" == "--confirm" || "${1:-}" == "-y" ]]; then
    confirm=true
elif [[ $# -gt 0 ]]; then
    echo "Usage: $0 [--confirm|-y]" >&2
    exit 2
fi

if ! logUtilsPath="$(
    python3 -c 'import importlib.util; spec = importlib.util.find_spec("organiseMyProjects"); print(next(iter(spec.submodule_search_locations)) + "/logUtils.sh" if spec and spec.submodule_search_locations else "")'
)"; then
    echo "Error: unable to locate organiseMyProjects/logUtils.sh." >&2
    exit 1
fi

if [[ ! -f "$logUtilsPath" ]]; then
    echo "Error: organiseMyProjects/logUtils.sh was not found." >&2
    exit 1
fi

# shellcheck source=/dev/null
source "$logUtilsPath"
setApplication "createIcons"

if command -v magick >/dev/null 2>&1; then
    imageMagick=(magick)
elif command -v convert >/dev/null 2>&1; then
    imageMagick=(convert)
else
    log_error "ImageMagick is required (expected 'magick' or 'convert')."
    exit 1
fi

if [[ ! -f "$src" ]]; then
    log_error "Source icon not found: $src"
    exit 1
fi

log_doing "creating website icons"
log_value "source" "$src"
log_value "output directory" "$out"
log_value "image processor" "${imageMagick[0]}"

if [[ "$confirm" != true ]]; then
    log_info "dry-run: pass --confirm to create the icon files"
    log_box "Icon generation preview\n${out}"
    exit 0
fi

mkdir -p "$out"

iconCount=0
for size in 16 32 48 64 72 96 128 144 152 180 192 256 384 512 1024; do
    log_action "creating favicon-${size}x${size}.png"
    "${imageMagick[@]}" "$src" \
        -filter Lanczos \
        -resize "${size}x${size}" \
        -strip \
        "$out/favicon-${size}x${size}.png"
    ((iconCount += 1))
done

log_action "creating favicon.ico"
"${imageMagick[@]}" \
    "$out/favicon-16x16.png" \
    "$out/favicon-32x32.png" \
    "$out/favicon-48x48.png" \
    "$out/favicon.ico"

log_action "creating apple-touch-icon.png"
cp "$out/favicon-180x180.png" "$out/apple-touch-icon.png"

log_action "creating android-chrome-192x192.png"
cp "$out/favicon-192x192.png" "$out/android-chrome-192x192.png"

log_action "creating android-chrome-512x512.png"
cp "$out/favicon-512x512.png" "$out/android-chrome-512x512.png"

((iconCount += 3))
log_done "website icons created"
log_box "Icon generation complete\n${iconCount} PNG files and 1 ICO file\n${out}"
