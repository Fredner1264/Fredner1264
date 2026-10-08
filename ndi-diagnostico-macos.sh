#!/usr/bin/env bash
# Script de diagnóstico NDI para macOS
# Execute com: bash ndi-diagnostico-macos.sh

set -euo pipefail

VERMELHO='\033[0;31m'
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
AZUL='\033[0;34m'
RESET='\033[0m'

ok()   { echo -e "  ${VERDE}✓${RESET} $*"; }
fail() { echo -e "  ${VERMELHO}✗${RESET} $*"; }
info() { echo -e "  ${AMARELO}→${RESET} $*"; }
sec()  { echo -e "\n${AZUL}▶ $*${RESET}"; }

echo "======================================================"
echo "   Diagnóstico NDI — macOS"
echo "   $(date)"
echo "======================================================"

# ── 1. Sistema ────────────────────────────────────────────
sec "Sistema"
SW=$(sw_vers -productVersion)
info "macOS $SW  ($(uname -m))"

# ── 2. Processos NDI ─────────────────────────────────────
sec "Processos NDI em execução"
NDI_PROCS=$(pgrep -lif "ndi" 2>/dev/null || true)
if [ -n "$NDI_PROCS" ]; then
  ok "Processos encontrados:"
  echo "$NDI_PROCS" | while read -r line; do echo "      $line"; done
else
  fail "Nenhum processo NDI encontrado — o software NDI pode não estar iniciado"
fi

# ── 3. Ferramentas NDI instaladas ────────────────────────
sec "Ferramentas / Apps NDI instalados"
NDI_PATHS=(
  "/Applications/NDI Tools.app"
  "/Applications/NDI Video Monitor.app"
  "/Applications/NDI Studio Monitor.app"
  "/Applications/NDI Screen Capture.app"
  "/Library/NDI"
  "/usr/local/lib/libndi.dylib"
  "$HOME/Library/Application Support/NewTek"
)
FOUND_ANY=0
for P in "${NDI_PATHS[@]}"; do
  if [ -e "$P" ]; then
    ok "Encontrado: $P"
    FOUND_ANY=1
  fi
done
[ $FOUND_ANY -eq 0 ] && fail "Nenhuma instalação NDI detectada em locais padrão"

# ── 4. Rede ───────────────────────────────────────────────
sec "Interfaces de rede ativas"
networksetup -listallhardwareports 2>/dev/null | grep -E "Hardware Port|Device|Ethernet Address" | \
  while IFS= read -r line; do info "$line"; done

echo ""
info "Endereços IP:"
ifconfig | grep -E "^[a-z]|inet " | grep -v "127.0.0.1\|::1" | \
  while IFS= read -r line; do
    [[ "$line" =~ ^[a-z] ]] && echo "  --- $line" || info "  $line"
  done

# Multicast — NDI usa mDNS/multicast
sec "Suporte a Multicast (necessário para NDI)"
if route -n get 224.0.0.0 &>/dev/null 2>&1; then
  ok "Rota multicast presente"
else
  fail "Nenhuma rota multicast — NDI pode não descobrir fontes"
  info "Verifique se seu roteador/switch suporta multicast (IGMP)"
fi

# ── 5. Portas NDI ─────────────────────────────────────────
sec "Portas usadas pelo NDI (5960 e 5961 são as principais)"
NDI_PORTS=(5960 5961)
for PORT in "${NDI_PORTS[@]}"; do
  LISTEN=$(lsof -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)
  if [ -n "$LISTEN" ]; then
    ok "Porta $PORT: em escuta"
    echo "$LISTEN" | tail -n +2 | while read -r line; do echo "      $line"; done
  else
    info "Porta $PORT: não está em escuta"
  fi
done

# Portas UDP/TCP usadas por processos NDI
sec "Conexões ativas de processos NDI"
NDI_CONNS=$(lsof -i -n -P 2>/dev/null | grep -i "ndi" || true)
if [ -n "$NDI_CONNS" ]; then
  ok "Conexões encontradas:"
  echo "$NDI_CONNS" | while read -r line; do echo "      $line"; done
