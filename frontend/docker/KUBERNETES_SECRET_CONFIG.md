# Configuração do webapp-secret no Kubernetes

Este documento explica como configurar o secret `webapp-secret` no Kubernetes para passar as variáveis de ambiente para o build do Docker no CI/CD.

## Como Funciona

O workflow do GitHub Actions (`build-image-on-push-tag-to-shared-ecr.yaml`) usa a opção:

```yaml
kludge_webapp_secret_enable: true
```

Isso faz com que o workflow reutilizável:

1. Busque o secret `webapp-secret` do namespace correspondente
2. Converta cada chave do secret em `--build-arg` para o docker build
3. Passe todos os valores para o build da imagem

## Criando/Atualizando o Secret

### Método 1: Via kubectl (Recomendado)

```bash
# Substitua <namespace> pelo ambiente correto (develop, staging, production)
kubectl create secret generic webapp-secret \
  --from-literal=VITE_API_URL="https://api.weni.ai/api/v1" \
  --from-literal=VITE_WEBCHAT_SOCKET_URL="https://websocket.weni.ai" \
  --from-literal=VITE_WEBCHAT_HOST="https://flows.weni.ai" \
  --from-literal=VITE_WEBCHAT_CHANNEL_UUID="a9687ddd-849c-44e2-8f81-da9a07de21b8" \
  --from-literal=VITE_VOICE_MODE_ENABLED="true" \
  --from-literal=VITE_ELEVENLABS_API_KEY="sk_your_api_key_here" \
  --from-literal=VITE_ELEVENLABS_VOICE_ID="IrjWdL4OFv83a0lTXEQg" \
  --from-literal=VITE_VOICE_MODE_LANGUAGE_CODE="pt" \
  --namespace=<namespace> \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Método 2: Via arquivo YAML

Crie um arquivo `webapp-secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: webapp-secret
  namespace: weni-roadmap-develop  # ou staging/production
type: Opaque
stringData:
  # API Configuration
  VITE_API_URL: "https://api.weni.ai/api/v1"

  # WebChat Configuration
  VITE_WEBCHAT_SOCKET_URL: "https://websocket.weni.ai"
  VITE_WEBCHAT_HOST: "https://flows.weni.ai"
  VITE_WEBCHAT_CHANNEL_UUID: "a9687ddd-849c-44e2-8f81-da9a07de21b8"

  # Voice Mode Configuration
  VITE_VOICE_MODE_ENABLED: "true"
  VITE_ELEVENLABS_API_KEY: "sk_your_api_key_here"
  VITE_ELEVENLABS_VOICE_ID: "IrjWdL4OFv83a0lTXEQg"

  # Optional: Language Code
  VITE_VOICE_MODE_LANGUAGE_CODE: "pt"
```

Aplique o secret:

```bash
kubectl apply -f webapp-secret.yaml
```

## Verificando o Secret

### Listar secrets

```bash
kubectl get secrets -n <namespace>
```

### Ver as chaves do secret (sem valores)

```bash
kubectl describe secret webapp-secret -n <namespace>
```

### Ver o conteúdo completo do secret

```bash
kubectl get secret webapp-secret -n <namespace> -o yaml
```

### Decodificar um valor específico

```bash
# Pegar o valor de VITE_ELEVENLABS_API_KEY
kubectl get secret webapp-secret -n <namespace> -o jsonpath='{.data.VITE_ELEVENLABS_API_KEY}' | base64 -d
echo  # nova linha
```

## Atualizando um Valor Específico

### Método 1: Patch (Recomendado para uma chave)

```bash
kubectl patch secret webapp-secret -n <namespace> \
  --type='json' \
  -p='[{"op":"add","path":"/data/VITE_ELEVENLABS_VOICE_ID","value":"'$(echo -n "NEW_VOICE_ID" | base64)'"}]'
