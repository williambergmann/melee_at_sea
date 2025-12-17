// Sound System - Web Audio API based 8-bit sound effects
export class SoundSystem {
    constructor() {
        this.audioContext = null;
        this.enabled = true;
        this.initialized = false;
    }
    
    init() {
        if (this.initialized) return;
        
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.initialized = true;
        } catch (e) {
            console.warn('Web Audio API not supported');
            this.enabled = false;
        }
    }
    
    play(soundName) {
        if (!this.enabled) return;
        if (!this.initialized) this.init();
        if (!this.audioContext) return;
        
        // Resume context if suspended (needed for user gesture requirement)
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
        
        switch (soundName) {
            case 'select':
                this.playTone(440, 0.1, 'square');
                break;
            case 'move':
                this.playTone(220, 0.1, 'triangle');
                break;
            case 'fire':
                this.playNoise(0.2);
                break;
            case 'hit':
                this.playTone(150, 0.15, 'sawtooth');
                break;
            case 'destroy':
                this.playExplosion();
                break;
        }
    }
    
    playTone(frequency, duration, type = 'square') {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.type = type;
        oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
        
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + duration);
    }
    
    playNoise(duration) {
        const bufferSize = this.audioContext.sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, bufferSize, this.audioContext.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        const source = this.audioContext.createBufferSource();
        const gainNode = this.audioContext.createGain();
        
        source.buffer = buffer;
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
        
        source.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        source.start();
    }
    
    playExplosion() {
        // Low rumble + noise
        this.playTone(80, 0.3, 'sawtooth');
        this.playNoise(0.3);
        
        // Descending tones
        setTimeout(() => this.playTone(60, 0.2, 'square'), 100);
        setTimeout(() => this.playTone(40, 0.2, 'square'), 200);
    }
    
    playTheme() {
        // Simple 8-bit melody (optional - can be expanded)
        if (!this.enabled) return;
        if (!this.initialized) this.init();
    }
    
    stopTheme() {
        // Stop theme if playing
    }
}
