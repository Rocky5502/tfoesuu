#!/usr/bin/env bash
set -euo pipefail

expected_sha="${1:?expected TFOESUU commit required}"
bundle="${2:-/mnt/c/Users/Administrator/tfoesuu_fairlearn_v2.bundle}"
upstream_bundle="${3:-}"
repo="/home/zbq/work/tfoesuu-fairlearn-v2-${expected_sha:0:7}"
upstream="/home/zbq/work/fairlearn-v2-upstream-${expected_sha:0:7}"
old_tree="/home/zbq/work/fairlearn-old-e8cc637-${expected_sha:0:7}"
new_tree="/home/zbq/work/fairlearn-new-0cf59ec-${expected_sha:0:7}"
results="/mnt/d/Rocky Work/TFOESUU/results/fairlearn_v2_pc2_${expected_sha:0:7}"
image="tfoesuu-fairlearn-v2:${expected_sha:0:7}"
uv_root="/home/zbq/work/tools/uv-0.12.20"
runtime="/home/zbq/work/fairlearn-runtime-${expected_sha:0:7}"

for target in "$repo" "$upstream" "$old_tree" "$new_tree" "$results"; do
  [[ ! -e "$target" ]] || {
    echo "refusing to overwrite $target" >&2
    exit 2
  }
done
[[ -f "$bundle" ]] || { echo "missing bundle $bundle" >&2; exit 2; }
command -v git >/dev/null || { echo "git is unavailable on PC2 WSL" >&2; exit 3; }

git clone "$bundle" "$repo"
git -C "$repo" checkout --detach "$expected_sha"
[[ "$(git -C "$repo" rev-parse HEAD)" == "$expected_sha" ]]
[[ -z "$(git -C "$repo" status --porcelain)" ]]

if [[ -n "$upstream_bundle" ]]; then
  [[ -f "$upstream_bundle" ]] || {
    echo "missing upstream bundle $upstream_bundle" >&2
    exit 2
  }
  git clone "$upstream_bundle" "$upstream"
else
  git clone --filter=blob:none https://github.com/fairlearn/fairlearn.git "$upstream"
fi
git -C "$upstream" config core.autocrlf true
git -C "$upstream" worktree add --detach "$old_tree" \
  e8cc63784de5410805c156715175fc60e2cd5653
git -C "$upstream" worktree add --detach "$new_tree" \
  0cf59eccfdd364417787fe2c368a1c77c3f378b8

audit_python="python3"
if [[ -x /home/zbq/work/tfoesuu/.venv/bin/python ]]; then
  audit_python="/home/zbq/work/tfoesuu/.venv/bin/python"
fi
PYTHONPATH="$repo/src" "$audit_python" "$repo/scripts/audit_fairlearn_evolving_pair.py" \
  "$old_tree" "$new_tree" --require source >/tmp/fairlearn_v2_source_audit.json

mkdir -p "$results"
mv /tmp/fairlearn_v2_source_audit.json "$results/source-audit.json"
if command -v docker >/dev/null; then
  docker build --pull=false -t "$image" "$repo/external_subjects/fairlearn_v2"
  docker run --rm --mount "type=bind,source=$old_tree,target=/subject,readonly" \
    --mount "type=bind,source=$repo/external_subjects/fairlearn_v2,target=/probe,readonly" \
    "$image" python /probe/probe.py --version old --checkout /subject >"$results/old.json"
  docker run --rm --mount "type=bind,source=$new_tree,target=/subject,readonly" \
    --mount "type=bind,source=$repo/external_subjects/fairlearn_v2,target=/probe,readonly" \
    "$image" python /probe/probe.py --version new --checkout /subject >"$results/new.json"
  docker image inspect "$image" >"$results/image-inspect.json"
  docker run --rm "$image" python -m pip freeze >"$results/pip-freeze.txt"
else
  command -v curl >/dev/null || { echo "curl is unavailable on PC2 WSL" >&2; exit 3; }
  [[ ! -e "$runtime" ]] || { echo "refusing to overwrite $runtime" >&2; exit 2; }
  if [[ ! -x "$uv_root/uv" ]]; then
    mkdir -p "$uv_root"
    curl --proto '=https' --tlsv1.2 -LsSf \
      https://releases.astral.sh/github/uv/releases/download/0.12.20/uv-installer.sh | \
      env UV_UNMANAGED_INSTALL="$uv_root" sh
  fi
  [[ "$($uv_root/uv --version)" == "uv 0.12.20"* ]]
  mkdir -p "$runtime"
  export UV_PYTHON_INSTALL_DIR="$runtime/python"
  "$uv_root/uv" python install 3.8.20
  "$uv_root/uv" venv --python 3.8.20 --python-preference only-managed "$runtime/venv"
  "$uv_root/uv" pip sync --python "$runtime/venv/bin/python" \
    "$repo/external_subjects/fairlearn_v2/requirements-lock.txt"
  "$runtime/venv/bin/python" "$repo/external_subjects/fairlearn_v2/probe.py" \
    --version old --checkout "$old_tree" >"$results/old.json"
  "$runtime/venv/bin/python" "$repo/external_subjects/fairlearn_v2/probe.py" \
    --version new --checkout "$new_tree" >"$results/new.json"
  {
    "$uv_root/uv" --version
    "$runtime/venv/bin/python" --version
    sha256sum "$uv_root/uv"
    uname -a
  } >"$results/runtime-manifest.txt"
  "$uv_root/uv" pip freeze --python "$runtime/venv/bin/python" >"$results/pip-freeze.txt"
fi
PYTHONPATH="$repo/src" "$audit_python" "$repo/scripts/validate_fairlearn_v2_results.py" \
  "$results/old.json" "$results/new.json" >"$results/validation.json"

sha256sum "$results"/* | sort
