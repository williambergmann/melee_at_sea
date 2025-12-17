// Ship - Warship entity for Melee at Sea
import { UP, RIGHT, DOWN, LEFT, DIRECTION_VECTORS, COLORS } from './constants.js';

export class Ship {
    constructor(x, y, length, orientation, team, board) {
        this.x = x;
        this.y = y;
        this.length = length;
        this.maxLength = length;
        this.orientation = orientation;
        this.team = team;
        this.board = board;
        this.selected = false;
        this.hasMoved = false;
        this.hasFired = false;
        
        // Cannons per side based on length: L2=1, L3=2, L4=3
        this.maxCannonsPerSide = length - 1;
        this.cannonsPerSide = this.maxCannonsPerSide;
    }
    
    get isAlive() {
        return this.cannonsPerSide > 0;
    }
    
    get totalCannons() {
        return this.cannonsPerSide * 2;
    }
    
    getCells() {
        const cells = [];
        const dir = DIRECTION_VECTORS[this.orientation];
        
        // Ship extends backwards from the bow position
        for (let i = 0; i < this.length; i++) {
            const cellX = this.x - dir.dx * i;
            const cellY = this.y - dir.dy * i;
            cells.push({ x: cellX, y: cellY });
        }
        
        return cells;
    }
    
    getFireZones(maxRange = 3) {
        const fireCells = [];
        const shipCells = this.getCells();
        
        // Get perpendicular directions
        let perpDirs;
        if (this.orientation === UP || this.orientation === DOWN) {
            perpDirs = [{ dx: 1, dy: 0 }, { dx: -1, dy: 0 }];
        } else {
            perpDirs = [{ dx: 0, dy: 1 }, { dx: 0, dy: -1 }];
        }
        
        for (const cell of shipCells) {
            for (const pdir of perpDirs) {
                for (let distance = 1; distance <= maxRange; distance++) {
                    const fireX = cell.x + pdir.dx * distance;
                    const fireY = cell.y + pdir.dy * distance;
                    
                    if (this.board.isValidCell(fireX, fireY)) {
                        const exists = fireCells.some(c => c.x === fireX && c.y === fireY);
                        if (!exists) {
                            fireCells.push({ x: fireX, y: fireY });
                        }
                    }
                }
            }
        }
        
        return fireCells;
    }
    
    canOccupy(cells, allShips) {
        // Check all cells are valid
        for (const cell of cells) {
            if (!this.board.isValidCell(cell.x, cell.y)) {
                return false;
            }
        }
        
        // Check for collisions with other ships
        for (const ship of allShips) {
            if (ship === this || !ship.isAlive) continue;
            
            const otherCells = ship.getCells();
            for (const cell of cells) {
                for (const other of otherCells) {
                    if (cell.x === other.x && cell.y === other.y) {
                        return false;
                    }
                }
            }
        }
        
        return true;
    }
    
    getCellsAt(newX, newY, newOrientation = null) {
        if (newOrientation === null) {
            newOrientation = this.orientation;
        }
        
        const cells = [];
        const dir = DIRECTION_VECTORS[newOrientation];
        
        for (let i = 0; i < this.length; i++) {
            const cellX = newX - dir.dx * i;
            const cellY = newY - dir.dy * i;
            cells.push({ x: cellX, y: cellY });
        }
        
        return cells;
    }
    
    canMoveTo(newX, newY, allShips) {
        const newCells = this.getCellsAt(newX, newY);
        return this.canOccupy(newCells, allShips);
    }
    
    move(direction, allShips) {
        let dx = 0, dy = 0;
        const dir = DIRECTION_VECTORS[this.orientation];
        
        if (direction === 'forward') {
            dx = dir.dx;
            dy = dir.dy;
        } else if (direction === 'backward') {
            dx = -dir.dx;
            dy = -dir.dy;
        }
        
        const newX = this.x + dx;
        const newY = this.y + dy;
        
        if (this.canMoveTo(newX, newY, allShips)) {
            this.x = newX;
            this.y = newY;
            return true;
        }
        return false;
    }
    
    canRotateTo(newOrientation, allShips) {
        const newCells = this.getCellsAt(this.x, this.y, newOrientation);
        return this.canOccupy(newCells, allShips);
    }
    
    rotate(direction, allShips) {
        let newOrientation;
        if (direction === 'cw') {
            newOrientation = (this.orientation + 90) % 360;
        } else {
            newOrientation = (this.orientation - 90 + 360) % 360;
        }
        
        if (this.canRotateTo(newOrientation, allShips)) {
            this.orientation = newOrientation;
            return true;
        }
        return false;
    }
    
    takeDamage(amount = 1) {
        this.cannonsPerSide = Math.max(0, this.cannonsPerSide - amount);
        return this.cannonsPerSide <= 0; // Returns true if ship is destroyed
    }
    
