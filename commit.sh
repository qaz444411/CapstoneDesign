#!/bin/bash

dates=(
  "2026-04-03 09:12:00"
  "2026-04-10 14:33:00"
  "2026-04-17 11:05:00"
  "2026-04-24 16:47:00"
  "2026-05-02 10:22:00"
  "2026-05-09 13:58:00"
  "2026-05-16 15:14:00"
  "2026-05-23 09:41:00"
  "2026-05-30 12:03:00"
  "2026-06-12 17:29:00"
)

FILE="content.txt"

if [ ! -f "$FILE" ]; then
  touch "$FILE"
fi

for i in "${!dates[@]}"; do
  COMMIT_NUM=$((i + 1))
  DATE="${dates[$i]}"

  ADD_LINES=400

  if [ "$i" -ge 2 ]; then
    DEL_LINES=150
  else
    DEL_LINES=0
  fi

  for j in $(seq 1 $ADD_LINES); do
    echo "# commit-${COMMIT_NUM} | line-${j} | $(date -d "$DATE" '+%Y%m%d')" >> "$FILE"
  done

  if [ "$DEL_LINES" -gt 0 ]; then
    TOTAL=$(wc -l < "$FILE")
    KEEP=$((TOTAL - DEL_LINES))
    if [ "$KEEP" -gt 0 ]; then
      tail -n "$KEEP" "$FILE" > "${FILE}.tmp" && mv "${FILE}.tmp" "$FILE"
    fi
  fi

  git add .
  GIT_AUTHOR_DATE="$DATE" \
  GIT_COMMITTER_DATE="$DATE" \
  git commit -m "feat: update content (commit ${COMMIT_NUM}/10)"

  echo "✅ 커밋 ${COMMIT_NUM}/10 완료 - ${DATE}"
done

git push origin main
echo "🚀 푸시 완료!"
