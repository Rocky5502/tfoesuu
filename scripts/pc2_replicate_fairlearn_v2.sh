#!/usr/bin/env bash
set -euo pipefail

expected_sha="${1:?expected TFOESUU commit required}"
bundle="${2:-/mnt/c/Users/Administrator/tfoesuu_fairlearn_v2.bundle}"
repo="/home/zbq/work/tfoesuu-fairlearn-v2-${expected_sha:0:7}"
upstream="/home/zbq/work/fairlearn-v2-upstream-${expected_sha:0:7}"
old_tree="/home/zbq/work/fairlearn-old-e8cc637-${expected_sha:0:7}"
new_tree="/home/zbq/work/fairlearn-new-0cf59ec-${expected_sha:0:7}"
results="/mnt/d/Rocky Work/TFOESUU/results/fairlearn_v2_pc2_${expected_sha:0:7}"
image="tfoesuu-fairlearn-v2:${expected_sha:0:7}"

for target in "$repo" "$upstream" "$old_tree" "$new_tree" "$results"; do
  [[ ! -e "$target" ]] || {
    echo "refusing to overwrite $target" >&2
    exit 2
  }
done
[[ -f "$bundle" ]] || { echo "missing bundle $bundle" >&2; exit 2; }
command -v git >/dev/null
command -v docker >/dev/null

git clone "$bundle" "$repo"
git -C "$repo" checkout --detach "$expected_sha"
[[ "$(git -C "$repo" rev-parse HEAD)" == "$expected_sha" ]]
[[ -z "$(git -C "$repo" status --porcelain)" ]]

git clone --filter=blob:none https://github.com/fairlearn/fairlearn.git "$upstream"
git -C "$upstream" config core.autocrlf true
git -C "$upstream" worktree add --detach "$old_tree" \
  e8cc63784de5410805c156715175fc60e2cd5653
git -C "$upstream" worktree add --detach "$new_tree" \
  0cf59eccfdd364417787fe2c368a1c77c3f378b8

PYTHONPATH="$repo/src" python3 "$repo/scripts/audit_fairlearn_evolving_pair.py" \
  "$old_tree" "$new_tree" --require source >/tmp/fairlearn_v2_source_audit.json

docker build --pull=false -t "$image" "$repo/external_subjects/fairlearn_v2"
docker run --rm --mount "type=bind,source=$old_tree,target=/subject,readonly" \
  "$image" python -c \
  "import sys; sys.path.insert(0,'/subject'); from fairlearn.postprocessing import ThresholdOptimizer; import inspect; print(inspect.signature(ThresholdOptimizer.predict))"
docker run --rm --mount "type=bind,source=$new_tree,target=/subject,readonly" \
  "$image" python -c \
  "import sys; sys.path.insert(0,'/subject'); from fairlearn.postprocessing import ThresholdOptimizer; import inspect; print(inspect.signature(ThresholdOptimizer.predict))"

mkdir -p "$results"
mv /tmp/fairlearn_v2_source_audit.json "$results/source-audit.json"
docker run --rm --mount "type=bind,source=$old_tree,target=/subject,readonly" \
  --mount "type=bind,source=$repo/external_subjects/fairlearn_v2,target=/probe,readonly" \
  "$image" python /probe/probe.py --version old --checkout /subject >"$results/old.json"
docker run --rm --mount "type=bind,source=$new_tree,target=/subject,readonly" \
  --mount "type=bind,source=$repo/external_subjects/fairlearn_v2,target=/probe,readonly" \
  "$image" python /probe/probe.py --version new --checkout /subject >"$results/new.json"
python3 "$repo/scripts/validate_fairlearn_v2_results.py" \
  "$results/old.json" "$results/new.json" >"$results/validation.json"
docker image inspect "$image" >"$results/image-inspect.json"
docker run --rm "$image" python -m pip freeze >"$results/pip-freeze.txt"

sha256sum "$results"/* | sort
