# Guia: Configurar Variáveis do WebChat no Kubernetes

**Feature**: 010-canvas-conversational-search
**Criado em**: January 22, 2026

## 📝 Objetivo

Configurar as variáveis de ambiente necessárias para o Canvas Conversational Search funcionar em produção no Kubernetes usando Secrets.

---

## 🏗️ Arquitetura do Deployment

O projeto usa:
- **Docker multi-stage build** para o frontend
- **Kubernetes Secrets** para variáveis sensíveis
- **Build-time environment variables** (Vite processa durante `npm run build`)
- **Repository**: `weni-ai/kubernetes-manifests` para manifestos K8s

### ⚠️ Importante: Variáveis VITE_* são Build-Time

As variáveis com prefixo `VITE_*` são processadas **durante o build do Docker** pelo Vite, não no runtime. Isso significa que precisam estar disponíveis como **build args** no `docker build`.

---

## 🚀 Configuração Passo a Passo

### 1. Atualizar Dockerfile (Build Args)

**Arquivo**: `frontend/docker/Dockerfile`

Adicione os build arguments antes do stage de build:

```dockerfile
# syntax = docker/dockerfile:1

# Weni Public Roadmap - Frontend

ARG NODE_VERSION="25"
ARG BASE_VERSION="alpine3.23"

# Build-time environment variables for Vite
ARG VITE_API_URL
ARG VITE_WEBCHAT_CHANNEL_UUID
ARG VITE_WEBCHAT_SOCKET_URL=https://websocket.weni.ai
ARG VITE_WEBCHAT_HOST=https://flows.weni.ai

# Build stage
FROM node:${NODE_VERSION}-${BASE_VERSION} AS build

WORKDIR /app

# Set environment variables for Vite build
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WEBCHAT_CHANNEL_UUID=${VITE_WEBCHAT_CHANNEL_UUID}
ENV VITE_WEBCHAT_SOCKET_URL=${VITE_WEBCHAT_SOCKET_URL}
ENV VITE_WEBCHAT_HOST=${VITE_WEBCHAT_HOST}

# ... resto do Dockerfile ...
```

### 2. Criar/Atualizar Secret do Kubernetes

**Repositório**: `weni-ai/kubernetes-manifests`

**Arquivo**: `secrets/weni-roadmap-frontend-secret.yaml` (ou similar)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: weni-roadmap-frontend-secret
  namespace: your-namespace
type: Opaque
stringData:
  # API Configuration
  VITE_API_URL: "https://roadmap-api.weni.ai"
  
  # WebChat Configuration (OBRIGATÓRIO para Canvas Search)
  VITE_WEBCHAT_CHANNEL_UUID: "a9687ddd-849c-44e2-8f81-da9a07de21b8"
  
  # WebChat Optional (pode usar defaults)
  VITE_WEBCHAT_SOCKET_URL: "https://websocket.weni.ai"
  VITE_WEBCHAT_HOST: "https://flows.weni.ai"
```

**Aplicar Secret**:
```bash
kubectl apply -f secrets/weni-roadmap-frontend-secret.yaml
```

### 3. Atualizar Deployment/BuildConfig

**Opção A: GitHub Actions Workflow (Recomendado)**

Se estiver usando o workflow `.github/workflows/build-image-on-push-tag-to-shared-ecr.yaml`, as secrets devem ser passadas como **build args**:

**No repositório `weni-ai/kubernetes-manifests`**, no arquivo de configuração do ArgoCD ou similar:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  source:
    helm:
      parameters:
        - name: frontend.build.args.VITE_API_URL
          value: "https://roadmap-api.weni.ai"
        - name: frontend.build.args.VITE_WEBCHAT_CHANNEL_UUID
          value: "a9687ddd-849c-44e2-8f81-da9a07de21b8"
        - name: frontend.build.args.VITE_WEBCHAT_SOCKET_URL
          value: "https://websocket.weni.ai"
        - name: frontend.build.args.VITE_WEBCHAT_HOST
          value: "https://flows.weni.ai"
```

**Opção B: Docker Build Command**

Se estiver fazendo build manual:

```bash
docker build \
  --build-arg VITE_API_URL="https://roadmap-api.weni.ai" \
  --build-arg VITE_WEBCHAT_CHANNEL_UUID="a9687ddd-849c-44e2-8f81-da9a07de21b8" \
  --build-arg VITE_WEBCHAT_SOCKET_URL="https://websocket.weni.ai" \
  --build-arg VITE_WEBCHAT_HOST="https://flows.weni.ai" \
  -f frontend/docker/Dockerfile \
  -t weni-roadmap-frontend:latest \
  ./frontend
```

