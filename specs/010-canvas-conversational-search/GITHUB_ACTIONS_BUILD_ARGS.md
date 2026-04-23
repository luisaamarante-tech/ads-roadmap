# Guia: Passar Build Args no GitHub Actions

**Feature**: 010-canvas-conversational-search
**Criado em**: January 22, 2026

## 📝 Objetivo

Configurar os build arguments (`--build-arg`) do Docker no GitHub Actions para passar as variáveis do WebChat durante o build da imagem do frontend.

---

## 🏗️ Arquitetura Atual

O projeto usa:
- **Reusable Workflow**: `weni-ai/actions-workflows/.github/workflows/reusable-workflow.yaml@main`
- **Secrets Inheritance**: `secrets: inherit`
- **Frontend Flag**: `kludge_webapp_secret_enable: true`

---

## 🚀 Opções para Passar Build Args

### **Opção 1: GitHub Secrets (Recomendado para Produção)**

Esta é a forma mais segura e recomendada para valores sensíveis como Channel UUIDs.

#### **Passo 1: Configurar Secrets no GitHub**

1. Acesse o repositório no GitHub: `weni-ai/weni-roadmap`
2. Vá em **Settings** > **Secrets and variables** > **Actions**
3. Clique em **New repository secret**
4. Adicione as seguintes secrets:

| Nome da Secret | Valor | Descrição |
|----------------|-------|-----------|
| `VITE_WEBCHAT_CHANNEL_UUID` | `a9687ddd-849c-44e2-8f81-da9a07de21b8` | Channel UUID do WebChat |
| `VITE_WEBCHAT_SOCKET_URL` | `https://websocket.weni.ai` | (Opcional) WebSocket URL |
| `VITE_WEBCHAT_HOST` | `https://flows.weni.ai` | (Opcional) WebChat Host |
| `VITE_API_URL` | `https://roadmap-api.weni.ai` | API URL do backend |

#### **Passo 2: Verificar o Reusable Workflow**

O reusable workflow `weni-ai/actions-workflows` provavelmente já suporta passar secrets como build args quando `kludge_webapp_secret_enable: true` está configurado.

**Verifique no repositório `weni-ai/actions-workflows`:**

```yaml
# Exemplo de como o reusable workflow pode processar secrets
- name: Build Docker image
  run: |
    docker build \
      --build-arg VITE_API_URL="${{ secrets.VITE_API_URL }}" \
      --build-arg VITE_WEBCHAT_CHANNEL_UUID="${{ secrets.VITE_WEBCHAT_CHANNEL_UUID }}" \
      --build-arg VITE_WEBCHAT_SOCKET_URL="${{ secrets.VITE_WEBCHAT_SOCKET_URL }}" \
      --build-arg VITE_WEBCHAT_HOST="${{ secrets.VITE_WEBCHAT_HOST }}" \
      -f ${{ inputs.dockerfile }} \
      -t ${{ inputs.image_repository }}:${{ inputs.image_tag }} \
      ${{ inputs.build_context }}
```

#### **Passo 3: Testar**

```bash
# Criar uma tag para acionar o workflow
git tag 1.1.0-develop
git push origin 1.1.0-develop
```

Verifique os logs do job `call-workflow-frontend` para confirmar que os build args foram passados.

---

### **Opção 2: Atualizar o Reusable Workflow (Se Necessário)**

Se o reusable workflow atual **não suporta** passar as secrets automaticamente, você precisará atualizar o workflow local.

#### **Modificar `.github/workflows/build-image-on-push-tag-to-shared-ecr.yaml`:**

```yaml
call-workflow-frontend:
  uses: weni-ai/actions-workflows/.github/workflows/reusable-workflow.yaml@main
  needs:
    - setup
  with:
    image_repository: "${{ needs.setup.outputs.repository_name }}"
    target_application: "${{ needs.setup.outputs.repository_name }}"
    dockerfile: "frontend/docker/Dockerfile"
    build_context: "frontend/"
    kludge_webapp_secret_enable: true
    target_repository: weni-ai/kubernetes-manifests
    target_patch_file: deployment-frontend-image.json
    image_tag_prefix: webapp-
    # NOVO: Passar build args explicitamente (se suportado pelo reusable workflow)
    build_args: |
      VITE_API_URL=${{ secrets.VITE_API_URL }}
      VITE_WEBCHAT_CHANNEL_UUID=${{ secrets.VITE_WEBCHAT_CHANNEL_UUID }}
      VITE_WEBCHAT_SOCKET_URL=${{ secrets.VITE_WEBCHAT_SOCKET_URL }}
      VITE_WEBCHAT_HOST=${{ secrets.VITE_WEBCHAT_HOST }}
  secrets: inherit
```

