#!/usr/bin/env bash
set -euo pipefail

ROOT="/dtu/blackhole/00/c27666"
PROTEIN_PY="$ROOT/miniforge3/envs/protein-design/bin/python"

if [[ ! -x "$PROTEIN_PY" ]]; then
  echo "Missing protein-design Python: $PROTEIN_PY" >&2
  exit 1
fi

"$PROTEIN_PY" -c 'import ipykernel, pandas, numpy, matplotlib, tmtools' 2>/dev/null || {
  echo "protein-design is missing one of: ipykernel, pandas, numpy, matplotlib, tmtools" >&2
  echo "Python checked: $PROTEIN_PY" >&2
  exit 1
}

install_kernel() {
  local data_dir="$1"
  local name="c27666-protein-design"
  local target="$data_dir/kernels/$name"

  mkdir -p "$target"
  rm -rf "$data_dir/kernels/c27666-base"
  cat >"$target/kernel.json" <<JSON
{
 "argv": [
  "$PROTEIN_PY",
  "-Xfrozen_modules=off",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "c27666 Protein Design",
 "language": "python",
 "metadata": {
  "debugger": true
 },
 "kernel_protocol_version": "5.5"
}
JSON
}

add_data_dir() {
  local dir="$1"
  [[ -n "$dir" ]] || return 0
  mkdir -p "$dir" 2>/dev/null && [[ -w "$dir" ]] || return 0
  for existing in "${DATA_DIRS[@]}"; do
    [[ "$existing" == "$dir" ]] && return 0
  done
  DATA_DIRS+=("$dir")
}

DATA_DIRS=()
add_data_dir "${HOME:?}/.local/share/jupyter"
if command -v jupyter >/dev/null 2>&1; then
  add_data_dir "$(jupyter --data-dir 2>/dev/null || true)"
fi
add_data_dir "$("$PROTEIN_PY" -m jupyter --data-dir 2>/dev/null || true)"

if [[ "${#DATA_DIRS[@]}" -eq 0 ]]; then
  echo "Could not find a writable Jupyter data directory for $(whoami)." >&2
  exit 1
fi

for data_dir in "${DATA_DIRS[@]}"; do
  install_kernel "$data_dir"
done

echo
echo "Registered c27666 Protein Design for $(whoami):"
for data_dir in "${DATA_DIRS[@]}"; do
  echo "  $data_dir/kernels/c27666-protein-design"
done

echo
echo "Visible to this shell's Jupyter:"
jupyter kernelspec list 2>/dev/null || "$PROTEIN_PY" -m jupyter kernelspec list

echo
echo "Notebook sanity check command:"
echo '  import sys; print(sys.executable)'
