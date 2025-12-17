// AI Opponent - Simple AI for enemy fleet control
export class AI {
    constructor(combat) {
        this.combat = combat;
    }
    
    takeTurn(enemyShips, playerShips, allShips) {
        const actions = [];
        
        // Get list of alive ships that can act
        const aliveShips = enemyShips.filter(ship => ship.isAlive);
        if (aliveShips.length === 0) return actions;
        
        // Shuffle to add unpredictability
        this.shuffle(aliveShips);
        
        // Find a ship that can either fire or make a good move
        let bestShip = null;
        let bestAction = null;
        let bestPriority = -1;
        
        for (const ship of aliveShips) {
            // Check if this ship can fire (highest priority)
            const targets = this.combat.getTargetsInRange(ship, allShips);
            if (targets.length > 0) {
                if (bestPriority < 2) {
                    bestPriority = 2;
                    bestShip = ship;
                    bestAction = { type: 'fire', dir: null };
                }
            } else {
                // Check if this ship can make a useful move
                const move = this.findBestMove(ship, playerShips, allShips);
                if (move && bestPriority < 1) {
                    bestPriority = 1;
                    bestShip = ship;
                    bestAction = move;
                }
            }
        }
        
        // If no good action found, pick random ship to move toward enemies
        if (!bestShip) {
            bestShip = aliveShips[Math.floor(Math.random() * aliveShips.length)];
            bestAction = this.findBestMove(bestShip, playerShips, allShips);
        }
        
        // Execute the action for the chosen ship
        if (bestShip && bestAction) {
            if (bestAction.type === 'fire') {
                const hits = this.combat.fireBroadside(bestShip, allShips);
                bestShip.hasFired = true;
                if (hits.length > 0) {
                    const hitNames = hits.map(h => h.destroyed ? 'destroyed a ship' : 'hit a ship');
                    actions.push(`Enemy fired: ${hitNames.join(', ')}!`);
                } else {
                    actions.push("Enemy ship fired but missed!");
                }
            } else if (bestAction.type === 'move') {
                if (bestShip.move(bestAction.dir, allShips)) {
                    bestShip.hasMoved = true;
                    actions.push("Enemy ship advanced");
                }
            } else if (bestAction.type === 'rotate') {
                if (bestShip.rotate(bestAction.dir, allShips)) {
                    bestShip.hasMoved = true;
                    actions.push("Enemy ship maneuvered");
                }
            }
        }
        
        return actions;
    }
    
    findBestMove(ship, playerShips, allShips) {
        let bestScore = -1;
        let bestMove = null;
        
        const moves = [
            { type: 'move', dir: 'forward' },
            { type: 'move', dir: 'backward' },
            { type: 'rotate', dir: 'cw' },
            { type: 'rotate', dir: 'ccw' }
        ];
        
        this.shuffle(moves);
        
        for (const move of moves) {
            // Save current state
            const oldX = ship.x;
            const oldY = ship.y;
            const oldOrientation = ship.orientation;
            
            // Try the move
            let success = false;
            if (move.type === 'move') {
                success = ship.move(move.dir, allShips);
            } else if (move.type === 'rotate') {
                success = ship.rotate(move.dir, allShips);
            }
            
            if (success) {
                // Evaluate new position
                const score = this.evaluatePosition(ship, playerShips, allShips);
                
                // Restore state
                ship.x = oldX;
                ship.y = oldY;
                ship.orientation = oldOrientation;
                
                if (score > bestScore) {
                    bestScore = score;
                    bestMove = move;
                }
            } else {
                // Restore state if move failed
                ship.x = oldX;
                ship.y = oldY;
                ship.orientation = oldOrientation;
            }
        }
        
        return bestMove;
    }
    
    evaluatePosition(ship, playerShips, allShips) {
        let score = 0;
        
        // Bonus for having targets in range
        const targets = this.combat.getTargetsInRange(ship, allShips);
        for (const { hitCells } of targets) {
            score += hitCells.length * 10;
        }
        
        // Penalty for being in enemy fire zones
        for (const playerShip of playerShips) {
            if (!playerShip.isAlive) continue;
            const enemyFireZones = playerShip.getFireZones();
            const shipCells = ship.getCells();
            
            for (const cell of shipCells) {
                for (const zone of enemyFireZones) {
                    if (cell.x === zone.x && cell.y === zone.y) {
                        score -= 5;
                    }
                }
            }
        }
        
        // Small bonus for being closer to enemies (aggressive AI)
        for (const playerShip of playerShips) {
            if (!playerShip.isAlive) continue;
            const distance = Math.abs(ship.x - playerShip.x) + Math.abs(ship.y - playerShip.y);
            score += Math.max(0, 10 - distance);
        }
        
        return score;
    }
    
    shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
}
