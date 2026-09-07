const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const templates = path.resolve(__dirname, '../templates/streams');
function script(name) {
    return [...readFileSync(path.join(templates, name), 'utf8').matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)]
        .map(match => match[1]).join('\n');
}

class Timers {
    now = 0;
    nextId = 0;
    jobs = new Map();
    set = (fn, delay) => {
        const id = ++this.nextId;
        this.jobs.set(id, { fn, due: this.now + delay });
        return id;
    };
    clear = id => this.jobs.delete(id);
    advance(ms) {
        const end = this.now + ms;
        for (let count = 0; count < 1000; count++) {
            const next = [...this.jobs].filter(([, job]) => job.due <= end)
                .sort((a, b) => a[1].due - b[1].due)[0];
            if (!next) { this.now = end; return; }
            this.now = next[1].due;
            this.jobs.delete(next[0]);
            next[1].fn();
        }
        throw new Error('Unbounded timer loop');
    }
}

class FakePC {
    connectionState = 'new';
    iceConnectionState = 'new';
    listeners = new Map();
    addEventListener(name, callback) {
        if (!this.listeners.has(name)) this.listeners.set(name, []);
        this.listeners.get(name).push(callback);
    }
    fire(name, event = {}) {
        this['on' + name]?.(event);
        for (const listener of this.listeners.get(name) || []) listener(event);
    }
}

class FakeCall extends EventEmitter {
    constructor(stream) {
        super();
        this.peer = 'viewer';
        this.peerConnection = new FakePC();
        this.stream = stream;
        this.sentCandidates = [];
        this.closed = false;
        // Match the handlers installed by the pinned PeerJS 1.5.4 negotiator.
        this.peerConnection.onicecandidate = event => this.sentCandidates.push(event.candidate);
        const pc = this.peerConnection;
        pc.oniceconnectionstatechange = () => {
            if (pc.iceConnectionState === 'failed') {
                this.emit('error', { type: 'negotiation-failed' });
                this.close();
            }
        };
    }
    answer() {}
    close() {
        if (this.closed) return;
        this.closed = true;
        this.peerConnection = null;
        this.emit('close');
    }
}

class FakePeer extends EventEmitter {
    constructor(id, options) {
        super();
        Object.assign(this, { id, options, open: false, disconnected: false,
            destroyed: false, reconnects: 0, calls: [], data: [] });
    }
    connected() { this.open = true; this.disconnected = false; this.emit('open', this.id); }
    disconnect() { this.open = false; this.disconnected = true; this.emit('disconnected'); }
    reconnect() { this.reconnects++; this.disconnected = false; }
    destroy() { this.destroyed = true; this.disconnect(); this.calls.forEach(call => call.close()); }
    call(id, stream) {
        const call = new FakeCall(stream);
        call.policy = this.options.config.iceTransportPolicy;
        this.calls.push(call);
        return call;
    }
    connect() {
        const conn = new EventEmitter();
        conn.closed = false;
        conn.close = () => { conn.closed = true; };
        conn.send = () => {};
        this.data.push(conn);
        return conn;
    }
}

function element() {
    return { style: {}, children: [], innerText: '',
        appendChild(child) { this.children.push(child); },
        remove() {},
        querySelector() { return null; },
        play() { return Promise.resolve(); },
        captureStream() {
            const track = { stopped: false, stop() { this.stopped = true; } };
            return { getTracks: () => [track] };
        }
    };
}

function harness(page = 'watch.html') {
    const timers = new Timers();
    const elements = new Map();
    const window = new FakePC();
    const context = vm.createContext({
        console: { log() {}, warn() {}, error() {} }, Peer: FakePeer,
        setTimeout: timers.set, clearTimeout: timers.clear, window,
        document: {
            getElementById(id) {
                if (!elements.has(id)) elements.set(id, element());
                return elements.get(id);
            },
            createElement: element
        }
    });
    vm.runInContext(script('_peer_signaling.html') + script(page), context);
    return { context, timers, elements, window, peer: vm.runInContext('peer', context),
        run: code => vm.runInContext(code, context) };
}

test('viewer diagnostics preserve candidate forwarding and PeerJS ICE failure handler', () => {
    const h = harness();
    h.peer.connected();
    const call = h.peer.calls[0];
    const pc = call.peerConnection;
    const candidate = { type: 'srflx', protocol: 'udp' };
    pc.fire('icecandidate', { candidate });
    assert.deepEqual(call.sentCandidates, [candidate]);
    pc.iceConnectionState = 'failed';
    pc.fire('iceconnectionstatechange');
    assert.equal(call.closed, true);
    h.timers.advance(3000);
    assert.equal(h.peer.calls.length, 2);
});

test('healthy video survives signaling disconnect and reopen', () => {
    const h = harness();
    h.peer.connected();
    const call = h.peer.calls[0];
    call.peerConnection.connectionState = 'connected';
    call.peerConnection.iceConnectionState = 'connected';
    call.peerConnection.fire('connectionstatechange');
    h.elements.get('status').innerText = 'Live';
    h.peer.emit('error', { type: 'network', message: 'Lost connection to server.' });
    h.peer.disconnect();
    h.timers.advance(2000);
    assert.equal(h.peer.reconnects, 1);
    h.peer.connected();
    assert.equal(h.peer.calls.length, 1);
    assert.equal(call.closed, false);
    assert.equal(h.elements.get('status').innerText, 'Live');
});

