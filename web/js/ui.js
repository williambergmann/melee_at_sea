// UI - DOS-style user interface elements
import { SCREEN_WIDTH, SCREEN_HEIGHT, COLORS } from './constants.js';

export class UI {
    constructor(screenWidth = SCREEN_WIDTH, screenHeight = SCREEN_HEIGHT) {
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
    }
    
    renderTurnIndicator(ctx, isPlayerTurn, state = '') {
        let text, color;
        
        if (isPlayerTurn) {
            text = 'YOUR TURN';
            if (state) text += ` - ${state}`;
            color = COLORS.player;
        } else {
            text = 'ENEMY TURN';
            color = COLORS.enemy;
        }
        
        ctx.font = 'bold 28px "Courier New", monospace';
        ctx.fillStyle = color;
        ctx.textAlign = 'center';
        ctx.fillText(text, this.screenWidth / 2, 30);
    }
    
    renderTurnIndicator2P(ctx, currentPlayer, state = '') {
        let text, color;
        
        if (currentPlayer === 1) {
            text = "PLAYER 1's TURN";
            color = COLORS.player;
        } else {
            text = "PLAYER 2's TURN";
            color = COLORS.enemy;
        }
        
        if (state) text += ` - ${state}`;
        
        ctx.font = 'bold 28px "Courier New", monospace';
        ctx.fillStyle = color;
        ctx.textAlign = 'center';
        ctx.fillText(text, this.screenWidth / 2, 30);
    }
    
    renderInstructions(ctx, instructions) {
        const text = instructions.join(' | ');
        
        ctx.font = '14px "Courier New", monospace';
        ctx.fillStyle = COLORS.textDim;
        ctx.textAlign = 'center';
        ctx.fillText(text, this.screenWidth / 2, this.screenHeight - 10);
    }
    
    renderShipInfo(ctx, ship, x, y) {
        if (!ship) return;
        
        // Background panel
        ctx.fillStyle = COLORS.panel;
        ctx.fillRect(x, y, 160, 90);
        
        ctx.strokeStyle = 'rgb(150, 150, 150)';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, 160, 90);
        
        // Ship info
        const teamText = ship.team === 'player' ? 'YOUR SHIP' : 'ENEMY SHIP';
        const teamColor = ship.team === 'player' ? COLORS.player : COLORS.enemy;
        
        ctx.font = '14px "Courier New", monospace';
        ctx.fillStyle = teamColor;
        ctx.textAlign = 'left';
        ctx.fillText(teamText, x + 10, y + 20);
        
        // Cannon display
        const filledCannons = '█'.repeat(ship.cannonsPerSide);
        const emptyCannons = '░'.repeat(ship.maxCannonsPerSide - ship.cannonsPerSide);
        const cannonText = `Cannons: ${filledCannons}${emptyCannons}`;
        
        ctx.fillStyle = COLORS.text;
        ctx.fillText(cannonText, x + 10, y + 45);
        
        // Status
        const statusParts = [];
        if (ship.hasMoved) statusParts.push('Moved');
        if (ship.hasFired) statusParts.push('Fired');
        
        if (statusParts.length > 0) {
            ctx.fillStyle = COLORS.textDim;
            ctx.fillText(statusParts.join(', '), x + 10, y + 70);
        }
    }
    
    renderGameOver(ctx, playerWon) {
        // Darken overlay
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, this.screenWidth, this.screenHeight);
        
        // Victory/Defeat text
        let text, color, subtext;
        if (playerWon) {
            text = 'VICTORY!';
            color = COLORS.player;
            subtext = 'All enemy ships destroyed!';
        } else {
            text = 'DEFEAT!';
            color = COLORS.enemy;
            subtext = 'Your fleet has been destroyed!';
        }
        
        ctx.font = 'bold 48px "Courier New", monospace';
        ctx.fillStyle = color;
        ctx.textAlign = 'center';
        ctx.fillText(text, this.screenWidth / 2, this.screenHeight / 2 - 20);
        
        ctx.font = '24px "Courier New", monospace';
        ctx.fillStyle = COLORS.text;
        ctx.fillText(subtext, this.screenWidth / 2, this.screenHeight / 2 + 30);
        
        ctx.font = '16px "Courier New", monospace';
        ctx.fillStyle = COLORS.textDim;
        ctx.fillText('Press R to restart or ESC to quit', this.screenWidth / 2, this.screenHeight / 2 + 80);
    }
    
    renderMessage(ctx, message) {
        if (!message) return;
        
        const textWidth = message.length * 12 + 40;
        const x = (this.screenWidth - textWidth) / 2;
        const y = this.screenHeight / 2 - 20;
        
        // Background
        ctx.fillStyle = COLORS.panel;
        ctx.fillRect(x, y, textWidth, 40);
        
        ctx.strokeStyle = COLORS.highlight;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, textWidth, 40);
        
        // Text
        ctx.font = 'bold 20px "Courier New", monospace';
        ctx.fillStyle = COLORS.highlight;
        ctx.textAlign = 'center';
        ctx.fillText(message, this.screenWidth / 2, y + 26);
    }
}