else
  info "Nenhuma conexão de rede NDI ativa no momento"
fi

# ── 6. Firewall ───────────────────────────────────────────
sec "Firewall do macOS"
FW_STATE=$(defaults read /Library/Preferences/com.apple.alf globalstate 2>/dev/null || echo "desconhecido")
case "$FW_STATE" in
  0) ok "Firewall DESATIVADO (NDI pode funcionar sem bloqueio)" ;;
  1) info "Firewall ATIVADO — verifique se apps NDI estão na lista de exceções" ;;
  2) fail "Firewall em modo STEALTH — pode bloquear descoberta NDI" ;;
  *) info "Estado do firewall: $FW_STATE" ;;
esac

# Verificar exceções de apps NDI no firewall
if plutil -convert json -o - /Library/Preferences/com.apple.alf.plist 2>/dev/null | \
   python3 -c "import json,sys; d=json.load(sys.stdin); apps=[a.get('bundleid','') for a in d.get('exceptions',{}).get('exceptions',[])];\
   ndi=[a for a in apps if 'ndi' in a.lower() or 'newtek' in a.lower()]; \
   print('\n'.join(ndi) if ndi else '')" 2>/dev/null | grep -qi "ndi\|newtek"; then
  ok "Apps NDI/NewTek encontrados nas exceções do Firewall"
else
  info "Apps NDI não detectados nas exceções do Firewall (pode precisar adicionar)"
fi

# ── 7. Permissões de Rede (macOS 14+) ────────────────────
sec "Permissões de Rede Local (macOS Sonoma/Ventura)"
info "Verifique em: Ajustes do Sistema → Privacidade e Segurança → Rede Local"
info "Apps NDI precisam de permissão de Rede Local para descobrir fontes"

# ── 8. DNS-SD / Bonjour (descoberta NDI) ─────────────────
sec "Serviço Bonjour / mDNS (necessário para descoberta NDI)"
if pgrep -x "mDNSResponder" &>/dev/null; then
  ok "mDNSResponder em execução"
else
  fail "mDNSResponder NÃO está em execução — a descoberta NDI vai falhar"
  info "Execute: sudo launchctl start com.apple.mDNSResponder"
fi

# Buscar serviços NDI via Bonjour
info "Buscando fontes NDI na rede local (aguarde 5 segundos)..."
DNS_RESULT=$(dns-sd -B _ndi._tcp local. 2>&1 &
  DNS_PID=$!
  sleep 5
  kill $DNS_PID 2>/dev/null
  wait $DNS_PID 2>/dev/null
  true)
if echo "$DNS_RESULT" | grep -qi "ndi\|newtek"; then
  ok "Fontes NDI detectadas via Bonjour:"
  echo "$DNS_RESULT" | grep -i "ndi\|newtek" | while read -r line; do echo "      $line"; done
else
  info "Nenhuma fonte NDI encontrada via Bonjour no momento"
fi

# ── 9. Resumo e próximos passos ───────────────────────────
sec "Próximos passos sugeridos"
cat <<'STEPS'
  1. Se NDI Tools não está instalado:
     → Baixe em: https://ndi.video/tools/

  2. Se o Firewall estiver ativo:
     → Ajustes do Sistema → Rede → Firewall → Opções
     → Adicione os apps NDI e permita conexões de entrada

  3. Se estiver no macOS 14+ (Sonoma):
     → Ajustes do Sistema → Privacidade e Segurança → Rede Local
     → Ative todos os apps NDI

  4. Se as fontes NDI não aparecem:
     → Confirme que todos os dispositivos estão na MESMA sub-rede
     → Desative VPNs temporariamente (VPNs bloqueiam multicast)
     → Verifique se o roteador tem IGMP Snooping/Proxy ativado

  5. Se o NDI Tools trava:
     → Reinicie o serviço: pkill -f "NDI" && abra o app novamente
     → Verifique Console.app por erros relacionados a NDI

  6. Para logs detalhados em apps NDI:
     → Abra Console.app e filtre por "NDI" ou "NewTek"
STEPS

echo ""
echo "======================================================"
echo "   Diagnóstico concluído"
echo "======================================================"