```

### Método 2: Edit interativo

```bash
kubectl edit secret webapp-secret -n <namespace>
```

**Nota:** Os valores no YAML são base64. Para codificar:

```bash
echo -n "seu_valor_aqui" | base64
```

### Método 3: Delete e recrie

```bash
kubectl delete secret webapp-secret -n <namespace>
kubectl create secret generic webapp-secret --from-literal=... -n <namespace>
```

## Configuração por Ambiente

Cada ambiente deve ter seu próprio secret com valores apropriados:

### Development (namespace: weni-roadmap-develop)

```yaml
VITE_API_URL: "https://api-develop.weni.ai/api/v1"
VITE_WEBCHAT_CHANNEL_UUID: "<uuid-do-canal-dev>"
VITE_VOICE_MODE_ENABLED: "true"
VITE_ELEVENLABS_API_KEY: "<chave-dev>"
```

### Staging (namespace: weni-roadmap-staging)

```yaml
VITE_API_URL: "https://api-staging.weni.ai/api/v1"
VITE_WEBCHAT_CHANNEL_UUID: "<uuid-do-canal-staging>"
VITE_VOICE_MODE_ENABLED: "true"
VITE_ELEVENLABS_API_KEY: "<chave-staging>"
```

### Production (namespace: weni-roadmap)

```yaml
VITE_API_URL: "https://api.weni.ai/api/v1"
VITE_WEBCHAT_CHANNEL_UUID: "<uuid-do-canal-prod>"
VITE_VOICE_MODE_ENABLED: "true"
VITE_ELEVENLABS_API_KEY: "<chave-prod>"
```

## Troubleshooting

### Secret não é encontrado durante o build

**Sintoma:** Build do GitHub Actions falha com erro sobre secret não encontrado

**Soluções:**

1. Verifique se o secret existe no namespace correto:
   ```bash
   kubectl get secret webapp-secret -n <namespace>
   ```

2. Verifique se o namespace do workflow corresponde ao da tag:
   - Tag `*.*.*-develop` → namespace `weni-roadmap-develop`
   - Tag `*.*.*-staging` → namespace `weni-roadmap-staging`
   - Tag `*.*.*` → namespace `weni-roadmap`

3. Crie o secret se não existir (veja "Criando/Atualizando o Secret")

### Variável não está sendo reconhecida

**Sintoma:** Build passa mas a variável aparece como `undefined` na aplicação

**Causas possíveis:**

1. **Typo no nome da chave do secret**
   ```bash
   # Errado
   VITE_ELEVENLABS_VOICEID  # faltou o underscore

   # Correto
   VITE_ELEVENLABS_VOICE_ID
   ```

2. **Valor vazio no secret**
   ```bash
   # Verificar se o valor está vazio
   kubectl get secret webapp-secret -n <namespace> -o jsonpath='{.data.VITE_ELEVENLABS_VOICE_ID}' | base64 -d
   ```

3. **Variável não declarada no Dockerfile**

   Verifique se a variável está em `frontend/docker/Dockerfile`:
   ```dockerfile
   ARG VITE_ELEVENLABS_VOICE_ID
   ENV VITE_ELEVENLABS_VOICE_ID=${VITE_ELEVENLABS_VOICE_ID}
   ```

4. **Variável não está no vite-env.d.ts**

   Verifique se está declarada em `frontend/src/vite-env.d.ts`:
   ```typescript
   interface ImportMetaEnv {
     readonly VITE_ELEVENLABS_VOICE_ID?: string;
   }
   ```

### Build logs para debug

Para ver os logs detalhados do build e verificar quais valores foram recebidos:

1. Acesse o workflow no GitHub Actions
2. Procure pela etapa "Build Docker image"
3. Procure por "=== Build Arguments Received ===" nos logs
4. Verifique se todas as variáveis aparecem como `<set>` e não `<not set>`

### Recriar o secret em todos os ambientes

Script helper:

```bash
#!/bin/bash
# recreate-secrets.sh

ENVIRONMENTS=("weni-roadmap-develop" "weni-roadmap-staging" "weni-roadmap")

for ns in "${ENVIRONMENTS[@]}"; do
    echo "Creating secret in namespace: $ns"

    kubectl create secret generic webapp-secret \
      --from-literal=VITE_API_URL="https://api.weni.ai/api/v1" \
      --from-literal=VITE_WEBCHAT_SOCKET_URL="https://websocket.weni.ai" \
      --from-literal=VITE_WEBCHAT_HOST="https://flows.weni.ai" \
      --from-literal=VITE_WEBCHAT_CHANNEL_UUID="your-uuid" \
      --from-literal=VITE_VOICE_MODE_ENABLED="true" \
      --from-literal=VITE_ELEVENLABS_API_KEY="your-key" \
      --from-literal=VITE_ELEVENLABS_VOICE_ID="your-voice-id" \
      --namespace="$ns" \
      --dry-run=client -o yaml | kubectl apply -f -

    echo "✓ Secret created/updated in $ns"
    echo ""
done
```

## Segurança

### Boas Práticas

1. **Nunca commite secrets no git**
   - Não commite arquivos com valores reais
   - Use `.gitignore` para arquivos de secrets

2. **Use secrets diferentes por ambiente**
   - API keys de desenvolvimento não devem ser usadas em produção
   - Use UUIDs de canais diferentes por ambiente

3. **Rotacione as chaves periodicamente**
   ```bash
   # Atualizar API key
   kubectl patch secret webapp-secret -n <namespace> \
     --type='json' \
     -p='[{"op":"replace","path":"/data/VITE_ELEVENLABS_API_KEY","value":"'$(echo -n "NEW_KEY" | base64)'"}]'
   ```

4. **Restrinja acesso ao namespace**
   - Use RBAC para controlar quem pode ver/editar secrets
   - Audite acessos regulalmente

### Variáveis Sensíveis

As seguintes variáveis contêm informações sensíveis e devem ser protegidas:

- ✅ `VITE_ELEVENLABS_API_KEY` - **Muito sensível** (chave de API com cobrança)
- ⚠️ `VITE_WEBCHAT_CHANNEL_UUID` - Sensível (identifica seu canal)
- ℹ️ `VITE_ELEVENLABS_VOICE_ID` - Não sensível (ID público de voz)

## Referências

- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [GitHub Actions Workflow](/.github/workflows/build-image-on-push-tag-to-shared-ecr.yaml)
- [Dockerfile](/frontend/docker/Dockerfile)
- [Build Args Guide](./BUILD_ARGS_GUIDE.md)
