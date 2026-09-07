const { chromium } = require('playwright');
const assert = require('node:assert/strict');

async function main() {
    const fixture = JSON.parse(process.env.FUTSTREAM_BROWSER_FIXTURE);
    const browser = await chromium.launch({headless: true, channel: 'chrome'});
    const errors = [];
    try {
        async function context(cookie) {
            const ctx = await browser.newContext();
            await ctx.addCookies([cookie]);
            // The entire workflow must work even when WebSockets are unavailable.
            await ctx.addInitScript(() => {
                window.WebSocket = class { constructor() { throw new Error('WebSocket is blocked in this test'); } };
            });
            return ctx;
        }
        const hostContext = await context(fixture.cookies[0]);
        const viewerContext = await context(fixture.cookies[1]);
        const host = await hostContext.newPage();
        host.on('pageerror', error => errors.push(error.message));
        await host.goto(fixture.baseURL + fixture.hostPath);
        await host.evaluate(() => {
            navigator.mediaDevices.getDisplayMedia = async () => {
                const canvas = document.createElement('canvas');
                canvas.width = 320; canvas.height = 180;
                const ctx = canvas.getContext('2d');
                let frame = 0;
                const timer = setInterval(() => {
                    ctx.fillStyle = frame++ % 2 ? '#ef3340' : '#00bb99';
                    ctx.fillRect(0, 0, 320, 180);
                    ctx.fillStyle = '#ffffff'; ctx.fillRect(20, 20, 80, 80);
                }, 100);
                const stream = canvas.captureStream(10);
                stream.getVideoTracks()[0].addEventListener('ended', () => clearInterval(timer));
                return stream;
            };
            navigator.mediaDevices.getUserMedia = async () => { throw new Error('No microphone needed'); };
        });
        await host.evaluate(() => startScreenShare());
        for (const [name, viewport] of [
            ['desktop', {width: 1366, height: 768}], ['mobile', {width: 390, height: 844}]
        ]) {
            const page = await viewerContext.newPage();
            page.on('pageerror', error => errors.push(error.message));
            await page.setViewportSize(viewport);
            await page.goto(fixture.baseURL + fixture.watchPath);
            await page.waitForFunction(() => {
                const video = document.getElementById('remoteVideo');
                return connection.connected && video.videoWidth === 320 && video.currentTime > 0;
            }, null, {timeout: 45000});
            const before = await page.evaluate(() => {
                const video = document.getElementById('remoteVideo');
                const canvas = document.createElement('canvas'); canvas.width = canvas.height = 8;
                const ctx = canvas.getContext('2d'); ctx.drawImage(video, 0, 0, 8, 8);
                return {id: video.srcObject.id, time: video.currentTime,
                    generation: [...connection.connections.values()][0].id,
                    colors: [...ctx.getImageData(0, 0, 8, 8).data].reduce((a, b) => a + b, 0)};
            });
            assert.ok(before.colors > 8 * 8 * 255);
            await page.route('**/streams/signal/**', route => route.abort());
            await page.waitForFunction(() => connection.networkFailures > 0);
            const interrupted = await page.evaluate(() => ({connected: connection.connected,
                id: videoEl.srcObject.id, time: videoEl.currentTime}));
            assert.equal(interrupted.connected, true);
            assert.equal(interrupted.id, before.id);
            assert.ok(interrupted.time > before.time);
            await page.unroute('**/streams/signal/**');
            await page.waitForFunction(() => connection.networkFailures === 0, null, {timeout: 20000});
            await page.evaluate(() => manualRetry());
            await page.waitForFunction(id => [...connection.connections.values()].some(entry => entry.id !== id && entry.connected)
                && videoEl.readyState >= 2 && videoEl.currentTime > 0,
                before.generation, {timeout: 45000});
            console.log(JSON.stringify({viewport: name, video: '320x180', websocketBlocked: true,
                playbackSurvivedHttpFailure: true, manualReconnect: true}));
            await page.close();
        }
        assert.deepEqual(errors, []);
    } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
