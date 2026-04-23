# Guia Rápido: Configurar Variáveis do WebChat no Netlify

**Feature**: 010-canvas-conversational-search
**Criado em**: January 22, 2026

## 📝 Objetivo

Configurar as variáveis de ambiente necessárias para o Canvas Conversational Search funcionar em produção no Netlify.

---

## 🚀 Passo a Passo

### 1. Acesse o Site do Frontend no Netlify

1. Faça login no [Netlify](https://app.netlify.com)
2. Navegue até o site do **frontend** do Weni Roadmap
3. Clique em **Site Settings**

### 2. Configure as Variáveis de Ambiente

1. No menu lateral, clique em **Environment variables**
2. Clique no botão **Add a variable**

### 3. Adicione as Variáveis Obrigatórias

#### **VITE_WEBCHAT_CHANNEL_UUID** (OBRIGATÓRIO)

- **Key**: `VITE_WEBCHAT_CHANNEL_UUID`
- **Value**: Seu UUID do canal do WebChat (ex: `a9687ddd-849c-44e2-8f81-da9a07de21b8`)
- **Contexts**: 
  - ✅ Production
  - ✅ Deploy previews
  - ✅ Branch deploys
- **Secret**: ❌ Não (não é sensível, mas específico do projeto)

**Como obter o Channel UUID:**
- Acesse o Weni Platform
- Vá até seu projeto de WebChat
- Copie o **Channel UUID** do canal configurado

#### **VITE_WEBCHAT_SOCKET_URL** (OPCIONAL)

- **Key**: `VITE_WEBCHAT_SOCKET_URL`
- **Value**: `https://websocket.weni.ai`
- **Contexts**: 
  - ✅ Production
  - ✅ Deploy previews
  - ✅ Branch deploys
- **Secret**: ❌ Não

⚠️ **Nota**: Só necessário se usar um servidor WebSocket diferente do padrão.

#### **VITE_WEBCHAT_HOST** (OPCIONAL)

- **Key**: `VITE_WEBCHAT_HOST`
- **Value**: `https://flows.weni.ai`
- **Contexts**: 
  - ✅ Production
  - ✅ Deploy previews
  - ✅ Branch deploys
- **Secret**: ❌ Não

⚠️ **Nota**: Só necessário se usar um host diferente do padrão.

---

## 🎯 Resumo Visual - Netlify UI

```
┌─────────────────────────────────────────────┐
│ Site Settings > Environment variables       │
├─────────────────────────────────────────────┤
│                                             │
│ Key: VITE_WEBCHAT_CHANNEL_UUID              │
│ Value: a9687ddd-849c-44e2-8f81-da9a07de21b8 │
│                                             │
│ Contexts:                                   │
│   ☑ Production                              │
│   ☑ Deploy previews                         │
│   ☑ Branch deploys                          │
│                                             │
│ [Add variable]                              │
└─────────────────────────────────────────────┘
```

---

## ✅ Verificação Pós-Configuração

### 1. Force um Novo Deploy

Após adicionar as variáveis:

1. Vá até **Deploys**
2. Clique em **Trigger deploy** > **Deploy site**
3. Aguarde o build completar

### 2. Verifique no Build Log

No log do build, procure por:

```
Building with environment variables:
  VITE_WEBCHAT_CHANNEL_UUID: a9687ddd-849c-44e2-8f81-da9a07de21b8
```

### 3. Teste o Canvas Search em Produção

1. Acesse seu site em produção
2. Clique no botão de **Canvas Search** (ícone de busca conversacional)
3. O WebChat deve carregar sem erros no console
4. Digite uma busca e verifique se retorna resultados

### 4. Verificar Console do Navegador

Abra o DevTools (F12) e verifique se **NÃO** aparecem erros como:

❌ **Erro (antes da configuração)**:
```
WebChat channel UUID not configured. Set VITE_WEBCHAT_CHANNEL_UUID.
```

✅ **Sucesso (após configuração)**:
```
WebChat initialized successfully
```

---

## 🔍 Troubleshooting

### ❌ Erro: "WebChat channel UUID not configured"

**Causa**: A variável `VITE_WEBCHAT_CHANNEL_UUID` não está configurada ou não foi aplicada no build.

**Solução**:
1. Verifique se a variável está salva no Netlify UI
2. Confirme que o **contexto correto** está selecionado (Production)
3. Force um **novo deploy** (as variáveis só são aplicadas em novos builds)
4. Limpe o cache do Netlify: **Site Settings > Build & deploy > Clear cache and deploy site**

### ❌ Erro: "WebChat library not loaded"

**Causa**: O script do WebChat não foi carregado no HTML.

**Solução**:
1. Verifique se o script está no `index.html`:
   ```html
   <script src="https://webchat.weni.ai/v3/webchat.js"></script>
   ```
2. Verifique a conexão de rede do navegador
3. Teste em uma aba anônima para descartar cache

### ❌ Canvas Search não retorna resultados

**Causa**: O Channel UUID pode estar incorreto ou o flow não está configurado.

**Solução**:
1. Verifique se o UUID está correto no Weni Platform
2. Confirme que o flow do WebChat está publicado e ativo
3. Teste o WebChat diretamente fora do roadmap para validar
4. Verifique logs do backend para erros de integração

---

## 📚 Referências

- [Documentação completa de variáveis de ambiente](../005-netlify-deployment/contracts/environment-variables.md)
- [Checklist de configuração Netlify](../005-netlify-deployment/ENV_VARIABLES_CHECKLIST.md)
- [Netlify Environment Variables Documentation](https://docs.netlify.com/environment-variables/overview/)
- [Vite Environment Variables Guide](https://vitejs.dev/guide/env-and-mode.html)

---

## 📝 Checklist Rápido

Antes de fazer deploy em produção:

- [ ] `VITE_WEBCHAT_CHANNEL_UUID` configurada no Netlify
- [ ] Contexto **Production** selecionado
- [ ] Novo deploy forçado após configuração
- [ ] Build log verificado (variável presente)
- [ ] Canvas Search testado em produção
- [ ] Console do navegador sem erros
- [ ] Flow do WebChat testado e funcional
- [ ] Documentação atualizada com UUID real (se necessário)

---

## 💡 Dica Pro

Para facilitar debug em diferentes ambientes, você pode usar UUIDs diferentes por contexto:

**Production**:
```
VITE_WEBCHAT_CHANNEL_UUID=production-uuid-here
```

**Deploy Preview**:
```
VITE_WEBCHAT_CHANNEL_UUID=staging-uuid-here
```

**Branch Deploy**:
```
VITE_WEBCHAT_CHANNEL_UUID=dev-uuid-here
```

Isso permite testar diferentes flows do WebChat em cada ambiente!
