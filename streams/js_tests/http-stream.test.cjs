const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const { randomUUID } = require('node:crypto');
const test = require('node:test');
const vm = require('node:vm');

class FakePeer extends EventEmitter {
    constructor(options) { super(); this.options = options; this.signals = []; }
    signal(data) { this.signals.push(data); }
    destroy() { this.destroyed = true; this.emit('close'); }
}
function harness(role = 'host', fetch = async () => { throw new Error('offline'); }) {
    let timerId = 0;
    const timers = new Map();
    const context = vm.createContext({window: {}, SimplePeer: FakePeer,
        crypto: {randomUUID}, AbortController, fetch,
        document: {querySelector: () => ({value: 'test-csrf'})},
        setTimeout: (fn, delay) => { timers.set(++timerId, {fn, delay}); return timerId; },
        clearTimeout: id => timers.delete(id)});
    vm.runInContext(readFileSync(path.resolve(__dirname, '../static/streams/http-stream.js'), 'utf8'), context);
    const stream = new context.window.HttpStream({role, endpoint: '/signal/', iceServers: []},
        {log() {}, status() {}, viewers() {}, stream() {}});
    stream.stream = {};
    stream.participants = [{id: 'remote', ready: true}];
    return {stream, timers};
}

test('network errors retain message IDs for idempotent retry and preserve connected video', async () => {
    let calls = 0;
    let sentId;
    const {stream} = harness('host', async (url, options) => {
        const body = JSON.parse(options.body);
        if (!calls++) { sentId = body.messages[0].id; throw new Error('Response lost'); }
        assert.equal(body.messages[0].id, sentId);
        return {ok: true, json: async () => ({accepted: [sentId], participants: [{id: 'remote', ready: true}], messages: [], cursor: 0})};
    });
    const entry = stream.createPeer('remote', 'generation', true);
    entry.peer.emit('connect');
    stream.queue('remote', 'generation', {type: 'offer', sdp: 'v=0'});
    await stream.sync();
    assert.equal(stream.outbox.length, 1);
    assert.equal(stream.connected, true);
    await stream.sync();
    assert.equal(stream.outbox.length, 0);
    assert.equal(stream.connections.get('remote'), entry);
});

test('only one HTTPS exchange can be in flight', async () => {
    let finish;
    let calls = 0;
    const {stream} = harness('viewer', () => { calls++; return new Promise(resolve => { finish = resolve; }); });
    const pending = stream.sync();
    await stream.sync();
    assert.equal(calls, 1);
    finish({ok: true, json: async () => ({accepted: [], participants: [], messages: [], cursor: 0})});
    await pending;
});

test('network retries are bounded without destroying established media', async () => {
    const {stream} = harness();
    const entry = stream.createPeer('remote', 'generation', true);
    entry.peer.emit('connect');
    for (let i = 0; i < 5; i++) await stream.sync();
    assert.equal(stream.paused, true);
    assert.equal(stream.networkFailures, 5);
    assert.equal(entry.peer.destroyed, undefined);
});

test('late HTTPS response after page close cannot create another connection', async () => {
    let finish;
    const {stream} = harness('host', (url, options) => {
        if (options.keepalive) return Promise.resolve({ok: true});
        return new Promise(resolve => { finish = resolve; });
    });
    const pending = stream.sync();
    stream.stop();
    finish({ok: true, json: async () => ({accepted: [], participants: [{id: 'remote', ready: true}], messages: [], cursor: 0})});
    await pending;
    assert.equal(stream.connections.size, 0);
});

test('error and close events count as one failed attempt, with relay after two failures', () => {
    const {stream} = harness();
    for (let i = 0; i < 5; i++) {
        stream.cooldowns.clear();
        stream.reconcile();
        const entry = stream.connections.get('remote');
        assert.equal(entry.peer.options.config.iceTransportPolicy, i >= 2 ? 'relay' : 'all');
        entry.peer.emit('error', new Error('failed'));
        entry.peer.emit('close');
        assert.equal(stream.failures.get('remote'), i + 1);
    }
    stream.cooldowns.clear();
    stream.reconcile();
    assert.equal(stream.connections.size, 0);
});

test('stale ICE or reset messages cannot affect a replacement call', () => {
    const {stream} = harness('viewer');
    stream.receive({from: 'remote', connection_id: 'first', signal: {type: 'offer', sdp: 'first'}});
    stream.receive({from: 'remote', connection_id: 'second', signal: {type: 'offer', sdp: 'second'}});
    const current = stream.connections.get('remote');
    stream.receive({from: 'remote', connection_id: 'first', signal: {candidate: {candidate: 'stale'}}});
    stream.receive({from: 'remote', connection_id: 'first', signal: {type: 'reset'}});
    assert.equal(stream.connections.get('remote'), current);
    assert.equal(current.peer.signals.length, 1);
});

test('manual viewer retry asks the host for a new call without replacing the HTTP session', () => {
    const {stream} = harness('viewer');
    const id = stream.id;
    stream.paused = true;
    stream.networkFailures = 5;
    stream.retry();
    assert.equal(stream.id, id);
    assert.equal(stream.paused, false);
    assert.equal(stream.outbox[0].signal.type, 'retry');
});
