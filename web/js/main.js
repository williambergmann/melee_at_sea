// Main entry point for Melee at Sea
import { Game } from './game.js';
import { SCREEN_WIDTH, SCREEN_HEIGHT } from './constants.js';

// ES modules are deferred by default, so DOM is already ready
const canvas = document.getElementById('game-canvas');

if (!canvas) {
    console.error('Canvas element not found!');
} else {
    // Set canvas size
    canvas.width = SCREEN_WIDTH;
    canvas.height = SCREEN_HEIGHT;
    
    // Create and start game
    const game = new Game(canvas);
    game.start();
    
    console.log('Melee at Sea - Web Edition loaded!');
}