**Nota**: Verifique se o reusable workflow aceita o parâmetro `build_args`. Consulte a documentação em `weni-ai/actions-workflows`.

---

### **Opção 3: Criar Step Customizado (Última Opção)**

Se o reusable workflow **não suporta** build args customizados, você pode criar um step próprio para o build:

```yaml
call-workflow-frontend:
  runs-on: ubuntu-latest
  needs:
    - setup
  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to ECR
      uses: aws-actions/amazon-ecr-login@v2
      with:
        mask-password: true

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        file: ./frontend/docker/Dockerfile
        push: true
        tags: |
          ${{ secrets.ECR_REGISTRY }}/${{ needs.setup.outputs.repository_name }}:webapp-${{ github.ref_name }}
        build-args: |
          VITE_API_URL=${{ secrets.VITE_API_URL }}
          VITE_WEBCHAT_CHANNEL_UUID=${{ secrets.VITE_WEBCHAT_CHANNEL_UUID }}
          VITE_WEBCHAT_SOCKET_URL=${{ secrets.VITE_WEBCHAT_SOCKET_URL }}
          VITE_WEBCHAT_HOST=${{ secrets.VITE_WEBCHAT_HOST }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    # Adicionar steps para deploy no kubernetes-manifests
```

---

## 🔍 Verificação

### **1. Verificar Secrets Configurados**

```bash
# No GitHub UI:
# Settings > Secrets and variables > Actions
# Deve mostrar:
# - VITE_WEBCHAT_CHANNEL_UUID
# - VITE_WEBCHAT_SOCKET_URL (opcional)
# - VITE_WEBCHAT_HOST (opcional)
# - VITE_API_URL
```

### **2. Verificar Logs do Workflow**

Após fazer push de uma tag:

1. Vá em **Actions** no GitHub
2. Clique no workflow **Build, push and deploy**
3. Clique no job **call-workflow-frontend**
4. Procure por:

```
Building Docker image...
  --build-arg VITE_WEBCHAT_CHANNEL_UUID=***
```

**Nota**: O valor será mascarado como `***` por segurança.

### **3. Verificar Imagem Docker**

Após o build, você pode inspecionar a imagem:

```bash
# Pull da imagem
docker pull <ecr-registry>/weni-roadmap:webapp-1.1.0-develop

# Executar a imagem
docker run -d -p 8080:8080 <ecr-registry>/weni-roadmap:webapp-1.1.0-develop

# Acessar e verificar no browser
open http://localhost:8080

# Abrir DevTools (F12) > Console
# Verificar que não aparece: "WebChat channel UUID not configured"
```

### **4. Verificar Bundle JavaScript**

```bash
# Extrair arquivos da imagem
docker create --name temp-container <ecr-registry>/weni-roadmap:webapp-1.1.0-develop
docker cp temp-container:/usr/share/nginx/html/assets ./extracted-assets
docker rm temp-container

# Procurar pelo UUID no bundle
grep -r "a9687ddd-849c-44e2-8f81-da9a07de21b8" ./extracted-assets/

# Deve retornar o arquivo JavaScript com o UUID embutido
```

---

## 🛠️ Troubleshooting

### ❌ Problema: "WebChat channel UUID not configured" em produção

**Causa**: Build args não foram passados durante `docker build`.

**Soluções**:

1. **Verificar se secrets existem no GitHub**:
   - Settings > Secrets and variables > Actions
   - Confirmar que `VITE_WEBCHAT_CHANNEL_UUID` existe

2. **Verificar logs do workflow**:
   - Actions > Build, push and deploy > call-workflow-frontend
   - Procurar por `--build-arg VITE_WEBCHAT_CHANNEL_UUID`
   - Se não aparecer, o reusable workflow não está passando os build args

