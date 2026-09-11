/* global LivekitClient */
class LiveKitStream {
    constructor(config, callbacks = {}) {
        this.config = config;
        this.callbacks = callbacks;
        this.room = null;
        this.publishedTracks = [];
    }
    status(message) { this.callbacks.status?.(message); }
    async connect() {
        if (this.room) return this.room;
        if (!window.LivekitClient) throw new Error('A biblioteca LiveKit não foi carregada.');
        const { Room, RoomEvent } = window.LivekitClient;
        const room = new Room({ adaptiveStream: true, dynacast: true });
        room.on(RoomEvent.ConnectionStateChanged, state => this.status(state === 'connected' ? 'Conectado ao servidor de vídeo' : 'Conexão: ' + state));
        room.on(RoomEvent.Disconnected, () => this.status('Transmissão desconectada'));
        room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => this.callbacks.trackSubscribed?.(track, publication, participant));
        room.on(RoomEvent.TrackUnsubscribed, track => this.callbacks.trackUnsubscribed?.(track));
        room.on(RoomEvent.ParticipantConnected, participant => this.callbacks.participantConnected?.(participant));
        room.on(RoomEvent.ParticipantDisconnected, participant => this.callbacks.participantDisconnected?.(participant));
        await room.connect(this.config.url, this.config.token);
        this.room = room;
        return room;
    }
    async publish(stream, microphoneTracks = []) {
        const room = await this.connect();
        await this.unpublish();
        for (const track of stream.getTracks()) {
            const source = track.kind === 'video' ? LivekitClient.Track.Source.ScreenShare : LivekitClient.Track.Source.ScreenShareAudio;
            await room.localParticipant.publishTrack(track, { source, simulcast: track.kind === 'video' });
            this.publishedTracks.push(track);
        }
        for (const track of microphoneTracks) {
            await room.localParticipant.publishTrack(track, { source: LivekitClient.Track.Source.Microphone });
            this.publishedTracks.push(track);
        }
    }
    async unpublish() {
        if (!this.room) return;
        for (const track of this.publishedTracks) await this.room.localParticipant.unpublishTrack(track);
        this.publishedTracks = [];
    }
    async disconnect() {
        await this.unpublish();
        this.room?.disconnect();
        this.room = null;
    }
}
window.LiveKitStream = LiveKitStream;