**Opção C: Deployment com EnvFrom (para runtime - NÃO funciona com VITE_*)**

⚠️ **ATENÇÃO**: Esta opção **NÃO funciona** para variáveis `VITE_*` porque elas precisam estar no build-time, não runtime.

```yaml
# ❌ Isso NÃO vai funcionar para VITE_*
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weni-roadmap-frontend
spec:
  template:
    spec:
      containers:
      - name: frontend
        envFrom:
        - secretRef:
            name: weni-roadmap-frontend-secret  # NÃO funciona para VITE_*!
```

### 4. Rebuild e Redeploy

Após configurar as build args/secrets:

```bash
# Tag a new version
git tag 1.0.0-staging
git push origin 1.0.0-staging

# O workflow build-image-on-push-tag-to-shared-ecr.yaml será acionado
# e fará o build com as variáveis corretas
```

---

## 🔍 Verificação

### 1. Verificar Secret Criado

```bash
kubectl get secret weni-roadmap-frontend-secret -n your-namespace
kubectl describe secret weni-roadmap-frontend-secret -n your-namespace
```

### 2. Verificar Build Args no Workflow

No GitHub Actions, verifique os logs do job `call-workflow-frontend`:

```
Building with arguments:
  --build-arg VITE_WEBCHAT_CHANNEL_UUID=a9687ddd-849c-44e2-8f81-da9a07de21b8
```

### 3. Verificar Variável no Bundle

Após o deploy, acesse o pod e verifique o bundle:

```bash
# Obter nome do pod
kubectl get pods -n your-namespace | grep weni-roadmap-frontend

# Acessar o pod
kubectl exec -it weni-roadmap-frontend-xxxxx -n your-namespace -- sh

# Verificar se a variável está no bundle JavaScript
cd /usr/share/nginx/html/assets
grep -r "WEBCHAT_CHANNEL_UUID" *.js

# Deve retornar o UUID embutido no código
```

### 4. Testar em Produção

1. Acesse o site em produção
2. Abra **DevTools** (F12) > **Console**
3. Clique no botão de **Canvas Search**
4. Verifique que **NÃO** aparece:
   ```
   ❌ WebChat channel UUID not configured
   ```

---

## 🛠️ Troubleshooting

### ❌ Erro: "WebChat channel UUID not configured"

**Causa**: A variável não foi passada como build arg durante o `docker build`.

**Soluções**:

1. **Verificar se o Dockerfile tem os ARGs**:
   ```dockerfile
   ARG VITE_WEBCHAT_CHANNEL_UUID
   ENV VITE_WEBCHAT_CHANNEL_UUID=${VITE_WEBCHAT_CHANNEL_UUID}
   ```

2. **Verificar se o GitHub Actions passa os build args**:
   - Edite o workflow ou o arquivo de configuração no `weni-ai/kubernetes-manifests`
   - Adicione os build args necessários

3. **Forçar rebuild da imagem**:
   ```bash
   # Criar nova tag para forçar rebuild
   git tag 1.0.1-staging
   git push origin 1.0.1-staging
   ```

4. **Verificar logs do build**:
   - No GitHub Actions, vá até o job `call-workflow-frontend`
   - Verifique a seção "Building Docker image"
   - Confirme que `--build-arg VITE_WEBCHAT_CHANNEL_UUID=...` está presente

### ❌ Variável aparece como "undefined" no bundle

**Causa**: A variável não estava disponível durante `npm run build`.

**Solução**:
1. Adicione `console.log` temporário antes do build:
   ```dockerfile
   RUN echo "VITE_WEBCHAT_CHANNEL_UUID=${VITE_WEBCHAT_CHANNEL_UUID}" && \
       npm run build
   ```
2. Verifique os logs do build para confirmar o valor
3. Se estiver vazio, o problema está na passagem do build arg

### ❌ Secret não está disponível no pod

**Causa**: Secret não foi aplicado ou está no namespace errado.

**Solução**:
```bash
# Verificar secrets no namespace
kubectl get secrets -n your-namespace

# Aplicar secret manualmente
kubectl apply -f secrets/weni-roadmap-frontend-secret.yaml

# Verificar se secret foi criado corretamente
kubectl get secret weni-roadmap-frontend-secret -n your-namespace -o yaml
```

---

## 🔐 Boas Práticas de Segurança

### ✅ DO (Faça)

