/* global SimplePeer */
class HttpStream {
    constructor(config, callbacks) {
        this.config = config;
        this.callbacks = callbacks;
        this.id = crypto.randomUUID();
        this.cursor = 0;
        this.outbox = [];
        this.connections = new Map();
        this.failures = new Map();
        this.cooldowns = new Map();
        this.participants = [];
        this.stream = null;
        this.timer = null;
        this.controller = null;
        this.stopped = false;
        this.paused = false;
        this.networkFailures = 0;
        this.csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    log(message) { this.callbacks.log(message); }
    get connected() { return [...this.connections.values()].some(entry => entry.connected); }

    start() {
        this.log('FutStream HTTPS v3: sinalizacao no proprio site, sem PeerJS/WebSocket');
        this.schedule(0);
    }

    schedule(delay = 2000) {
        if (this.stopped || this.paused) return;
        clearTimeout(this.timer);
        this.timer = setTimeout(() => this.sync(), delay);
    }

    queue(to, connectionId, signal) {
        if (this.stopped) return;
        this.outbox.push({id: crypto.randomUUID(), to, connection_id: connectionId, signal});
        if (!this.controller) this.schedule(50);
    }

    async sync() {
        if (this.stopped || this.paused || this.controller) return;
        const controller = new AbortController();
        this.controller = controller;
        const timeout = setTimeout(() => controller.abort(), 15000);
        let delay = 2000;
        try {
            const response = await fetch(this.config.endpoint, {
                method: 'POST', credentials: 'same-origin', cache: 'no-store',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': this.csrf},
                signal: controller.signal,
                body: JSON.stringify({client_id: this.id, role: this.config.role,
                    cursor: this.cursor, ready: this.config.role === 'viewer' || !!this.stream,
                    messages: this.outbox.slice(0, 64)})
            });
            if (this.stopped) return;
            if (!response.ok || response.redirected) {
                let message = `Falha na sinalizacao HTTPS (${response.status})`;
                const body = await response.json().catch(() => null);
                if (body?.error) message = body.error;
                if ([401, 403, 404, 410].includes(response.status) || response.redirected) this.paused = true;
                throw new Error(message);
            }
            const body = await response.json();
            if (this.stopped) return;
            this.networkFailures = 0;
            const accepted = new Set(body.accepted);
            this.outbox = this.outbox.filter(message => !accepted.has(message.id));
            this.participants = body.participants;
            this.reconcile();
            for (const message of body.messages) this.receive(message);
            this.cursor = body.cursor;
            if (this.outbox.length) delay = 50;
        } catch (error) {
            if (this.stopped) return;
            this.networkFailures++;
            this.log(error.message);
            if (this.networkFailures >= 5) this.paused = true;
            this.callbacks.status(this.paused ? error.message : 'Reconectando ao site...', this.connected);
            delay = Math.min(2000 * (2 ** this.networkFailures), 15000);
        } finally {
            clearTimeout(timeout);
            this.controller = null;
            this.schedule(delay);
        }
    }

    reconcile() {
        const active = new Set(this.participants.filter(item => item.ready).map(item => item.id));
        for (const [id] of this.connections) {
            if (!active.has(id)) this.drop(id, false);
        }
        if (this.config.role === 'host') {
            if (!this.stream) return;
            for (const remote of this.participants) {
                if (remote.ready && !this.connections.has(remote.id) &&
                    (this.failures.get(remote.id) || 0) < 5 &&
                    (this.cooldowns.get(remote.id) || 0) <= Date.now()) {
                    this.createPeer(remote.id, crypto.randomUUID(), true);
                }
            }
        } else if (!this.connected) {
            this.callbacks.status(active.size ? 'Conectando video...' : 'Aguardando o transmissor...', false);
        }
    }

    createPeer(remoteId, connectionId, initiator) {
        const failures = this.failures.get(remoteId) || 0;
        const peer = new SimplePeer({
            initiator, stream: initiator ? this.stream : undefined,
            trickle: true,
            config: {iceServers: this.config.iceServers, iceTransportPolicy: failures >= 2 ? 'relay' : 'all'}
        });
        const entry = {peer, id: connectionId, connected: false, timeout: null, stableTimer: null};
        this.connections.set(remoteId, entry);
        this.log(`Negociando video por HTTPS; tentativa=${failures + 1}; relay=${failures >= 2}`);
        peer.on('signal', signal => {
            if (this.connections.get(remoteId) === entry) this.queue(remoteId, connectionId, signal);
        });
        peer.on('stream', stream => {
            if (this.connections.get(remoteId) === entry) this.callbacks.stream?.(stream);
        });
        peer.on('connect', () => {
            if (this.connections.get(remoteId) !== entry) return;
            entry.connected = true;
            clearTimeout(entry.timeout);
            entry.stableTimer = setTimeout(() => this.failures.delete(remoteId), 30000);
            this.log('Video conectado');
            this.updateViewers();
        });
        peer.on('error', error => {
            this.log(`WebRTC: ${error.code || error.message}`);
            if (this.connections.get(remoteId) === entry) this.drop(remoteId, true);
        });
        peer.on('close', () => {
            if (this.connections.get(remoteId) === entry) this.drop(remoteId, true);
        });
        entry.timeout = setTimeout(() => {
            if (this.connections.get(remoteId) === entry && !entry.connected) this.drop(remoteId, true);
        }, 30000);
        return entry;
    }

    receive(message) {
        if (!this.participants.some(item => item.id === message.from && item.ready)) return;
        let entry = this.connections.get(message.from);
        if (message.signal.type === 'retry' && this.config.role === 'host') {
            this.drop(message.from, false);
            this.failures.delete(message.from);
            this.cooldowns.delete(message.from);
            return;
        }
        if (message.signal.type === 'reset') {
            if (entry?.id === message.connection_id) this.drop(message.from, true);
            return;
        }
        if (this.config.role === 'viewer' && message.signal.type === 'offer' && entry?.id !== message.connection_id) {
            this.drop(message.from, false);
            entry = this.createPeer(message.from, message.connection_id, false);
        }
        if (!entry || entry.id !== message.connection_id) return;
        try { entry.peer.signal(message.signal); }
        catch (error) { this.log(error.message); this.drop(message.from, true); }
    }

    drop(remoteId, retry) {
        const entry = this.connections.get(remoteId);
        if (!entry) return;
        this.connections.delete(remoteId);
        clearTimeout(entry.timeout);
        clearTimeout(entry.stableTimer);
        entry.peer.destroy();
        this.outbox = this.outbox.filter(message => message.connection_id !== entry.id);
        if (retry && !this.stopped) {
            const failures = (this.failures.get(remoteId) || 0) + 1;
            this.failures.set(remoteId, failures);
            this.cooldowns.set(remoteId, Date.now() + Math.min(2000 * failures, 10000));
            if (this.config.role === 'viewer') this.queue(remoteId, entry.id, {type: 'reset'});
            this.log(`Conexao de video encerrada; falhas=${failures}/5`);
            this.callbacks.status(failures >= 5 ? 'Nao foi possivel conectar o video' : 'Reconectando video...', this.connected);
        }
        this.updateViewers();
    }

    updateViewers() {
        this.callbacks.viewers?.(this.participants.filter(item => this.connections.get(item.id)?.connected));
    }

    setStream(stream) {
        for (const [id] of this.connections) this.drop(id, false);
        this.stream = stream;
        this.failures.clear();
        this.cooldowns.clear();
        this.schedule(0);
    }

    retry() {
        this.paused = false;
        this.networkFailures = 0;
        this.failures.clear();
        this.cooldowns.clear();
        for (const [id] of this.connections) this.drop(id, false);
        if (this.config.role === 'viewer') {
            for (const remote of this.participants) this.queue(remote.id, crypto.randomUUID(), {type: 'retry'});
        }
        this.schedule(0);
    }

    stop() {
        if (this.stopped) return;
        this.stopped = true;
        clearTimeout(this.timer);
        this.controller?.abort();
        for (const [id] of this.connections) this.drop(id, false);
        fetch(this.config.endpoint, {
            method: 'POST', credentials: 'same-origin', keepalive: true,
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': this.csrf},
            body: JSON.stringify({client_id: this.id, role: this.config.role, leave: true})
        }).catch(() => {});
    }
}
window.HttpStream = HttpStream;
