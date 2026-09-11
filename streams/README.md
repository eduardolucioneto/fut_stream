# Transmissao por WebRTC com sinalizacao HTTPS

O transmissor e os espectadores trocam ofertas, respostas e candidatos ICE em
`POST /streams/signal/<stream_id>/`, no mesmo Django que serve a pagina. Nao ha
conexao WebSocket com o PeerJS publico. O video continua P2P: ele nao passa pelo
processo Django. O upload do transmissor ainda cresce com o numero de espectadores.

O cliente faz uma consulta a cada dois segundos e antecipa a consulta quando ha
mensagens de negociacao. Uma falha HTTP nao encerra video ja conectado. Tentativas
automaticas sao limitadas; o botao Reconectar permite uma nova tentativa manual.

Cada aba recebe um UUID associado ao usuario, sala e papel. Somente o dono da sala
pode anunciar um transmissor. As mensagens exigem sessao autenticada e CSRF. O
servidor entrega mensagens somente entre transmissor e espectador da mesma sala.
IDs de mensagens confirmadas permanecem por cinco minutos para deduplicar respostas
HTTP perdidas. Participantes sem heartbeat por tres minutos deixam de ser anunciados.

## Deploy no Render

- Usar `./build.sh` como Build Command. Ele aplica migrations e coleta os estaticos.
- A migration `streams.0002_http_signaling` cria duas tabelas, sem remover dados existentes.
- O Procfile tambem aplica migrations antes de iniciar o Gunicorn.
- Se o Render usa comandos personalizados, incluir `python manage.py migrate --no-input`
  e `python manage.py collectstatic --no-input` no fluxo de deploy.
- Depois do deploy, recarregar as duas paginas e iniciar novamente o compartilhamento.
- O painel DEBUG do espectador deve mostrar `FutStream HTTPS v3`.

## Redes que precisam de TURN

Sinalizacao HTTPS e transporte de video sao etapas diferentes. Redes que impedem
conexao P2P ainda precisam de um TURN acessivel. Sem as variaveis abaixo, somente STUN e usado.
Crie credenciais TURN no seu provedor e configure no Render:

- `STREAM_TURN_URLS`: `turn:global.relay.metered.ca:80,turn:global.relay.metered.ca:80?transport=tcp,turn:global.relay.metered.ca:443,turns:global.relay.metered.ca:443?transport=tcp`
- `STREAM_TURN_USERNAME`: usuario TURN.
- `STREAM_TURN_CREDENTIAL`: credencial TURN.

As credenciais TURN sao enviadas aos clientes autenticados para criar a conexao
WebRTC. Nao usar uma chave administrativa do provedor nesses campos.

## Verificacao

```powershell
$env:DATABASE_URL = 'sqlite:///:memory:'
python manage.py test streams --noinput
node --test streams/js_tests/http-stream.test.cjs
```

O teste opcional de navegador exige Node, Playwright e Chrome. Configurar `NODE_PATH`
caso Playwright nao esteja instalado no caminho padrao do Node:

```powershell
$env:FUTSTREAM_BROWSER_TEST = '1'
python manage.py test streams --noinput
```

Ele usa um banco de testes, um Django temporario e video sintetico. Testa dois
tamanhos de tela, WebSockets bloqueados, perda de HTTP e reconexao manual. Nao usa
contas, sessoes ou capturas de tela reais do usuario.

## Biblioteca

`static/streams/vendor/simplepeer-9.11.1.min.js` e a distribuicao standalone oficial
de simple-peer 9.11.1, obtida de
https://unpkg.com/simple-peer@9.11.1/simplepeer.min.js . A licenca MIT esta em
`static/streams/vendor/simple-peer.LICENSE`.

SHA-256: `de8330796ae774276491ac796aed42ea0141cdef43e46e90dedd2499a5d1b3e1`.
