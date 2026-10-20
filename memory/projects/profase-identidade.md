# ProFase — Identidade Visual Oficial

**Versão:** 1.0 · Outubro 2026
**Responsável:** Fredner Sales

---

## Marca

- **Nome no logotipo:** PROFASE (tudo maiúsculo, sem espaço)
- **Nome comercial:** ProFase
- **Segmento:** Consultoria e projeto de AV integrado (Áudio · Vídeo · Iluminação)
- **Localização:** São Paulo, SP
- **Tagline:** *A corrente viva do seu projeto*
- **Conceito de "FASE":** fase elétrica — o condutor vivo (fio fase), não "stage/phase"

---

## Paleta de Cores

```css
:root {
  --mg:   #FF007F;   /* Rosa — primário, distintivo, acento único */
  --cy:   #00E5FF;   /* Ciano — pilar Vídeo, gradiente */
  --bk:   #000000;   /* Preto puro — capas, fundos escuros */
  --wh:   #FFFFFF;   /* Branco — páginas de conteúdo */
  --fg:   #F5F5F7;   /* Off-white — texto sobre fundo preto */
  --tx:   #111111;   /* Preto suave — texto principal */
  --t2:   #555555;   /* Cinza — texto secundário */
  --bd:   #E4E4E4;   /* Borda / divisória */
  --bg:   #F7F7F7;   /* Fundo de linhas pares em tabelas */
  color-scheme: light; /* páginas de conteúdo */
}
```

### Três Pilares
| Pilar | Cor | Token |
|-------|-----|-------|
| Áudio | Rosa `#FF007F` | `--mg` (dominante) |
| Vídeo | Ciano `#00E5FF` | `--cy` |
| Iluminação | Branco `#F5F5F7` | `--fg` |

---

## Tipografia

| Uso | Família | Peso |
|-----|---------|------|
| Logo / Display | Outfit | 200 |
| Corpo / parágrafos | Outfit | 300 |
| Títulos de seção | Outfit | 600 |
| Labels / caps | Outfit | 600 + letter-spacing 0.22em |

**Import Google Fonts:**
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700&display=swap">
```

**Regras:**
- NUNCA substituir Outfit por outra família sem autorização explícita
- Wordmark: `font-size: clamp(52px, 13vw, 112px)`, `letter-spacing: 0.22em`

---

## Estilo Visual (Apple-minimalist)

### Estrutura de Página Padrão
- **Capa / cover:** fundo `#000000`, texto `#F5F5F7`
- **Páginas de conteúdo:** fundo `#FFFFFF`, texto `#111111`
- **Barra de rodapé:** `height: 3px; background: linear-gradient(90deg, #FF007F 0%, #00E5FF 100%)`
- **Acento único por página:** linha fina (1–3px) em `#FF007F` — UMA por seção

### Princípios
1. Espaço negativo generoso — padding mínimo 32px lateral (mobile), 52px (desktop)
2. Um único acento colorido por área — nunca dois simultâneos
3. Sem sombras decorativas pesadas
4. Sem animações em documentos para impressão
5. Clareza sobre decoração — nenhum elemento sem função

---

## Componentes Padrão (HTML/CSS)

### Logo mínimo
```html
<h1 style="font-family:'Outfit';font-weight:200;letter-spacing:0.22em;">PROFASE</h1>
<hr style="width:48px;height:1px;background:#FF007F;border:none;">
<p style="font-family:'Outfit';font-weight:300;font-size:10px;letter-spacing:0.30em;text-transform:uppercase;color:rgba(245,245,247,0.40);">
  Áudio &nbsp;·&nbsp; Vídeo &nbsp;·&nbsp; Iluminação
</p>
```

### Barra de rodapé
```html
<div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#FF007F,#00E5FF);"></div>
```

### Running header (documentos)
```html
<div style="display:flex;justify-content:space-between;padding-bottom:14px;border-bottom:1px solid #E4E4E4;">
  <span style="font-family:'Outfit';font-weight:300;letter-spacing:0.16em;">PRO<b style="color:#FF007F;font-weight:300;">FASE</b></span>
  <span style="font-family:'Outfit';font-weight:300;font-size:11px;color:#AAA;">Título do documento</span>
</div>
```

---

## Documentos Criados

| Documento | URL / Artifact |
|-----------|---------------|
| Logo (Apple-minimalista) | https://claude.ai/artifact/HEBuGVtKZdRrakwzbiDacn |
| Proposta Comercial (template) | https://claude.ai/artifact/7pD8TJGbJQWVHoJkPU3mX2 |
| Estratégia de cor (Ehrenberg-Bass) | https://claude.ai/artifact/CeTo42i7FEedt9sUccmmqK |

---

## Instrução para Claude

**Todo documento ProFase** — proposta, relatório, apresentação, contrato, laudo — deve obrigatoriamente:
1. Usar `font-family: 'Outfit'` com os pesos definidos acima
2. Aplicar os tokens de cor desta folha (copiar o bloco `:root` acima)
3. Ter capa preta + páginas de conteúdo brancas
4. Ter barra de rodapé gradiente rosa → ciano
5. Usar `#FF007F` como único acento colorido em títulos e labels
6. Manter espaçamento generoso e ausência de gimmicks

Quando receber qualquer pedido de documento ProFase, carregar este arquivo antes de escrever uma linha de código.
