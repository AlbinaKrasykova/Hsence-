#!/usr/bin/env bash
# Deploy Hsence to Render (needs GitHub + Render account)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Hsence → Render deploy ==="
echo ""

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Log in to GitHub (browser opens):"
  gh auth login --web --git-protocol https
fi

REPO_NAME="${1:-hsence}"
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Creating GitHub repo: $REPO_NAME"
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
else
  echo "Pushing to origin..."
  git push -u origin HEAD
fi

echo ""
echo "=== Next: Render (2 minutes) ==="
echo "1. Open: https://dashboard.render.com/select-repo?type=blueprint"
echo "2. Connect GitHub → pick repo: $REPO_NAME"
echo "3. Click Apply — Render reads render.yaml"
echo "4. Wait for deploy → copy your *.onrender.com URL"
echo ""
echo "Done. Share: https://YOUR-SERVICE.onrender.com"
