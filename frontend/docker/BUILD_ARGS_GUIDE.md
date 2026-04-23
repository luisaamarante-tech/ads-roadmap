# Docker Build Arguments Guide

Este documento explica como as variáveis de ambiente são gerenciadas no build do Docker para o frontend da aplicação.

## Como Funciona

### 1. Variáveis em Tempo de Build (Build Time)

O Vite incorpora as variáveis de ambiente **durante o build** (`npm run build`). Isso significa que:

- As variáveis precisam estar disponíveis como **ENV** durante o comando `npm run build`
- O Vite só expõe variáveis que começam com `VITE_` para o código cliente
- Os valores são embutidos no JavaScript compilado

### 2. Dockerfile - ARG e ENV

```dockerfile
# ARG - Recebe valores do comando docker build
ARG VITE_ELEVENLABS_API_KEY

# ENV - Disponibiliza a variável durante o build
ENV VITE_ELEVENLABS_API_KEY=${VITE_ELEVENLABS_API_KEY}
```

**Importante:** A ordem é:
1. `ARG` - declara que o Dockerfile aceita o argumento
2. `ENV` - torna a variável disponível para o processo de build

## Variáveis Disponíveis

Todas as variáveis VITE_ estão declaradas no Dockerfile:

- `VITE_API_URL` - URL da API backend
- `VITE_WEBCHAT_SOCKET_URL` - URL do WebSocket do WebChat
- `VITE_WEBCHAT_HOST` - Host do WebChat
- `VITE_WEBCHAT_CHANNEL_UUID` - UUID do canal do WebChat
- `VITE_VOICE_MODE_ENABLED` - Habilita/desabilita modo de voz (true/false)
- `VITE_ELEVENLABS_API_KEY` - API Key do ElevenLabs
- `VITE_ELEVENLABS_VOICE_ID` - ID da voz do ElevenLabs
- `VITE_VOICE_MODE_LANGUAGE_CODE` - Código de idioma para modo de voz (opcional)

## Como Passar as Variáveis

### Opção 1: Via --build-arg (Manual)

```bash
docker build \
  --build-arg VITE_API_URL="https://api.example.com" \
  --build-arg VITE_WEBCHAT_SOCKET_URL="https://websocket.weni.ai" \
  --build-arg VITE_WEBCHAT_HOST="https://flows.weni.ai" \
  --build-arg VITE_WEBCHAT_CHANNEL_UUID="your-uuid" \
  --build-arg VITE_VOICE_MODE_ENABLED="true" \
  --build-arg VITE_ELEVENLABS_API_KEY="sk_xxxxx" \
  --build-arg VITE_ELEVENLABS_VOICE_ID="voice-id-here" \
  --build-arg VITE_VOICE_MODE_LANGUAGE_CODE="pt" \
  -f docker/Dockerfile \
  -t weni-roadmap-frontend:latest \
  .
```

### Opção 2: Via Kubernetes Secret (CI/CD)

No GitHub Actions, o workflow usa `kludge_webapp_secret_enable: true`, que automaticamente:

1. Busca o secret `webapp-secret` do namespace
2. Converte cada chave do secret em `--build-arg`
3. Passa para o docker build

**Exemplo de webapp-secret.yaml:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: webapp-secret
  namespace: weni-roadmap
type: Opaque
stringData:
  VITE_API_URL: "https://api.weni.ai/api/v1"
  VITE_WEBCHAT_SOCKET_URL: "https://websocket.weni.ai"
  VITE_WEBCHAT_HOST: "https://flows.weni.ai"
  VITE_WEBCHAT_CHANNEL_UUID: "a9687ddd-849c-44e2-8f81-da9a07de21b8"
  VITE_VOICE_MODE_ENABLED: "true"
  VITE_ELEVENLABS_API_KEY: "sk_xxxxx"
  VITE_ELEVENLABS_VOICE_ID: "IrjWdL4OFv83a0lTXEQg"
  # VITE_VOICE_MODE_LANGUAGE_CODE: "pt"  # Opcional
