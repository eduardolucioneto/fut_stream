# 🔍 Informações de Debug da Transmissão

## 📡 Página de Transmissão (Broadcaster)

### Informações Exibidas no Template

O template `broadcast.html` exibe as seguintes informações de debug em tempo real:

#### 1. **Status da Conexão**
- Localização: Elemento `#status`
- Estados possíveis:
  - "Inicializando..."
  - "Pronto para compartilhar"
  - "Aguardando seleção..."
  - "Broadcasting (Live) 🔊 Com Áudio" ou "Broadcasting (Live) 🔇 Sem Áudio"
  - "Stream encerrado"
  - "Erro ao compartilhar"

#### 2. **Peer ID**
- Localização: Elemento `#my-peer-id`
- Formato: `futstream_host_{stream_id}`
- Exibe o ID único do peer do transmissor

#### 3. **Debug Info (Elemento #debug-info)**
Localizado em um painel cinza com fonte monospace, exibe:

**Informações de Vídeo:**
- 📹 Número de Video Tracks
- Resolução (width x height)
- FPS (frames por segundo)
- Estado do track (readyState)

**Informações de Áudio:**
- 🔊 Número de Audio Tracks
- Label de cada track
- Sample Rate (Hz)
- Estado de cada track (readyState)

#### 4. **Console Logs**

O broadcaster registra os seguintes logs no console do navegador:

**Conexão:**
- `✅ Peer connected: {id}` - Quando o peer se conecta
- `🎬 Requesting screen share...` - Ao solicitar compartilhamento
- `✅ Display stream obtained` - Stream obtido com sucesso
- `✅ Microphone stream obtained` - Microfone obtido

**Chamadas de Viewers:**
- `📞 Received call from {peer_id}` - Chamada recebida
- `✅ Answering call with stream` - Respondendo chamada
- `📹 Video tracks: {count}` - Número de tracks de vídeo
- `🔊 Audio tracks: {count}` - Número de tracks de áudio

**Estados de Conexão:**
- `🔗 Connection with {peer}: {state}` - Estado da conexão WebRTC
- `🧊 ICE with {peer}: {state}` - Estado ICE
- `✅ Successfully connected to viewer: {peer}` - Conexão bem-sucedida
- `❌ Lost connection with viewer: {peer}` - Conexão perdida

**Stream:**
- `📡 Receiving stream from viewer {peer}` - Recebendo stream
- `🔌 Call closed with {peer}` - Chamada fechada
- `⚠️ Video track ended` - Track de vídeo encerrado

**Erros:**
- `❌ Error with {peer}: {error}` - Erro com viewer específico
- `⚠️ Call received but stream not ready yet` - Stream não pronto

### Configuração de Debug

**Nível de Debug do PeerJS:**
```javascript
debug: 3  // Nível máximo de debug
```

**ICE Servers Configurados:**
- stun:stun.l.google.com:19302
- stun:stun1.l.google.com:19302
- stun:stun2.l.google.com:19302
- stun:stun3.l.google.com:19302
- stun:stun4.l.google.com:19302

---

## 👁️ Página de Visualização (Viewer)

### Informações Exibidas no Template

#### 1. **Status da Conexão**
- Localização: Elemento `#status`
- Estados possíveis:
  - "Connecting..."
  - "Ao Vivo 🔊" (com áudio)
  - "Ao Vivo 🔇" (sem áudio)
  - "Ao Vivo 🔇 (Clique para ativar áudio)"
  - "Stream sem vídeo"
  - "Conexão perdida"
  - "Host não respondeu (Timeout)"
  - "Stream encerrado"
  - "Erro: {tipo}"
  - "Stream offline ou host não encontrado"

#### 2. **Console Logs**

O viewer registra os seguintes logs no console:

**Conexão:**
- `✅ My Peer ID: {id}` - ID do peer do viewer
- `🔄 Initiating call to {host_peer_id}` - Iniciando chamada
- `🔌 Closing previous call` - Fechando chamada anterior

**Estados de Conexão:**
- `🔗 Connection State: {state}` - Estado da conexão WebRTC
  - Estados: connecting, connected, disconnected, failed, closed
- `🧊 ICE State: {state}` - Estado ICE
  - Estados: new, checking, connected, completed, failed, disconnected, closed
- `✅ WebRTC connection established!` - Conexão estabelecida

**Stream:**
- `✅ Received remote stream!` - Stream recebido
- `📹 Video tracks: {tracks}` - Tracks de vídeo
- `🔊 Audio tracks: {tracks}` - Tracks de áudio
- `❌ No video tracks in stream!` - Sem vídeo no stream

