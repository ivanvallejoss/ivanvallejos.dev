#!/usr/bin/env bash
# smoke_test.sh — Verificación end-to-end de ivanvallejos.dev + blog
# Uso: ./scripts/smoke_test.sh [--local]
#   Sin flags: testea desde afuera (via Cloudflare), corrélo desde tu máquina.
#   --local:   agrega checks de puertos internos, corrélo desde la VPS.

set -u

PASS=0
FAIL=0

check() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$actual" == "$expected" ]]; then
        printf '  \033[32mOK\033[0m   %s\n' "$desc"
        ((PASS++))
    else
        printf '  \033[31mFAIL\033[0m %s (esperado: %s, obtuvo: %s)\n' "$desc" "$expected" "$actual"
        ((FAIL++))
    fi
}

status_of() { curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$1"; }
header_of() { curl -sI --max-time 10 "$1" | grep -i "^$2:" | tr -d '\r' | cut -d' ' -f2-; }

echo "== Landing =="
check "home responde 200"            "200" "$(status_of https://ivanvallejos.dev/)"
check "www redirige (301)"           "301" "$(status_of https://www.ivanvallejos.dev/)"
check "http redirige (301)"          "301" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://ivanvallejos.dev/)"
check "css principal 200"            "200" "$(status_of https://ivanvallejos.dev/static/landing/css/layout.css)"
check "css content-type"             "text/css" "$(header_of https://ivanvallejos.dev/static/landing/css/layout.css content-type)"
check "fuente woff2 200"             "200" "$(status_of https://ivanvallejos.dev/static/landing/fonts/Geist-Variable.woff2)"
check "cv.pdf 200"                   "200" "$(status_of https://ivanvallejos.dev/static/cv.ivanvallejos.pdf)"

echo "== Redirects /go/ =="
check "/go/blog es 302"              "302" "$(status_of https://ivanvallejos.dev/go/blog)"
check "/go/blog apunta al blog"      "https://blog.ivanvallejos.dev" "$(header_of https://ivanvallejos.dev/go/blog location)"
check "/go/github es 302"            "302" "$(status_of https://ivanvallejos.dev/go/github)"

echo "== Blog =="
check "blog home responde 200"       "200" "$(status_of https://blog.ivanvallejos.dev/)"
check "blog http redirige (301)"     "301" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://blog.ivanvallejos.dev/)"
# TODO: agregar un estático concreto del blog cuando definas uno estable, p.ej.:
# check "blog css 200" "200" "$(status_of https://blog.ivanvallejos.dev/static/css/blog.css)"

if [[ "${1:-}" == "--local" ]]; then
    echo "== Interno (VPS) =="
    check "gunicorn landing :8000"   "200" "$(status_of http://127.0.0.1:8000/)"
    check "gunicorn blog :8001"      "200" "$(status_of http://127.0.0.1:8001/)"
    check "landing.service activo"   "active" "$(systemctl is-active landing)"
    check "blog.service activo"      "active" "$(systemctl is-active blog)"
    check "landing enabled"          "enabled" "$(systemctl is-enabled landing)"
    check "blog enabled"             "enabled" "$(systemctl is-enabled blog)"
    check "postgres enabled"         "enabled" "$(systemctl is-enabled postgresql@18-main)"
fi

echo
echo "Resultado: $PASS OK, $FAIL FAIL"
[[ $FAIL -eq 0 ]]
