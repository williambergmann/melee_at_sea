// Board - Dot-grid game board for Melee at Sea
import { GRID_COLS, GRID_ROWS, CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, DOT_COLOR, BG_COLOR } from './constants.js';

export class Board {
    constructor(cols = GRID_COLS, rows = GRID_ROWS, cellSize = CELL_SIZE) {
        this.cols = cols;
        this.rows = rows;
        this.cellSize = cellSize;
        this.width = cols * cellSize;
        this.height = rows * cellSize;
        
        // Offset to center the grid on screen
        this.offsetX = 0;
        this.offsetY = 0;
        
        // Highlights for fire zones etc
        this.highlights = [];
    }
    
    setOffset(screenWidth, screenHeight) {
        this.offsetX = Math.floor((screenWidth - this.width) / 2);
        this.offsetY = Math.floor((screenHeight - this.height) / 2);
    }
    
    gridToScreen(gridX, gridY) {
        const screenX = this.offsetX + gridX * this.cellSize + this.cellSize / 2;
        const screenY = this.offsetY + gridY * this.cellSize + this.cellSize / 2;
        return { x: screenX, y: screenY };
    }
    
    screenToGrid(screenX, screenY) {
        const gridX = Math.floor((screenX - this.offsetX) / this.cellSize);
        const gridY = Math.floor((screenY - this.offsetY) / this.cellSize);
        return { x: gridX, y: gridY };
    }
    
    isValidCell(gridX, gridY) {
        return gridX >= 0 && gridX < this.cols && gridY >= 0 && gridY < this.rows;
    }
    
    clearHighlights() {
        this.highlights = [];
    }
    
    addHighlight(gridX, gridY, color, alpha = 0.4) {
        if (!this.isValidCell(gridX, gridY)) return;
        
        this.highlights.push({
            x: gridX,
            y: gridY,
            color: color,
            alpha: alpha
        });
    }
    
    render(ctx) {
        // Fill background
        ctx.fillStyle = BG_COLOR;
        ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
        
        // Draw highlights first (behind dots)
        for (const highlight of this.highlights) {
            const screenX = this.offsetX + highlight.x * this.cellSize;
            const screenY = this.offsetY + highlight.y * this.cellSize;
            
            ctx.fillStyle = highlight.color;
            ctx.globalAlpha = highlight.alpha;
            ctx.fillRect(screenX, screenY, this.cellSize, this.cellSize);
            ctx.globalAlpha = 1;
        }
        
        // Draw the dot grid
        ctx.fillStyle = DOT_COLOR;
        for (let row = 0; row <= this.rows; row++) {
            for (let col = 0; col <= this.cols; col++) {
                const x = this.offsetX + col * this.cellSize;
                const y = this.offsetY + row * this.cellSize;
                
                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
}
