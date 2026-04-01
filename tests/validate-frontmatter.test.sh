#!/usr/bin/env bash
# Tests unitaires pour scripts/validate-frontmatter.sh
set -euo pipefail

VALIDATOR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/validate-frontmatter.sh"
PASS=0
FAIL=0

# Long enough description to satisfy the 100-char minimum
DESC="Cette description est suffisamment longue pour satisfaire l'exigence minimale de cent caractères pour la qualité SEO."

check() {
    local name="$1" expected="$2" dir="$3"
    local actual=0
    POSTS_DIR="$dir" bash "$VALIDATOR" >/dev/null 2>&1 || actual=$?
    if [[ "$actual" -eq "$expected" ]]; then
        echo "✅ $name"
        PASS=$((PASS + 1))
    else
        echo "❌ $name (expected exit $expected, got $actual)"
        FAIL=$((FAIL + 1))
    fi
}

make_post() {
    cat > "$1/post.md" <<EOF
---
title: "Titre valide pour le test unitaire"
slug: "titre-valide"
date: "2024-01-15"
description: "$DESC"
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
image: /images/og-default.svg
---
EOF
}

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# 1. Valid post passes
D="$TMP/t1"; mkdir "$D"; make_post "$D"
check "valid post passes" 0 "$D"

# 2. Invalid slug (uppercase) fails
D="$TMP/t2"; mkdir "$D"
cat > "$D/post.md" <<EOF
---
title: "Titre valide pour le test unitaire"
slug: "Invalid-Slug"
date: "2024-01-15"
description: "$DESC"
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
image: /images/og-default.svg
---
EOF
check "invalid slug (uppercase) fails" 1 "$D"

# 3. Title too short fails
D="$TMP/t3"; mkdir "$D"
cat > "$D/post.md" <<EOF
---
title: "Court"
slug: "court"
date: "2024-01-15"
description: "$DESC"
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
image: /images/og-default.svg
---
EOF
check "title too short fails" 1 "$D"

# 4. Description too short fails
D="$TMP/t4"; mkdir "$D"
cat > "$D/post.md" <<EOF
---
title: "Titre valide pour le test unitaire"
slug: "titre-valide"
date: "2024-01-15"
description: "Trop court."
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
image: /images/og-default.svg
---
EOF
check "description too short fails" 1 "$D"

# 5. Missing required field fails
D="$TMP/t5"; mkdir "$D"
cat > "$D/post.md" <<EOF
---
title: "Titre valide pour le test unitaire"
slug: "titre-valide"
date: "2024-01-15"
description: "$DESC"
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
---
EOF
check "missing image field fails" 1 "$D"

# 6. Invalid date format fails
D="$TMP/t6"; mkdir "$D"
cat > "$D/post.md" <<EOF
---
title: "Titre valide pour le test unitaire"
slug: "titre-valide"
date: "15/01/2024"
description: "$DESC"
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
image: /images/og-default.svg
---
EOF
check "invalid date format fails" 1 "$D"

# 7. Duplicate slugs fail
D="$TMP/t7"; mkdir "$D"
cat > "$D/post1.md" <<EOF
---
title: "Titre valide pour le test unitaire"
slug: "titre-valide"
date: "2024-01-15"
description: "$DESC"
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
image: /images/og-default.svg
---
EOF
cat > "$D/post2.md" <<EOF
---
title: "Autre titre valide pour le test unitaire"
slug: "titre-valide"
date: "2024-01-16"
description: "$DESC"
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
image: /images/og-default.svg
---
EOF
check "duplicate slugs fail" 1 "$D"

# 8. Relative image path fails
D="$TMP/t8"; mkdir "$D"
cat > "$D/post.md" <<EOF
---
title: "Titre valide pour le test unitaire"
slug: "titre-valide"
date: "2024-01-15"
description: "$DESC"
categories: ["data-engineering"]
tags: ["test"]
keywords: ["test"]
image: images/og-default.svg
---
EOF
check "relative image path fails" 1 "$D"

echo ""
echo "Résultats: $PASS réussis, $FAIL échoués"
[[ $FAIL -eq 0 ]] || exit 1
