# Docker Configuration - Weni Roadmap Frontend

## 📋 Resumo das Alterações

Este diretório contém a configuração Docker completa para o frontend da aplicação Weni Roadmap, com suporte a todas as variáveis de ambiente VITE_ necessárias.

### ✅ Variáveis Configuradas

Todas as seguintes variáveis estão agora corretamente declaradas no Dockerfile:

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `VITE_API_URL` | URL da API backend | ✅ |
| `VITE_WEBCHAT_SOCKET_URL` | URL do WebSocket | ✅ |
| `VITE_WEBCHAT_HOST` | Host do WebChat | ✅ |
| `VITE_WEBCHAT_CHANNEL_UUID` | UUID do canal | ✅ |
| `VITE_VOICE_MODE_ENABLED` | Habilitar modo de voz | ✅ |
| `VITE_ELEVENLABS_API_KEY` | API Key do ElevenLabs | ✅* |
| `VITE_ELEVENLABS_VOICE_ID` | ID da voz | ✅* |
| `VITE_VOICE_MODE_LANGUAGE_CODE` | Código do idioma | ⬜ |

\* Obrigatório se `VITE_VOICE_MODE_ENABLED=true`

## 🔧 Arquivos

### Principais

- **`Dockerfile`** - Configuração principal com todos os ARGs e ENVs
- **`entrypoint.sh`** - Script de inicialização do container
- **`nginx.conf`** - Configuração do servidor Nginx

### Documentação

- **`BUILD_ARGS_GUIDE.md`** - Guia completo sobre como passar variáveis no build
- **`KUBERNETES_SECRET_CONFIG.md`** - Como configurar o webapp-secret no K8s
- **`README.md`** - Este arquivo

### Scripts

- **`build-test.sh`** - Script para testar o build localmente

## 🚀 Quick Start

### Build Local

```bash
cd frontend

# Opção 1: Usando o script (recomendado)
./docker/build-test.sh

# Opção 2: Manual
docker build \
  --build-arg VITE_API_URL="/api/v1" \
  --build-arg VITE_WEBCHAT_SOCKET_URL="https://websocket.weni.ai" \
  --build-arg VITE_WEBCHAT_HOST="https://flows.weni.ai" \
  --build-arg VITE_WEBCHAT_CHANNEL_UUID="your-uuid" \
  --build-arg VITE_VOICE_MODE_ENABLED="true" \
  --build-arg VITE_ELEVENLABS_API_KEY="sk_your_key" \
  --build-arg VITE_ELEVENLABS_VOICE_ID="your-voice-id" \
  -f docker/Dockerfile \
  -t weni-roadmap-frontend:latest \
  .
```

### Executar o Container

```bash
docker run -p 8080:8080 weni-roadmap-frontend:latest
```

Acesse: http://localhost:8080

## 🔍 Debug e Verificação

### Ver variáveis recebidas no build

Os logs do build mostrarão:

```
=== Build Arguments Received ===
VITE_API_URL: /api/v1
VITE_WEBCHAT_SOCKET_URL: https://websocket.weni.ai
VITE_WEBCHAT_HOST: https://flows.weni.ai
VITE_WEBCHAT_CHANNEL_UUID: <set>
VITE_VOICE_MODE_ENABLED: true
VITE_ELEVENLABS_API_KEY: <set>
VITE_ELEVENLABS_VOICE_ID: IrjWdL4OFv83a0lTXEQg
VITE_VOICE_MODE_LANGUAGE_CODE: <not set>
===============================
```

### Verificar se as variáveis foram embutidas no bundle

```
=== Checking if env vars are embedded in bundle ===
dist/assets/index-abc123.js:1:WEBCHAT_CHANNEL_UUID
dist/assets/index-abc123.js:1:ELEVENLABS
===============================
```

### Inspecionar o container em execução

```bash
# Listar arquivos
docker run --rm weni-roadmap-frontend:latest ls -la /usr/share/nginx/html/

# Ver variáveis de ambiente
docker run --rm weni-roadmap-frontend:latest env | grep VITE
```

## 🐛 Troubleshooting

### Problema: Variáveis não estão sendo reconhecidas

**Causa:** Build args não estão sendo passados corretamente

**Solução:**
1. Verifique se está usando `--build-arg` no comando docker build
2. Para CI/CD, verifique o webapp-secret no Kubernetes
3. Veja os logs de debug durante o build

📖 Leia: [BUILD_ARGS_GUIDE.md](./BUILD_ARGS_GUIDE.md)

### Problema: Secret do Kubernetes não funciona

**Causa:** webapp-secret não existe ou tem valores incorretos

