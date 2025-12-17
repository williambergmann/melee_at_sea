// Combat System - Handles firing and damage for Melee at Sea
import { UP, DOWN, LEFT, RIGHT } from './constants.js';

export class Combat {
    constructor(board) {
        this.board = board;
    }
    
    getSideFireZones(ship) {
        const sideCells = [];
        const shipCells = ship.getCells();
        
        // Determine perpendicular directions based on ship orientation
        let sideOffsets;
        if (ship.orientation === UP || ship.orientation === DOWN) {
            sideOffsets = [{ dx: -1, dy: 0 }, { dx: 1, dy: 0 }];
        } else {
            sideOffsets = [{ dx: 0, dy: -1 }, { dx: 0, dy: 1 }];
        }
        
        // Only fire from segments that have cannons
        const bodySegments = shipCells.length - 1;
        const cannonCount = Math.min(ship.cannonsPerSide, bodySegments);
        
        for (let i = 0; i < shipCells.length; i++) {
            // Skip bow (i=0), only body segments have cannons
            if (i === 0) continue;
            // Only include segments that still have cannons
            if (i > cannonCount) continue;
            
            const cell = shipCells[i];
            for (const offset of sideOffsets) {
                const targetX = cell.x + offset.dx;
                const targetY = cell.y + offset.dy;
                
                if (this.board.isValidCell(targetX, targetY)) {
                    const exists = sideCells.some(c => c.x === targetX && c.y === targetY);
                    if (!exists) {
                        sideCells.push({ x: targetX, y: targetY });
                    }
                }
            }
        }
        
        return sideCells;
    }
    
    getTargetsInRange(attacker, allShips) {
        const fireZones = this.getSideFireZones(attacker);
        const targets = [];
        
        for (const ship of allShips) {
            if (ship === attacker || ship.team === attacker.team) continue;
            if (!ship.isAlive) continue;
            
            const shipCells = ship.getCells();
            const hitCells = [];
            
            for (const cell of shipCells) {
                for (const zone of fireZones) {
                    if (cell.x === zone.x && cell.y === zone.y) {
                        hitCells.push(cell);
                        break;
                    }
                }
            }
            
            if (hitCells.length > 0) {
                targets.push({ ship, hitCells });
            }
        }
        
        return targets;
    }
    
    fire(attacker, targetCell, allShips) {
        const fireZones = this.getSideFireZones(attacker);
        
        const inRange = fireZones.some(z => z.x === targetCell.x && z.y === targetCell.y);
        if (!inRange) {
            return { hitShip: null, destroyed: false };
        }
        
        // Check if any enemy ship occupies this cell
        for (const ship of allShips) {
            if (ship === attacker || ship.team === attacker.team) continue;
            if (!ship.isAlive) continue;
            
            const cells = ship.getCells();
            for (const cell of cells) {
                if (cell.x === targetCell.x && cell.y === targetCell.y) {
                    const destroyed = ship.takeDamage();
                    return { hitShip: ship, destroyed };
                }
            }
        }
        
        return { hitShip: null, destroyed: false };
    }
    
    fireBroadside(attacker, allShips) {
        // Check if ship has any cannons to fire
        if (attacker.cannonsPerSide <= 0) {
            return [];
        }
        
        const hits = [];
        const targets = this.getTargetsInRange(attacker, allShips);
        
        // Each ship can only be hit once per broadside
        for (const { ship, hitCells } of targets) {
            if (hitCells.length > 0) {
                const destroyed = ship.takeDamage();
                hits.push({ ship, destroyed });
            }
        }
        
        return hits;
    }
}