test('duplicate network events use one bounded reconnect schedule even with short opens', () => {
    const h = harness('broadcast.html');
    h.peer.connected();
    for (let i = 0; i < 5; i++) {
        h.peer.emit('error', { type: 'network', message: 'Lost connection' });
        h.peer.disconnect();
        h.timers.advance(Math.min(2000 * (2 ** i), 15000));
        assert.equal(h.peer.reconnects, i + 1);
        h.peer.connected();
    }
    h.peer.disconnect();
    h.timers.advance(120000);
    assert.equal(h.peer.reconnects, 5);
    assert.match(h.elements.get('status').innerText, /indisponivel/);
});

test('a socket that never opens times out and exhausts automatic retries', () => {
    const h = harness();
    h.timers.advance(300000);
    assert.equal(h.peer.reconnects, 5);
    assert.equal(h.peer.calls.length, 0);
    assert.match(h.elements.get('status').innerText, /indisponivel/);
    assert.equal(h.timers.jobs.size, 0);
});

test('call failures are deduplicated, try relay, and stop after five retries', () => {
    const h = harness();
    h.peer.connected();
    for (let i = 0; i < 6; i++) {
        const call = h.peer.calls.at(-1);
        const pc = call.peerConnection;
        pc.connectionState = 'failed';
        pc.fire('connectionstatechange');
        pc.iceConnectionState = 'failed';
        pc.fire('iceconnectionstatechange');
        call.emit('close');
        h.timers.advance(3000);
    }
    assert.equal(h.peer.calls.length, 6);
    assert.equal(h.peer.calls[2].policy, 'relay');
    assert.equal(h.elements.get('retryBtn').style.display, 'inline-flex');
    h.run('manualRetry()');
    assert.equal(h.peer.calls.length, 7);
    assert.equal(h.peer.calls[6].policy, 'all');
});

test('remote stream metadata alone does not cancel the connection timeout', () => {
    const h = harness();
    h.peer.connected();
    h.peer.calls[0].emit('stream', {
        getAudioTracks: () => [], getVideoTracks: () => [{}], getTracks: () => []
    });
    h.timers.advance(23000);
    assert.equal(h.peer.calls.length, 2);
});

test('manual retry frees the previous canvas track and data connection', () => {
    const h = harness();
    h.peer.connected();
    const previous = h.peer.calls[0];
    h.run('manualRetry()');
    assert.equal(previous.stream.getTracks()[0].stopped, true);
    assert.equal(h.peer.data[0].closed, true);
    assert.equal(h.peer.calls.length, 2);
    const status = h.elements.get('status').innerText;
    previous.emit('close');
    assert.equal(h.elements.get('status').innerText, status);
});

test('closing the page cancels all retries and releases media', () => {
    const h = harness();
    h.peer.connected();
    h.peer.disconnect();
    h.window.fire('pagehide');
    h.timers.advance(300000);
    assert.equal(h.peer.reconnects, 0);
    assert.equal(h.peer.destroyed, true);
    assert.equal(h.peer.calls[0].stream.getTracks()[0].stopped, true);
    assert.equal(h.timers.jobs.size, 0);
});

test('broadcaster diagnostics preserve PeerJS ICE failure handling', () => {
    const h = harness('broadcast.html');
    h.run('localStream = {getVideoTracks: () => [{}], getAudioTracks: () => []}');
    const call = new FakeCall();
    const pc = call.peerConnection;
    h.peer.emit('call', call);
    assert.equal(typeof pc.oniceconnectionstatechange, 'function');
    pc.iceConnectionState = 'failed';
    assert.doesNotThrow(() => pc.fire('iceconnectionstatechange'));
    assert.equal(call.closed, true);
});

test('temporary media disconnection recovers without a replacement call', () => {
    const h = harness();
    h.peer.connected();
    const pc = h.peer.calls[0].peerConnection;
    pc.connectionState = 'disconnected';
    pc.fire('connectionstatechange');
    h.timers.advance(5000);
    pc.connectionState = 'connected';
    pc.fire('connectionstatechange');
    h.timers.advance(30000);
    assert.equal(h.peer.calls.length, 1);
});

test('persistent media disconnection starts a new call after the grace period', () => {
    const h = harness();
    h.peer.connected();
    const pc = h.peer.calls[0].peerConnection;
    pc.connectionState = 'disconnected';
    pc.fire('connectionstatechange');
    h.timers.advance(15000);
    assert.equal(h.peer.calls.length, 2);
});

test('socket diagnostics expose close codes without dumping signaling payloads', () => {
    const h = harness();
    const messages = [];
    const logger = h.run('createPeerLogger')(message => messages.push(message));
    logger(3, 'Socket closed.', { code: 1006, reason: '', wasClean: false });
    logger(3, 'Server message received:', { token: 'must-not-log' });
    assert.equal(messages.length, 1);
    assert.match(messages[0], /codigo=1006/);
    assert.doesNotMatch(messages[0], /must-not-log/);
});
