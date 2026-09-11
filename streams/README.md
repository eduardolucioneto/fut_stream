# Transmissão LiveKit (SFU)

A mídia não é mais negociada pelo Django nem distribuída P2P. Cada transmissão usa a sala
`meusports-stream-<id>` no LiveKit: o transmissor publica tela, áudio da tela e microfone uma
única vez; o SFU entrega as faixas aos espectadores.

Django continua responsável por autenticação e autorização. Ao abrir a página, ele emite um JWT
LiveKit de curta duração, específico para a sala e para a aba atual. O transmissor só pode publicar
`screen_share`, `screen_share_audio` e `microphone`; espectadores recebem um token sem permissão de
publicação. A chave secreta do LiveKit nunca chega ao navegador.

## Variáveis de ambiente

Configure no Render (ou no host Django):

- `LIVEKIT_URL`: URL WebSocket pública do VPS, por exemplo `wss://live.seudominio.com`.
- `LIVEKIT_API_KEY`: API key configurada no LiveKit.
- `LIVEKIT_API_SECRET`: secret correspondente à API key.
- `LIVEKIT_TOKEN_TTL_HOURS`: opcional; padrão de 12 horas.

O VPS precisa expor corretamente o WebSocket e as portas UDP/TCP do LiveKit. TURN continua sendo
configurado no próprio servidor LiveKit quando a rede do usuário exigir relay; não há credenciais
TURN no frontend Django.

## Deploy e verificação

```powershell
python -m pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py test streams --noinput
```

Abra a página do transmissor, escolha a tela/aba e, em outra conta, abra a página de espectador.
O upload do transmissor permanece uma única publicação para o LiveKit, independentemente do número
de espectadores.

Os arquivos e tabelas de sinalização HTTP legados foram preservados apenas para compatibilidade de
migrations e histórico; as páginas de transmissão não os carregam nem os usam.