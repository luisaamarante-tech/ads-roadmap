# Configuração do Modo de Voz (Voice Mode)

Este documento explica como ativar e configurar o modo de voz no WebChat para o modo Canvas de busca conversacional.

## 📋 Pré-requisitos

1. **Conta ElevenLabs**: Você precisa de uma conta na [ElevenLabs](https://elevenlabs.io/) para obter:
   - API Key
   - Voice ID (recomendado: escolha uma voz multilíngue)

2. **Voice ID Recomendado**: `pFZP5JQG7iQjIQuC4Bku` (Lily - voz multilíngue)
   - Encontre mais vozes em: https://elevenlabs.io/app/voice-library

## 🚀 Como Ativar o Modo de Voz

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na pasta `frontend/` (se ainda não existir) ou edite o existente:

```bash
# Ativar o modo de voz
VITE_VOICE_MODE_ENABLED=true

# API Key da ElevenLabs (obrigatório)
VITE_ELEVENLABS_API_KEY=sua-api-key-aqui

# Voice ID (opcional - usa Lily por padrão)
VITE_ELEVENLABS_VOICE_ID=pFZP5JQG7iQjIQuC4Bku

# Código de idioma (opcional - auto-detecta do navegador)
# Opções: 'en' (Inglês), 'pt' (Português), 'es' (Espanhol)
VITE_VOICE_MODE_LANGUAGE_CODE=pt
```

### 2. Reiniciar o Servidor de Desenvolvimento

Após configurar as variáveis de ambiente, reinicie o servidor:

```bash
cd frontend
npm run dev
```

### 3. Testar o Modo de Voz

1. Abra a aplicação no navegador
2. Ative o modo Canvas clicando no botão de busca mágica
3. Você verá um ícone de ondas sonoras (🎤) ao lado do campo de entrada
4. Clique no ícone para ativar o modo de voz
5. Permita o acesso ao microfone quando solicitado
6. Fale naturalmente - a mensagem será enviada automaticamente após o silêncio

## ⚙️ Configurações Avançadas

### Opções de Configuração do Voice Mode

As seguintes opções são configuradas automaticamente no código:

- **silenceThreshold**: `1.5` segundos - tempo de silêncio antes do envio automático
- **enableBargeIn**: `true` - permite interromper o agente enquanto ele fala
- **autoListen**: `true` - ativa automaticamente a escuta após o agente terminar de falar

### Detecção de Idioma

O modo de voz suporta três estratégias de detecção de idioma:

1. **Auto-detectar do navegador (padrão)**:
   ```bash
   # Não definir VITE_VOICE_MODE_LANGUAGE_CODE
   ```

2. **Forçar idioma específico**:
   ```bash
   VITE_VOICE_MODE_LANGUAGE_CODE=pt  # Português
   # ou
   VITE_VOICE_MODE_LANGUAGE_CODE=en  # Inglês
   # ou
   VITE_VOICE_MODE_LANGUAGE_CODE=es  # Espanhol
   ```

## ⚠️ Segurança e Produção

### Importante: Proteção da API Key

**NUNCA exponha sua API Key diretamente no código frontend em produção!**

A configuração atual é adequada apenas para desenvolvimento local. Para produção, você deve:

1. **Criar um endpoint backend** que gera tokens da ElevenLabs
2. **Remover a API Key** das variáveis de ambiente do frontend
3. **Configurar o backend** para fazer as chamadas à API da ElevenLabs

### Exemplo de Endpoint Backend (Node.js/Express)

```javascript
// Backend - Endpoint para gerar token
app.get('/api/voice/token', async (req, res) => {
  try {
    const response = await fetch(
      'https://api.elevenlabs.io/v1/single-use-token/realtime_scribe',
      {
        method: 'POST',
        headers: {
          'xi-api-key': process.env.ELEVENLABS_API_KEY,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get token: ${response.status}`);
    }

    const data = await response.json();
    res.json({ token: data.token });
  } catch (error) {
    console.error('Error getting voice token:', error);
    res.status(500).json({ error: 'Failed to get voice token' });
  }
});
```

### Atualizar Frontend para Usar Backend

Quando você tiver o endpoint backend, atualize a função `getVoiceToken` em `useCanvasSearch.ts`:

```typescript
async function getVoiceToken(): Promise<string> {
  const response = await fetch('/api/voice/token');

  if (!response.ok) {
    throw new Error('Failed to get voice token');
  }

  const data = await response.json();
  return data.token;
}
```

## 🧪 Testes

Para desativar o modo de voz durante testes, defina:

```bash
VITE_VOICE_MODE_ENABLED=false
```

Isso está configurado por padrão no arquivo `.env.test`.

## 🚢 Deployment em Produção

Para ativar o modo de voz em produção (build Docker via GitHub Actions), você precisa configurar as variáveis como **GitHub Secrets**.

### Configurar GitHub Secrets

1. Acesse o repositório no GitHub: `weni-ai/weni-roadmap`
2. Vá em **Settings** > **Secrets and variables** > **Actions**
3. Clique em **New repository secret**
4. Adicione as seguintes secrets:

| Nome da Secret | Valor | Obrigatório |
|----------------|-------|-------------|
| `VITE_VOICE_MODE_ENABLED` | `true` ou `false` | Sim |
| `VITE_ELEVENLABS_API_KEY` | Sua API key da ElevenLabs | Sim (se enabled=true) |
| `VITE_ELEVENLABS_VOICE_ID` | Voice ID (ex: `pFZP5JQG7iQjIQuC4Bku`) | Opcional |
| `VITE_VOICE_MODE_LANGUAGE_CODE` | `pt`, `en`, ou `es` | Opcional |

**Importante**: O workflow do GitHub Actions (`build-image-on-push-tag-to-shared-ecr.yaml`) herda automaticamente todos os secrets com `secrets: inherit` e o flag `kludge_webapp_secret_enable: true`, que passa todas as variáveis `VITE_*` como build args para o Docker.

### Verificar o Build

Após criar uma tag (ex: `1.2.0-develop`), você pode verificar nos logs do job `call-workflow-frontend` se as variáveis foram passadas corretamente para o build da imagem Docker.

## 📚 Referências

- **ElevenLabs API Docs**: https://elevenlabs.io/docs
- **Voice Library**: https://elevenlabs.io/app/voice-library
- **Pricing**: https://elevenlabs.io/pricing

## 🐛 Troubleshooting

### Modo de Voz não aparece

1. Verifique se `VITE_VOICE_MODE_ENABLED=true` no arquivo `.env`
2. Reinicie o servidor de desenvolvimento
3. Limpe o cache do navegador (Ctrl+Shift+Delete)
4. Verifique o console do navegador para erros

### Erro "API key not configured"

1. Verifique se `VITE_ELEVENLABS_API_KEY` está definido no `.env`
2. Certifique-se de que a API key é válida
3. Reinicie o servidor de desenvolvimento

### Microfone não funciona

1. Verifique se o navegador tem permissão para acessar o microfone
2. Teste o microfone em outra aplicação
3. Verifique as configurações de privacidade do sistema operacional

### Voice ID inválido

1. Acesse https://elevenlabs.io/app/voice-library
2. Escolha uma voz **multilíngue** (recomendado)
3. Copie o Voice ID e atualize `VITE_ELEVENLABS_VOICE_ID`
4. Reinicie o servidor de desenvolvimento
