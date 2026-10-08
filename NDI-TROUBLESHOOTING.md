# Troubleshooting NDI no macOS

## Diagnóstico rápido

Execute o script de diagnóstico no seu Mac:

```bash
bash ndi-diagnostico-macos.sh
```

O script verifica automaticamente: processos NDI, instalação, rede, firewall, Bonjour e portas.

---

## Causas mais comuns e soluções

### 1. NDI Tools não instalado
Baixe e instale em: **https://ndi.video/tools/**

Instale o pacote completo (inclui NDI Video Monitor, Studio Monitor, Screen Capture).

---

### 2. Firewall bloqueando o NDI

**Ajustes do Sistema → Rede → Firewall → Opções do Firewall**

- Adicione todos os apps NDI (NDI Video Monitor, Studio Monitor, etc.)
- Selecione **"Permitir conexões de entrada"** para cada um
- Desative **"Ativar modo furtivo"** se estiver ligado

---

### 3. Permissão de Rede Local (macOS Ventura / Sonoma)

**Ajustes do Sistema → Privacidade e Segurança → Rede Local**

Ative a permissão para todos os apps NDI listados.

> Sem essa permissão, os apps não conseguem descobrir fontes na rede.

---

### 4. VPN ativa

VPNs geralmente bloqueiam tráfego multicast, impedindo a descoberta NDI.

- Desative a VPN temporariamente e teste
- Se funcionar sem VPN, configure o cliente VPN para excluir tráfego local (split tunnel)

---

### 5. Dispositivos em sub-redes diferentes

NDI usa multicast para descoberta. Todos os dispositivos devem estar na **mesma sub-rede** (ex.: todos com IP `192.168.1.x`).

Verifique os IPs:
```bash
ifconfig | grep "inet "
```

---

### 6. Roteador sem suporte a multicast

Se tiver vários switches ou um roteador gerenciado:

- Ative **IGMP Snooping** e/ou **IGMP Proxy** no roteador
- Verifique se há isolamento de clientes Wi-Fi ativado (bloqueia comunicação entre dispositivos)

---

### 7. mDNSResponder parado

```bash
# Verificar se está rodando
pgrep mDNSResponder

# Reiniciar se necessário
sudo killall -HUP mDNSResponder
```

---

### 8. Reinstalar / redefinir NDI

```bash
# Encerrar todos os processos NDI
pkill -f NDI 2>/dev/null || true
pkill -f NewTek 2>/dev/null || true

# Limpar caches
rm -rf ~/Library/Caches/com.newtek.*
rm -rf ~/Library/Caches/NDI*

# Reinstale o NDI Tools após isso
```

---

## Verificações rápidas no terminal

```bash
# Processos NDI rodando?
pgrep -lif ndi

# Portas NDI abertas?
lsof -i TCP:5960-5961

# Fontes NDI na rede (aguarda 5s)?
dns-sd -B _ndi._tcp local.

# Firewall ativo?
defaults read /Library/Preferences/com.apple.alf globalstate
# 0 = desativado, 1 = ativado, 2 = stealth (problemático)
```

---

## Logs úteis

Abra o **Console.app** e filtre por:
- `NDI`
- `NewTek`
- `mDNSResponder`

---

## Versões testadas

Guia válido para macOS 12 (Monterey), 13 (Ventura) e 14 (Sonoma).