**Reprodução:**
- `✅ Video playing with audio` - Vídeo tocando com áudio
- `⚠️ Autoplay with audio prevented: {error}` - Autoplay bloqueado
- `✅ Video playing (muted fallback)` - Vídeo tocando mutado
- `❌ Autoplay failed completely: {error}` - Autoplay falhou

**Tracks:**
- `⚠️ Track ended: {kind}` - Track encerrado (video/audio)

**Data Connection:**
- `✅ Data connection opened` - Conexão de dados aberta
- `❌ Data connection error: {error}` - Erro na conexão de dados

**Erros:**
- `❌ Peer Error: {error}` - Erro do peer
- `❌ Call object creation failed!` - Falha ao criar chamada
- `❌ Call Error: {error}` - Erro na chamada
- `⏱️ Connection timed out.` - Timeout (15 segundos)

### Configuração de Debug

**Nível de Debug do PeerJS:**
```javascript
debug: 0  // Debug desabilitado (pode ser alterado para 1, 2 ou 3)
```

**Timeout de Conexão:**
- 15 segundos (15000ms)

**Peer ID Format:**
- `futstream_viewer_{random_number}` (número aleatório de 0-99999)

---

## 🔧 Como Ativar Mais Debug

### Para o Broadcaster (broadcast.html)

O debug já está no nível máximo (3). Para ver todos os logs:
1. Abra o Console do navegador (F12)
2. Filtre por "futstream" ou pelos emojis (🔗, 📞, ✅, ❌, etc.)

### Para o Viewer (watch.html)

Para ativar debug completo, altere a linha 55 de:
```javascript
debug: 0,
```

Para:
```javascript
debug: 3,
```

---

## 📊 Informações Técnicas da Stream

### Configurações de Vídeo (getDisplayMedia)
```javascript
video: {
    cursor: "always"  // Mostra o cursor sempre
}
```

### Configurações de Áudio do Sistema
```javascript
audio: {
    echoCancellation: false,
    noiseSuppression: false,
    sampleRate: 44100,
    channelCount: 2
}
```

### Configurações de Áudio do Microfone
```javascript
audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
}
```

---

## 🐛 Problemas Comuns e Como Diagnosticar

### 1. "Stream sem vídeo"
**Verificar:**
- Console: `📹 Video tracks: 0`
- Possível causa: Compartilhamento cancelado ou janela protegida (DRM)

### 2. "Conexão perdida"
**Verificar:**
- Console: `🔗 Connection State: failed` ou `disconnected`
- Console: `🧊 ICE State: failed` ou `disconnected`
- Possível causa: Problemas de rede ou firewall

### 3. "Host não respondeu (Timeout)"
**Verificar:**
- Console do broadcaster: Verificar se há `📞 Received call from {peer}`
- Possível causa: Broadcaster offline ou peer ID incorreto

### 4. Sem áudio
**Verificar:**
- Console do broadcaster: `🔊 Audio tracks: 0`
- Debug Info: Verificar número de audio tracks
- Possível causa: Áudio do sistema não compartilhado ou aplicação sem áudio

### 5. "Ao Vivo 🔇 (Clique para ativar áudio)"
**Verificar:**
- Console: `⚠️ Autoplay with audio prevented`
- Possível causa: Política de autoplay do navegador
- Solução: Clicar no vídeo para ativar o áudio

---

## 📝 Logs Importantes para Reportar Problemas

Se encontrar problemas, capture os seguintes logs:

**Do Broadcaster:**
1. Peer ID exibido
2. Debug Info (resolução, FPS, audio tracks)
3. Todos os logs do console com 📞, 🔗, 🧊
4. Mensagens de erro (❌)

**Do Viewer:**
1. Peer ID (console)
2. Host Peer ID tentado
3. Estados de conexão (🔗, 🧊)
4. Logs de stream recebido (📹, 🔊)
5. Mensagens de erro (❌)

---

## 🎯 Monitoramento em Tempo Real

### Atualização Automática
O broadcaster atualiza as informações de debug a cada **2 segundos** (2000ms) enquanto o stream está ativo.

### Informações Atualizadas
- Resolução atual
- FPS atual
- Estado dos tracks
- Sample rate do áudio
- Número de tracks ativos

---

## 🔍 Ferramentas de Debug do Navegador

### Chrome/Edge
1. F12 → Console (para logs)
2. F12 → Network → WS (para WebSocket/WebRTC)
3. chrome://webrtc-internals (para detalhes WebRTC)

### Firefox
1. F12 → Console
2. F12 → Network → WS
3. about:webrtc (para detalhes WebRTC)

---

**Data de criação:** 2025-11-23
**Versão:** 1.0
