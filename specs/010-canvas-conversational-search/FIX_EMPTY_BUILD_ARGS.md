# Fix: Build Args Vazios no Docker Build

**Problema**: As variáveis aparecem vazias no build:
```
#19 0.050 Building with environment variables:
#19 0.050   VITE_API_URL=
#19 0.050   VITE_WEBCHAT_CHANNEL_UUID=
#19 0.050   VITE_WEBCHAT_SOCKET_URL=
#19 0.050   VITE_WEBCHAT_HOST=
```

**Causa**: O reusable workflow `weni-ai/actions-workflows` não está passando as secrets como build arguments para o `docker build`.

---

## 🔧 **O que Foi Feito**

### 1. Workflow Atualizado

**Arquivo**: `.github/workflows/build-image-on-push-tag-to-shared-ecr.yaml`

Mudamos de `secrets: inherit` para passar as secrets explicitamente:

```yaml
call-workflow-frontend:
  uses: weni-ai/actions-workflows/.github/workflows/reusable-workflow.yaml@main
  with:
    # ... parâmetros ...
  secrets:
    # Passar secrets explicitamente
    VITE_WEBCHAT_CHANNEL_UUID: ${{ secrets.VITE_WEBCHAT_CHANNEL_UUID }}
    VITE_WEBCHAT_SOCKET_URL: ${{ secrets.VITE_WEBCHAT_SOCKET_URL }}
    VITE_WEBCHAT_HOST: ${{ secrets.VITE_WEBCHAT_HOST }}
    VITE_API_URL: ${{ secrets.VITE_API_URL }}
```

### 2. Dockerfile já está Pronto

**Arquivo**: `frontend/docker/Dockerfile`

O Dockerfile já está configurado para receber as variáveis como build args:

```dockerfile
ARG VITE_API_URL
ARG VITE_WEBCHAT_CHANNEL_UUID
ARG VITE_WEBCHAT_SOCKET_URL
ARG VITE_WEBCHAT_HOST

ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WEBCHAT_CHANNEL_UUID=${VITE_WEBCHAT_CHANNEL_UUID}
# ...
```

---

## ✅ **Próximos Passos**

### **Opção 1: Verificar se o Reusable Workflow Já Suporta**

O flag `kludge_webapp_secret_enable: true` pode indicar que o reusable workflow já tem suporte para passar secrets como build args.

**Teste**:

1. **Configure as GitHub Secrets**:
   ```
   Settings > Secrets and variables > Actions > New repository secret
   
   - VITE_WEBCHAT_CHANNEL_UUID = a9687ddd-849c-44e2-8f81-da9a07de21b8
   - VITE_WEBCHAT_SOCKET_URL = https://websocket.weni.ai
   - VITE_WEBCHAT_HOST = https://flows.weni.ai
   - VITE_API_URL = https://api.roadmap.weni.ai
   ```

2. **Faça push de uma tag de teste**:
   ```bash
   git tag 1.1.0-develop
   git push origin 1.1.0-develop
   ```

3. **Verifique os logs do workflow**:
   - Acesse: `Actions > Build, push and deploy > call-workflow-frontend`
   - Procure por: `Building with environment variables:`
   - **Se aparecer valores** (não vazios), funcionou! ✅
   - **Se ainda estiverem vazios**, vá para Opção 2

---

### **Opção 2: Modificar o Reusable Workflow (Se Necessário)**

Se o reusable workflow **não suporta** passar essas secrets como build args, você tem 2 opções:

#### **A) Modificar o Reusable Workflow** (Recomendado)

**Repositório**: `weni-ai/actions-workflows`

1. Abra o arquivo: `.github/workflows/reusable-workflow.yaml`
2. Adicione os secrets como inputs:

```yaml
on:
  workflow_call:
    inputs:
      # ... existing inputs ...
    secrets:
      # ... existing secrets ...
      VITE_WEBCHAT_CHANNEL_UUID:
        required: false
      VITE_WEBCHAT_SOCKET_URL:
        required: false
      VITE_WEBCHAT_HOST:
        required: false
      VITE_API_URL:
        required: false
```

3. No step de `docker build`, adicione os build args:

