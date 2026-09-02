#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/../.." && pwd)"
build_root="${project_root}/.build/macos"
venv_dir="${build_root}/venv"
pyinstaller_work="${build_root}/pyinstaller"
stage_root="${build_root}/pkg-root"
dist_dir="${project_root}/dist"

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Error: the macOS package must be built on macOS." >&2
    exit 1
fi

python_bin="${PYTHON:-python3}"
if ! command -v "${python_bin}" >/dev/null 2>&1; then
    echo "Error: ${python_bin} is not available." >&2
    exit 1
fi

if ! command -v pkgbuild >/dev/null 2>&1; then
    echo "Error: pkgbuild is not available. Install the macOS command-line tools." >&2
    exit 1
fi

version="$(PROJECT_ROOT="${project_root}" "${python_bin}" - <<'PY'
import os
from pathlib import Path
import tomllib

project_root = Path(os.environ["PROJECT_ROOT"])
with (project_root / "pyproject.toml").open("rb") as handle:
    print(tomllib.load(handle)["project"]["version"])
PY
)"

architecture="$(uname -m)"
package_name="ClannEolas-${version}-macos-${architecture}.pkg"

rm -rf "${build_root}"
mkdir -p "${build_root}" "${dist_dir}"

"${python_bin}" -m venv "${venv_dir}"
"${venv_dir}/bin/python" -m pip install --upgrade pip
"${venv_dir}/bin/python" -m pip install "${project_root}" "pyinstaller>=6,<7"

"${venv_dir}/bin/python" -m PyInstaller \
    --clean \
    --noconfirm \
    --distpath "${build_root}/dist" \
    --workpath "${pyinstaller_work}" \
    "${script_dir}/ClannEolas.spec"

mkdir -p "${stage_root}/usr/local/bin"
install -m 0755 "${build_root}/dist/eolas" "${stage_root}/usr/local/bin/eolas"

pkgbuild \
    --root "${stage_root}" \
    --identifier "com.clanneolas.cli" \
    --version "${version}" \
    --install-location "/" \
    "${dist_dir}/${package_name}"

checksum="$(shasum -a 256 "${dist_dir}/${package_name}" | awk '{print $1}')"

cat <<EOF
macOS verification package created:
  ${dist_dir}/${package_name}
  SHA-256: ${checksum}

This package is unsigned and intended for verification testing only.
It installs the self-contained 'eolas' command at /usr/local/bin/eolas.
EOF