3. **Consultar o time de DevOps**:
   - Perguntar como passar build args customizados no `weni-ai/actions-workflows`
   - Verificar se há documentação interna

4. **Alternativa temporária** (não recomendado):
   - Hardcode o valor no `.env` (mas será commitado ao Git se não estiver no `.gitignore`)

### ❌ Problema: Secrets não disponíveis no reusable workflow

**Causa**: `secrets: inherit` pode não estar funcionando corretamente.

**Solução**:

Passe as secrets explicitamente:

```yaml
call-workflow-frontend:
  uses: weni-ai/actions-workflows/.github/workflows/reusable-workflow.yaml@main
  needs:
    - setup
  with:
    # ... outros parâmetros ...
  secrets:
    VITE_API_URL: ${{ secrets.VITE_API_URL }}
    VITE_WEBCHAT_CHANNEL_UUID: ${{ secrets.VITE_WEBCHAT_CHANNEL_UUID }}
    VITE_WEBCHAT_SOCKET_URL: ${{ secrets.VITE_WEBCHAT_SOCKET_URL }}
    VITE_WEBCHAT_HOST: ${{ secrets.VITE_WEBCHAT_HOST }}
```

### ❌ Problema: Build args aparecem vazios nos logs

**Causa**: Secrets não foram configurados no GitHub.

**Solução**:

1. Configurar todas as secrets necessárias no GitHub UI
2. Testar localmente primeiro:

```bash
# Build local para validar
docker build \
  --build-arg VITE_API_URL="http://localhost:5001/api/v1" \
  --build-arg VITE_WEBCHAT_CHANNEL_UUID="test-uuid-123" \
  -f frontend/docker/Dockerfile \
  -t weni-roadmap-frontend:test \
  ./frontend
```

---

## 📋 Checklist de Implementação

Antes de fazer deploy:

- [ ] Secrets configurados no GitHub (VITE_WEBCHAT_CHANNEL_UUID, etc.)
- [ ] Dockerfile atualizado com ARGs (já feito ✅)
- [ ] Workflow atualizado para passar build args (se necessário)
- [ ] Tag criada e workflow acionado
- [ ] Logs do workflow verificados (build args presentes)
- [ ] Imagem Docker testada localmente (se possível)
- [ ] Console do navegador sem erros em produção
- [ ] Canvas Search funcional em produção

---

## 🔐 Segurança

### ✅ Boas Práticas

- Use **GitHub Secrets** para valores sensíveis
- Configure **branch protection rules** para proteger secrets
- Use **different secrets** para ambientes diferentes (dev/staging/prod)
- **Rotate secrets** periodicamente
- **Audit** quem tem acesso às secrets

### ⚠️ Secrets vs Environment Variables

| Tipo | Uso | Visibilidade | Quando Usar |
|------|-----|--------------|-------------|
| **GitHub Secrets** | Build args, deploy keys | Mascarado nos logs | Valores sensíveis (API keys, UUIDs) |
| **Environment Variables** | Runtime config | Visível nos logs | Valores públicos (URLs públicas) |
| **Hardcoded no código** | Constantes | Público no Git | ❌ Nunca para valores sensíveis |

---

## 📚 Recursos Úteis

- [GitHub Actions: Using secrets in workflows](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Docker Build Args](https://docs.docker.com/build/guide/build-args/)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Weni AI Actions Workflows](https://github.com/weni-ai/actions-workflows) (repositório interno)

---

## 💡 Recomendação Final

**Passo a Passo Recomendado**:

1. ✅ Configure as **GitHub Secrets** primeiro
2. ✅ Verifique se o **reusable workflow** já suporta passar essas secrets
3. ✅ Se não suportar, **atualize o workflow local** para passar explicitamente
4. ✅ Teste fazendo push de uma **tag de desenvolvimento** (`1.1.0-develop`)
5. ✅ Verifique os **logs do workflow** para confirmar build args
6. ✅ Teste em **produção** após sucesso em dev/staging

**Dúvidas?** Consulte o time de DevOps ou a documentação interna do `weni-ai/actions-workflows`! 🚀
