#!/usr/bin/env bash
# Exercises the golden path end to end: health -> profile -> matches (normal + surge) -> needs.
# Starts a local uvicorn server if one isn't already answering on $PORT, and stops it on exit.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR" || exit 1

PORT="${PORT:-8080}"
BASE_URL="http://127.0.0.1:${PORT}"
RESUME_FIXTURE="$ROOT_DIR/tests/fixtures/sample_resume.txt"
# Native Windows curl (mingw build) needs a Windows-style path for -F @path;
# a POSIX /c/... path from git-bash's pwd fails with "Failed to open/read local data".
if command -v cygpath > /dev/null 2>&1; then
  RESUME_FIXTURE="$(cygpath -w "$RESUME_FIXTURE")"
fi

STARTED_SERVER=0
SERVER_PID=""
FAILURES=0

fail() {
  echo "FAIL: $1"
  FAILURES=$((FAILURES + 1))
}

pass() {
  echo "PASS: $1"
}

cleanup() {
  if [ "$STARTED_SERVER" -eq 1 ] && [ -n "$SERVER_PID" ]; then
    echo "Stopping uvicorn (pid $SERVER_PID)..."
    kill "$SERVER_PID" 2>/dev/null
    wait "$SERVER_PID" 2>/dev/null
  fi
}
trap cleanup EXIT

echo "== Tenderly smoke test =="

if curl -sf "$BASE_URL/api/health" > /dev/null 2>&1; then
  echo "Server already running at $BASE_URL"
else
  echo "Starting uvicorn on port $PORT..."
  python -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" > "$ROOT_DIR/scripts/.smoke_server.log" 2>&1 &
  SERVER_PID=$!
  STARTED_SERVER=1

  READY=0
  for i in $(seq 1 30); do
    if curl -sf "$BASE_URL/api/health" > /dev/null 2>&1; then
      READY=1
      break
    fi
    sleep 1
  done

  if [ "$READY" -ne 1 ]; then
    fail "server did not become healthy within 30s"
    echo "--- server log ---"
    cat "$ROOT_DIR/scripts/.smoke_server.log" 2>/dev/null
    exit 1
  fi
fi

echo
echo "-- GET /api/health --"
HEALTH_BODY="$(curl -sf "$BASE_URL/api/health")"
if [ $? -eq 0 ] && echo "$HEALTH_BODY" | grep -q '"status"[[:space:]]*:[[:space:]]*"ok"'; then
  pass "health check"
else
  fail "health check (body: $HEALTH_BODY)"
fi

echo
echo "-- POST /api/profile --"
PROFILE_BODY="$(curl -sf -X POST "$BASE_URL/api/profile" \
  -F "file=@${RESUME_FIXTURE};type=text/plain" \
  -F "interests=food security,immigrant support,community safety" \
  -F "availability=weekday evenings")"

if [ $? -ne 0 ] || [ -z "$PROFILE_BODY" ]; then
  fail "profile creation returned no body"
  echo "$PROFILE_BODY"
  exit 1
fi

PROFILE_ID="$(python - "$PROFILE_BODY" <<'PYEOF'
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("profile_id", ""))
except Exception:
    print("")
PYEOF
)"

if [ -n "$PROFILE_ID" ]; then
  pass "profile creation (profile_id=$PROFILE_ID)"
else
  fail "profile creation did not return profile_id"
  echo "$PROFILE_BODY"
  exit 1
fi

echo "$PROFILE_BODY" | python -m json.tool 2>/dev/null || echo "$PROFILE_BODY"

echo
echo "-- GET /api/matches/{profile_id}?scenario=normal --"
NORMAL_BODY="$(curl -sf "$BASE_URL/api/matches/${PROFILE_ID}?scenario=normal")"
if [ $? -eq 0 ] && [ -n "$NORMAL_BODY" ]; then
  pass "normal matches request"
else
  fail "normal matches request"
fi

python - "$NORMAL_BODY" <<'PYEOF'
import json, sys
data = json.loads(sys.argv[1])
matches = data.get("matches", [])
print(f"scenario={data.get('scenario')} needs_summary={data.get('needs_summary')!r}")
print(f"match count={len(matches)}")
for i, m in enumerate(matches[:3]):
    print(f"  #{i+1} {m['org_name']} - {m['title']} score={m['score']} urgency={m['urgency']} why_you={'set' if m['why_you'] else 'MISSING'}")
for i, m in enumerate(matches[3:], start=4):
    if m.get("why_you") is not None:
        print(f"  WARNING: rank {i} should have why_you=null, got: {m['why_you']!r}")
PYEOF

echo
echo "-- GET /api/matches/{profile_id}?scenario=surge --"
SURGE_BODY="$(curl -sf "$BASE_URL/api/matches/${PROFILE_ID}?scenario=surge")"
if [ $? -eq 0 ] && [ -n "$SURGE_BODY" ]; then
  pass "surge matches request"
else
  fail "surge matches request"
fi

python - "$NORMAL_BODY" "$SURGE_BODY" <<'PYEOF'
import json, sys
normal = json.loads(sys.argv[1])
surge = json.loads(sys.argv[2])
normal_order = [m["opportunity_id"] for m in normal["matches"]]
surge_order = [m["opportunity_id"] for m in surge["matches"]]
print(f"normal top3: {normal_order[:3]}")
print(f"surge top3:  {surge_order[:3]}")
if normal_order != surge_order:
    print("OK: surge scenario visibly re-ranked opportunities")
else:
    print("NOTE: ranking identical between normal and surge for this profile (seed data variety may need widening)")
PYEOF

echo
echo "-- GET /api/needs --"
NEEDS_BODY="$(curl -sf "$BASE_URL/api/needs")"
if [ $? -eq 0 ] && [ -n "$NEEDS_BODY" ]; then
  pass "needs request"
else
  fail "needs request"
fi

python - "$NEEDS_BODY" <<'PYEOF'
import json, sys
data = json.loads(sys.argv[1])
print(f"updated_at={data.get('updated_at')}")
for n in data.get("neighborhoods", [])[:5]:
    print(f"  {n['name']}: {n['case_count']} cases, top_categories={n['top_categories']}")
PYEOF

echo
if [ "$FAILURES" -eq 0 ]; then
  echo "== ALL CHECKS PASSED =="
  exit 0
else
  echo "== $FAILURES CHECK(S) FAILED =="
  exit 1
fi