- Use Kubernetes Secrets para armazenar o Channel UUID
- Rotacione o Channel UUID periodicamente
- Use diferentes UUIDs para ambientes diferentes (dev/staging/prod)
- Documente onde encontrar o UUID no Weni Platform
- Configure RBAC para limitar acesso aos secrets

### ❌ DON'T (Não Faça)

- **NÃO** commite o UUID diretamente no código
- **NÃO** use o mesmo UUID em todos os ambientes
- **NÃO** compartilhe o UUID em canais inseguros (Slack, email)
- **NÃO** exponha a secret do Kubernetes publicamente
- **NÃO** use secrets de produção em ambientes de desenvolvimento

---

## 📋 Diferença: Build-Time vs Runtime

### Build-Time Variables (VITE_*)

```
┌──────────────┐
│  docker build│  ← Variáveis VITE_* são lidas AQUI
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  npm run     │  ← Vite processa e embute as variáveis
│  build       │     no bundle JavaScript
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  dist/       │  ← Variáveis EMBUTIDAS no código
│  bundle.js   │     (não podem ser mudadas depois)
└──────────────┘
```

**Como passar**:
- ✅ `--build-arg VITE_WEBCHAT_CHANNEL_UUID=...`
- ❌ `envFrom: secretRef` (não funciona!)

### Runtime Variables (Sem VITE_*)

```
┌──────────────┐
│  docker run  │  ← Variáveis lidas aqui
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  entrypoint  │  ← envsubst substitui no HTML
│  envsubst    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  index.html  │  ← Variáveis injetadas em runtime
└──────────────┘
```

**Como passar**:
- ✅ `envFrom: secretRef`
- ✅ `env: [{ name: ..., valueFrom: secretKeyRef }]`

---

## 📚 Referências

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Docker Build Args](https://docs.docker.com/build/guide/build-args/)
- [Weni AI Actions Workflows](https://github.com/weni-ai/actions-workflows)

---

## 🎯 Checklist de Deploy

Antes de fazer deploy em produção:

- [ ] Dockerfile atualizado com ARGs `VITE_WEBCHAT_*`
- [ ] Secret do Kubernetes criado com UUID correto
- [ ] Build args configurados no workflow/ArgoCD
- [ ] Nova tag criada para acionar build
- [ ] Build logs verificados (build args presentes)
- [ ] Bundle verificado (UUID embutido no código)
- [ ] Canvas Search testado em produção
- [ ] Console do navegador sem erros
- [ ] Documentação atualizada no kubernetes-manifests

---

## 💡 Exemplo Completo - Dockerfile Atualizado

```dockerfile
# syntax = docker/dockerfile:1

# Weni Public Roadmap - Frontend

ARG NODE_VERSION="25"
ARG BASE_VERSION="alpine3.23"

# Build-time environment variables
ARG VITE_API_URL
ARG VITE_WEBCHAT_CHANNEL_UUID
ARG VITE_WEBCHAT_SOCKET_URL=https://websocket.weni.ai
ARG VITE_WEBCHAT_HOST=https://flows.weni.ai

# Build stage
FROM node:${NODE_VERSION}-${BASE_VERSION} AS build

WORKDIR /app

# Set environment variables for Vite
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WEBCHAT_CHANNEL_UUID=${VITE_WEBCHAT_CHANNEL_UUID}
ENV VITE_WEBCHAT_SOCKET_URL=${VITE_WEBCHAT_SOCKET_URL}
ENV VITE_WEBCHAT_HOST=${VITE_WEBCHAT_HOST}

# Install dependencies
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
  apk add git \
  && npm clean-install

# Copy source and build
COPY . .
RUN --mount=type=cache,target=/root/.npm \
  echo "Building with VITE_WEBCHAT_CHANNEL_UUID=${VITE_WEBCHAT_CHANNEL_UUID}" && \
  npm run build \
  && touch /headers \
  && chmod +r /headers \
  && chmod -wx /headers

# Production stage
FROM nginxinc/nginx-unprivileged:1-alpine

COPY --chown=nginx:nginx docker/nginx.conf /etc/nginx/nginx.conf
COPY --from=build --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY --from=build --chown=nginx:nginx /headers /usr/share/nginx/html/
COPY docker/entrypoint.sh /

USER root:root

RUN mv /usr/share/nginx/html/index.html /usr/share/nginx/html/index.html.tmpl \
  && cd /usr/share/nginx/html/ \
  && ln -s /tmp/index.html

USER nginx:nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:8080 || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
```

---

**Precisa de ajuda com algum passo específico? Entre em contato com o time de DevOps!** 🚀