```

## Verificando se Funcionou

### 1. Durante o Build

Adicione um echo no Dockerfile após as ENV declarations:

```dockerfile
RUN echo "VITE_ELEVENLABS_API_KEY=$VITE_ELEVENLABS_API_KEY" && \
    echo "VITE_VOICE_MODE_ENABLED=$VITE_VOICE_MODE_ENABLED" && \
    echo "VITE_ELEVENLABS_VOICE_ID=$VITE_ELEVENLABS_VOICE_ID"
```

### 2. No Bundle Final

O Dockerfile já inclui verificação:

```dockerfile
RUN npm run build && \
    echo "Verifying build artifacts..." && \
    ls -la dist/ && \
    grep -r "WEBCHAT_CHANNEL_UUID" dist/assets/*.js || echo "WARNING: UUID not found in bundle!"
```

Adicione mais verificações se necessário:

```dockerfile
grep -r "ELEVENLABS" dist/assets/*.js || echo "WARNING: ElevenLabs config not found!"
```

### 3. No Runtime (Browser)

No navegador, abra o console e verifique:

```javascript
// Verificar se o env.ts está retornando os valores corretos
import { env } from '@/utils/env';
console.log('Env config:', env);
```

## Troubleshooting

### Problema: Variáveis não aparecem no build

**Causa:** ARG não declarado ou ENV não definido no Dockerfile

**Solução:** Verifique se a variável está em ambas as seções:
```dockerfile
ARG VITE_NOVA_VARIAVEL
ENV VITE_NOVA_VARIAVEL=${VITE_NOVA_VARIAVEL}
```

### Problema: Variável está no Dockerfile mas não é reconhecida

**Causa:** Não está sendo passada no `docker build`

**Solução (Local):**
```bash
docker build --build-arg VITE_NOVA_VARIAVEL="valor" ...
```

**Solução (Kubernetes):**
Adicione a chave no secret `webapp-secret`

### Problema: Variável com valor "undefined" ou vazio

**Causa 1:** A variável foi passada mas está vazia
```bash
# Errado
docker build --build-arg VITE_API_URL="" ...

# Correto
docker build --build-arg VITE_API_URL="https://api.example.com" ...
```

**Causa 2:** Typo no nome da variável (não começa com VITE_)

**Causa 3:** No Kubernetes, o secret não existe ou a chave está errada

## Runtime Override (window.configs)

O sistema também suporta override em runtime via `window.configs`:

```html
<!-- index.html.tmpl -->
<script>
  window.configs = {
    VITE_API_URL: '${VITE_API_URL}',
    VITE_WEBCHAT_CHANNEL_UUID: '${VITE_WEBCHAT_CHANNEL_UUID}'
  };
</script>
```

Isso permite que o `entrypoint.sh` substitua valores usando `envsubst` sem precisar rebuildar a imagem.

**Prioridade de resolução no env.ts:**
1. `window.configs[name]` (runtime)
2. `import.meta.env[name]` (build time)

## Adicionando Nova Variável

1. Adicione no `.env`:
   ```bash
   VITE_NOVA_FEATURE="valor"
   ```

2. Adicione no `vite-env.d.ts`:
   ```typescript
   interface ImportMetaEnv {
     readonly VITE_NOVA_FEATURE?: string;
   }
   ```

3. Adicione no `src/utils/env.ts`:
   ```typescript
   export const env = {
     // ...
     novaFeature: getEnv('VITE_NOVA_FEATURE') || 'default',
   }
   ```

4. Adicione no `Dockerfile`:
   ```dockerfile
   ARG VITE_NOVA_FEATURE
   ENV VITE_NOVA_FEATURE=${VITE_NOVA_FEATURE}
   ```

5. Adicione no `webapp-secret` do Kubernetes (se aplicável)

6. Use no código:
   ```typescript
   import { env } from '@/utils/env';
   console.log(env.novaFeature);
   ```

## Referências

- [Vite - Env Variables and Modes](https://vitejs.dev/guide/env-and-mode.html)
- Projeto de referência: `chats-webapp` (mesmo padrão ARG→ENV)