```yaml
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

4. Commit e push:
   ```bash
   git commit -m "feat: support VITE_* build args for webapp builds"
   git push
   ```

5. Teste novamente no `weni-roadmap` com uma nova tag

#### **B) Criar Step Customizado no weni-roadmap** (Alternativa Temporária)

Se você **não pode modificar** o reusable workflow, pode criar um step customizado:

**Arquivo**: `.github/workflows/build-image-on-push-tag-to-shared-ecr.yaml`

Substitua o job `call-workflow-frontend` por:

```yaml
build-frontend:
  runs-on: ubuntu-latest
  needs:
    - setup
  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-region: us-east-1
        role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        file: ./frontend/docker/Dockerfile
        push: true
        tags: |
          ${{ steps.login-ecr.outputs.registry }}/${{ needs.setup.outputs.repository_name }}:webapp-${{ github.ref_name }}
        build-args: |
          VITE_API_URL=${{ secrets.VITE_API_URL }}
          VITE_WEBCHAT_CHANNEL_UUID=${{ secrets.VITE_WEBCHAT_CHANNEL_UUID }}
          VITE_WEBCHAT_SOCKET_URL=${{ secrets.VITE_WEBCHAT_SOCKET_URL }}
          VITE_WEBCHAT_HOST=${{ secrets.VITE_WEBCHAT_HOST }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    # Adicionar steps para atualizar kubernetes-manifests
    # ... (consulte o reusable workflow original para ver como fazer)
```

---

## 🔍 **Como Verificar se Está Funcionando**

### 1. Logs do Build

Procure por esta seção nos logs:

✅ **Funcionando**:
```
#19 0.050 Building with environment variables:
#19 0.050   VITE_API_URL=https://api.roadmap.weni.ai
#19 0.050   VITE_WEBCHAT_CHANNEL_UUID=a9687ddd-849c-44e2-8f81-da9a07de21b8
#19 0.050   VITE_WEBCHAT_SOCKET_URL=https://websocket.weni.ai
#19 0.050   VITE_WEBCHAT_HOST=https://flows.weni.ai
```

❌ **Não Funcionando**:
```
#19 0.050 Building with environment variables:
#19 0.050   VITE_API_URL=
#19 0.050   VITE_WEBCHAT_CHANNEL_UUID=
#19 0.050   VITE_WEBCHAT_SOCKET_URL=
#19 0.050   VITE_WEBCHAT_HOST=
```

### 2. Console do Navegador em Produção

Após o deploy:

1. Acesse o site em produção
2. Abra DevTools (F12) > Console
3. Clique no botão Canvas Search
4. Verifique que **não aparece**:
   ```
   ❌ WebChat channel UUID not configured
   ```

### 3. Inspecionar o Bundle

```bash
# Pull da imagem
docker pull <ecr-registry>/weni-roadmap:webapp-<tag>

# Extrair bundle
docker create --name temp <ecr-registry>/weni-roadmap:webapp-<tag>
docker cp temp:/usr/share/nginx/html/assets ./assets
docker rm temp

# Procurar pelo UUID
grep -r "a9687ddd-849c-44e2-8f81-da9a07de21b8" ./assets/

# Deve retornar o arquivo .js com o UUID embutido
```

---

## 🐛 **Troubleshooting**

### Problema: Secrets não configurados

**Erro**: Valores ainda vazios após configurar o workflow.

**Solução**:
1. Verifique se as secrets estão configuradas no GitHub:
   ```
   https://github.com/weni-ai/weni-roadmap/settings/secrets/actions
   ```
2. Confirme que os nomes das secrets estão **exatamente** como no workflow:
   - `VITE_WEBCHAT_CHANNEL_UUID` (sem espaços, case-sensitive)

### Problema: Reusable workflow não suporta secrets

**Erro**: Secrets passados mas não usados no build.

**Solução**:
1. Consulte o time de DevOps da Weni AI
2. Verifique a documentação do `weni-ai/actions-workflows`
3. Use a **Opção 2B** (criar step customizado) temporariamente

### Problema: `kludge_webapp_secret_enable` não funciona

**Causa**: O flag pode fazer outra coisa, não passar build args.

**Solução**:
1. Verifique o código do reusable workflow para entender o que esse flag faz
2. Se não relacionado a build args, use **Opção 2A** ou **2B**

---

## 📋 **Checklist de Validação**

Após implementar a solução:

- [ ] GitHub Secrets configurados com valores corretos
- [ ] Workflow atualizado (commit `804bd9e` aplicado)
- [ ] Tag de teste criada e workflow acionado
- [ ] Logs do build mostram variáveis com valores (não vazios)
- [ ] Deploy concluído com sucesso
- [ ] Console do navegador sem erro de "channel UUID not configured"
- [ ] Canvas Search funciona em produção
- [ ] UUID visível no bundle JavaScript (grep confirmado)

---

## 💡 **Recomendação**

**Passo 1**: Teste a **Opção 1** primeiro (pode já funcionar com `kludge_webapp_secret_enable`).

**Passo 2**: Se não funcionar, consulte o time de DevOps sobre modificar o reusable workflow (**Opção 2A**).

**Passo 3**: Como última alternativa, use um step customizado (**Opção 2B**) temporariamente até o reusable workflow ser atualizado.

---

## 📞 **Contato**

- **Time de DevOps**: Para modificar `weni-ai/actions-workflows`
- **Issue**: Abra uma issue no `weni-ai/actions-workflows` solicitando suporte a build args customizados
- **Pull Request**: Se tiver permissão, abra um PR no reusable workflow

---

**Status**: ✅ Workflow local atualizado (commit `804bd9e`)
**Próximo Passo**: Configurar GitHub Secrets e testar