**Solução:**
1. Verifique se o secret existe: `kubectl get secret webapp-secret -n <namespace>`
2. Verifique as chaves: `kubectl describe secret webapp-secret -n <namespace>`
3. Recrie o secret se necessário

📖 Leia: [KUBERNETES_SECRET_CONFIG.md](./KUBERNETES_SECRET_CONFIG.md)

### Problema: API Key aparece como "undefined"

**Causas possíveis:**
1. ❌ Variável não declarada no Dockerfile (ARG + ENV)
2. ❌ Typo no nome da variável
3. ❌ Variável não foi passada no build
4. ❌ Variável está vazia

**Como verificar:**
```bash
# 1. Ver logs do build
# Procure por "=== Build Arguments Received ==="

# 2. Verificar bundle
docker run --rm weni-roadmap-frontend:latest sh -c "grep -r 'ELEVENLABS_API_KEY' /usr/share/nginx/html/assets/*.js | head -1"

# 3. Testar no browser
# Abra o console e verifique: window.configs ou import.meta.env
```

## 📚 Documentação Completa

- **[BUILD_ARGS_GUIDE.md](./BUILD_ARGS_GUIDE.md)** - Guia detalhado sobre build arguments
  - Como o Vite processa env vars
  - Como passar variáveis via docker build
  - Como adicionar novas variáveis
  - Troubleshooting completo

- **[KUBERNETES_SECRET_CONFIG.md](./KUBERNETES_SECRET_CONFIG.md)** - Configuração do K8s
  - Como criar/atualizar o webapp-secret
  - Configuração por ambiente
  - Comandos kubectl úteis
  - Boas práticas de segurança

## 🎯 Mudanças Principais

### 1. Dockerfile Atualizado

**Antes:**
```dockerfile
ARG VITE_WEBCHAT_CHANNEL_UUID
ARG VITE_ELEVENLABS_API_KEY
ARG VITE_VOICE_MODE_ENABLED
```

**Depois:**
```dockerfile
# Todas as 8 variáveis VITE_ declaradas
ARG VITE_API_URL
ARG VITE_WEBCHAT_SOCKET_URL
ARG VITE_WEBCHAT_HOST
ARG VITE_WEBCHAT_CHANNEL_UUID
ARG VITE_VOICE_MODE_ENABLED
ARG VITE_ELEVENLABS_API_KEY
ARG VITE_ELEVENLABS_VOICE_ID  # ✨ NOVA
ARG VITE_VOICE_MODE_LANGUAGE_CODE  # ✨ NOVA
```

### 2. Debug Logging Adicionado

O Dockerfile agora mostra quais variáveis foram recebidas durante o build:

```dockerfile
RUN echo "=== Build Arguments Received ===" && \
    echo "VITE_API_URL: ${VITE_API_URL:-<not set>}" && \
    # ... todas as outras variáveis
```

### 3. Verificação do Bundle

Adicionada verificação se as variáveis foram embutidas:

```dockerfile
grep -r "ELEVENLABS" dist/assets/*.js || echo "WARNING: ELEVENLABS config not found!"
```

### 4. Centralização das Envs

Código refatorado para usar o módulo `src/utils/env.ts`:

**Antes:**
```typescript
const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
```

**Depois:**
```typescript
import { env } from '@/utils/env';
const apiUrl = env.apiUrl;
```

## 🔐 Segurança

### ⚠️ IMPORTANTE

- **NUNCA** commite valores de API keys no git
- Use secrets diferentes por ambiente (dev/staging/prod)
- Em produção, considere usar um proxy backend para API keys sensíveis
- Rotacione as chaves periodicamente

### Variáveis Sensíveis

- 🔴 **Muito sensível:** `VITE_ELEVENLABS_API_KEY`
- 🟡 **Sensível:** `VITE_WEBCHAT_CHANNEL_UUID`
- 🟢 **Público:** `VITE_ELEVENLABS_VOICE_ID`, `VITE_WEBCHAT_HOST`

## 📞 Suporte

Se tiver problemas:

1. ✅ Leia o [BUILD_ARGS_GUIDE.md](./BUILD_ARGS_GUIDE.md)
2. ✅ Leia o [KUBERNETES_SECRET_CONFIG.md](./KUBERNETES_SECRET_CONFIG.md)
3. ✅ Verifique os logs de debug do build
4. ✅ Teste localmente com `build-test.sh`

## 🔗 Links Úteis

- [Vite - Env Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Docker Build Args](https://docs.docker.com/engine/reference/builder/#arg)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [GitHub Actions Workflow](../../.github/workflows/build-image-on-push-tag-to-shared-ecr.yaml)

---

**Última atualização:** 2026-01-30
**Versão:** 1.0.0