    render(ctx) {
        if (!this.isAlive) return;
        
        const color = this.team === 'player' ? COLORS.player : COLORS.enemy;
        const cells = this.getCells();
        const cellSize = this.board.cellSize;
        
        // Determine which segments get cannons
        const bodySegments = cells.length - 1;
        const cannonPositions = [];
        if (this.cannonsPerSide > 0 && bodySegments > 0) {
            for (let c = 0; c < Math.min(this.cannonsPerSide, bodySegments); c++) {
                cannonPositions.push(1 + c);
            }
        }
        
        // Ship dimensions
        const bodyWidth = cellSize * 0.6;
        const cannonLength = cellSize * 0.4;
        const cannonThickness = cellSize * 0.15;
        
        for (let i = 0; i < cells.length; i++) {
            const cell = cells[i];
            const screen = this.board.gridToScreen(cell.x, cell.y);
            
            if (this.orientation === UP || this.orientation === DOWN) {
                // Vertical ship
                const halfWidth = bodyWidth / 2;
                const segmentHeight = cellSize * 0.9;
                
                if (i === 0) {
                    // Bow (pointed triangle)
                    ctx.fillStyle = color;
                    ctx.beginPath();
                    if (this.orientation === UP) {
                        ctx.moveTo(screen.x, screen.y - segmentHeight / 2);
                        ctx.lineTo(screen.x - halfWidth, screen.y + segmentHeight / 3);
                        ctx.lineTo(screen.x + halfWidth, screen.y + segmentHeight / 3);
                    } else {
                        ctx.moveTo(screen.x, screen.y + segmentHeight / 2);
                        ctx.lineTo(screen.x - halfWidth, screen.y - segmentHeight / 3);
                        ctx.lineTo(screen.x + halfWidth, screen.y - segmentHeight / 3);
                    }
                    ctx.closePath();
                    ctx.fill();
                } else {
                    // Body segment
                    ctx.fillStyle = color;
                    ctx.fillRect(
                        screen.x - halfWidth,
                        screen.y - segmentHeight / 2,
                        bodyWidth,
                        segmentHeight
                    );
                }
                
                // Cannons
                if (cannonPositions.includes(i)) {
                    ctx.fillStyle = COLORS.cannon;
                    // Left cannon
                    ctx.fillRect(
                        screen.x - halfWidth - cannonLength,
                        screen.y - cannonThickness / 2,
                        cannonLength,
                        cannonThickness
                    );
                    // Right cannon
                    ctx.fillRect(
                        screen.x + halfWidth,
                        screen.y - cannonThickness / 2,
                        cannonLength,
                        cannonThickness
                    );
                }
            } else {
                // Horizontal ship
                const halfHeight = bodyWidth / 2;
                const segmentWidth = cellSize * 0.9;
                
                if (i === 0) {
                    // Bow (pointed triangle)
                    ctx.fillStyle = color;
                    ctx.beginPath();
                    if (this.orientation === RIGHT) {
                        ctx.moveTo(screen.x + segmentWidth / 2, screen.y);
                        ctx.lineTo(screen.x - segmentWidth / 3, screen.y - halfHeight);
                        ctx.lineTo(screen.x - segmentWidth / 3, screen.y + halfHeight);
                    } else {
                        ctx.moveTo(screen.x - segmentWidth / 2, screen.y);
                        ctx.lineTo(screen.x + segmentWidth / 3, screen.y - halfHeight);
                        ctx.lineTo(screen.x + segmentWidth / 3, screen.y + halfHeight);
                    }
                    ctx.closePath();
                    ctx.fill();
                } else {
                    // Body segment
                    ctx.fillStyle = color;
                    ctx.fillRect(
                        screen.x - segmentWidth / 2,
                        screen.y - halfHeight,
                        segmentWidth,
                        bodyWidth
                    );
                }
                
                // Cannons (vertical for horizontal ships)
                if (cannonPositions.includes(i)) {
                    ctx.fillStyle = COLORS.cannon;
                    // Top cannon
                    ctx.fillRect(
                        screen.x - cannonThickness / 2,
                        screen.y - halfHeight - cannonLength,
                        cannonThickness,
                        cannonLength
                    );
                    // Bottom cannon
                    ctx.fillRect(
                        screen.x - cannonThickness / 2,
                        screen.y + halfHeight,
                        cannonThickness,
                        cannonLength
                    );
                }
            }
        }
        
        // Selection indicator
        if (this.selected) {
            const bow = this.board.gridToScreen(this.x, this.y);
            ctx.strokeStyle = COLORS.selected;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(bow.x, bow.y, cellSize / 2 + 4, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
}
