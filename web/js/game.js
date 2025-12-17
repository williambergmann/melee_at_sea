// Game - Main game class for Melee at Sea
import { 
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_COLS, GRID_ROWS, CELL_SIZE,
    UP, DOWN, LEFT, RIGHT, GameState, GameMode, COLORS
} from './constants.js';
import { Board } from './board.js';
import { Ship } from './ship.js';
import { Combat } from './combat.js';
import { AI } from './ai.js';
import { UI } from './ui.js';
import { TitleScreen } from './title_screen.js';
import { SoundSystem } from './sound.js';

export class Game {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        
        // Initialize game components
        this.board = new Board(GRID_COLS, GRID_ROWS, CELL_SIZE);
        this.board.setOffset(SCREEN_WIDTH, SCREEN_HEIGHT);
        
        this.combat = new Combat(this.board);
        this.ai = new AI(this.combat);
        this.ui = new UI(SCREEN_WIDTH, SCREEN_HEIGHT);
        
        // Initialize sound effects
        this.sound = new SoundSystem();
        
        // Initialize title screen
        this.titleScreen = new TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT, this.sound);
        
        // Game state
        this.state = GameState.TITLE;
        this.selectedShip = null;
        this.playerWon = false;
        
        // Game mode
        this.gameMode = GameMode.SINGLE_PLAYER;
        
        // Message system
        this.message = '';
        this.messageTimer = 0;
        
        // AI turn timing
        this.aiActionTimer = 0;
        this.aiActions = [];
        this.aiActionIndex = 0;
        
        // Ships
        this.playerShips = [];
        this.enemyShips = [];
        this.allShips = [];
        
        // Initialize ships
        this.initShips();
        
        // Bind event handlers
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleClick = this.handleClick.bind(this);
        
        // Last frame time for delta calculation
        this.lastTime = 0;
    }
    
    initShips() {
        this.playerShips = [];
        this.enemyShips = [];
        
        // Ship configs: [length, count]
        const shipConfigs = [[2, 2], [3, 3], [4, 2]];
        
        // Create all ship lengths
        const allLengths = [];
        for (const [length, count] of shipConfigs) {
            for (let i = 0; i < count; i++) {
                allLengths.push(length);
            }
        }
        this.shuffle(allLengths);
        
        // Available y positions
        const playerYPositions = [0, 2, 4, 6, 8, 10, 12];
        const enemyYPositions = [0, 2, 4, 6, 8, 10, 12];
        this.shuffle(playerYPositions);
        this.shuffle(enemyYPositions);
        
        // Place player ships on left side (facing RIGHT)
        for (let i = 0; i < allLengths.length; i++) {
            const length = allLengths[i];
            const y = playerYPositions[i % playerYPositions.length];
            this.playerShips.push(new Ship(length - 1, y, length, RIGHT, 'player', this.board));
        }
        
        // Place enemy ships on right side (facing LEFT)
        this.shuffle(allLengths);
        for (let i = 0; i < allLengths.length; i++) {
            const length = allLengths[i];
            const y = enemyYPositions[i % enemyYPositions.length];
            const bowX = 20 - length;
            this.enemyShips.push(new Ship(bowX, y, length, LEFT, 'enemy', this.board));
        }
        
        this.allShips = [...this.playerShips, ...this.enemyShips];
    }
    
    shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
    
    resetGame() {
        this.state = GameState.PLAYER_SELECT;
        this.selectedShip = null;
        this.playerWon = false;
        this.message = '';
        this.messageTimer = 0;
        this.initShips();
    }
    
    startGame(mode) {
        this.gameMode = mode;
        this.resetGame();
        if (mode === GameMode.TWO_PLAYER) {
            this.showMessage("PLAYER 1'S TURN - Select a ship!", 3000);
        } else {
            this.showMessage("Select a ship to begin!", 3000);
        }
    }
    
    showMessage(text, duration = 2000) {
        this.message = text;
        this.messageTimer = duration;
    }
    
    startPlayerTurn() {
        this.state = GameState.PLAYER_SELECT;
        this.selectedShip = null;
        
        for (const ship of this.playerShips) {
            ship.hasMoved = false;
            ship.hasFired = false;
            ship.selected = false;
        }
    }
    
    startEnemyTurn() {
        if (this.gameMode === GameMode.TWO_PLAYER) {
            this.startPlayer2Turn();
        } else {
            this.state = GameState.ENEMY_TURN;
            this.selectedShip = null;
            
            for (const ship of this.enemyShips) {
                ship.hasMoved = false;
                ship.hasFired = false;
            }
            
            this.aiActions = this.ai.takeTurn(this.enemyShips, this.playerShips, this.allShips);
            this.aiActionIndex = 0;
            this.aiActionTimer = 500;
        }
    }
    
    startPlayer2Turn() {
        this.state = GameState.PLAYER2_SELECT;
        this.selectedShip = null;
        
        for (const ship of this.enemyShips) {
            ship.hasMoved = false;
            ship.hasFired = false;
            ship.selected = false;
        }
        
        this.showMessage("PLAYER 2'S TURN!", 1500);
    }
    
    checkGameOver() {
        const playerAlive = this.playerShips.some(s => s.isAlive);
        const enemyAlive = this.enemyShips.some(s => s.isAlive);
        
        if (!enemyAlive) {
            this.state = GameState.GAME_OVER;
            this.playerWon = true;
            return true;
        } else if (!playerAlive) {
            this.state = GameState.GAME_OVER;
            this.playerWon = false;
            return true;
        }
        return false;
    }
    
    selectShip(ship, player = 1) {
        if (this.selectedShip) {
            this.selectedShip.selected = false;
        }
        
        this.selectedShip = ship;
        ship.selected = true;
        
        if (player === 1) {
            this.state = GameState.PLAYER_MOVE;
        } else {
            this.state = GameState.PLAYER2_MOVE;
        }
    }
    
    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        const x = (event.clientX - rect.left) * scaleX;
        const y = (event.clientY - rect.top) * scaleY;
        
        if (this.state === GameState.GAME_OVER) return;
        
        const grid = this.board.screenToGrid(x, y);
        
        if (this.state === GameState.PLAYER_SELECT) {
            for (const ship of this.playerShips) {
                if (!ship.isAlive) continue;
                const cells = ship.getCells();
                if (cells.some(c => c.x === grid.x && c.y === grid.y)) {
                    this.selectShip(ship, 1);
                    break;
                }
            }
        } else if (this.state === GameState.PLAYER2_SELECT) {
            for (const ship of this.enemyShips) {
                if (!ship.isAlive) continue;
                const cells = ship.getCells();
                if (cells.some(c => c.x === grid.x && c.y === grid.y)) {
                    this.selectShip(ship, 2);
                    break;
                }
            }
        } else if (this.state === GameState.PLAYER_FIRE || this.state === GameState.PLAYER2_FIRE) {
            if (this.selectedShip && !this.selectedShip.hasFired) {
                const fireZones = this.combat.getSideFireZones(this.selectedShip);
                if (fireZones.some(z => z.x === grid.x && z.y === grid.y)) {
                    const result = this.combat.fire(this.selectedShip, grid, this.allShips);
                    this.selectedShip.hasFired = true;
                    
                    if (result.hitShip) {
                        if (result.destroyed) {
                            this.showMessage("SHIP DESTROYED!");
                        } else {
                            this.showMessage("HIT!");
                        }
                        this.checkGameOver();
                    } else {
                        this.showMessage("MISS!");
                    }
                }
            }
        }
    }
    
    handleKeyDown(event) {
        const key = event.key;
        
        // Initialize sound on first interaction
        this.sound.init();
        
        // Title screen handling
        if (this.state === GameState.TITLE) {
            const result = this.titleScreen.handleKey(key);
            if (result === 'start_single') {
                this.startGame(GameMode.SINGLE_PLAYER);
            } else if (result === 'start_multi') {
                this.startGame(GameMode.TWO_PLAYER);
            } else if (result === 'quit') {
                // Can't really quit in browser
            }
            if (key === 'Escape' && this.titleScreen.state === TitleScreen.STATE_TITLE) {
                // Can't quit in browser
            }
            return;
        }
        
        if (this.state === GameState.GAME_OVER) {
            if (key === 'r' || key === 'R') {
                this.startGame(this.gameMode);
            }
            return;
        }
        
        if (key === 'Escape') {
            // Go back to title
            this.state = GameState.TITLE;
            this.titleScreen.reset();
            return;
        }
        
        // Player 1 SELECT phase
        if (this.state === GameState.PLAYER_SELECT) {
            if (key === 'Enter') {
                this.startEnemyTurn();
            }
        }
        
        // Player 1 MOVE phase
        if (this.state === GameState.PLAYER_MOVE) {
            if (this.selectedShip) {
                let moved = false;
                
                if (key === 'w' || key === 'W' || key === 'ArrowUp') {
                    moved = this.selectedShip.move('forward', this.allShips);
                } else if (key === 's' || key === 'S' || key === 'ArrowDown') {
                    moved = this.selectedShip.move('backward', this.allShips);
                } else if (key === 'q' || key === 'Q') {
                    moved = this.selectedShip.rotate('ccw', this.allShips);
                } else if (key === 'e' || key === 'E') {
                    moved = this.selectedShip.rotate('cw', this.allShips);
                } else if (key === 'a' || key === 'A' || key === 'ArrowLeft') {
                    moved = this.selectedShip.rotate('ccw', this.allShips);
                } else if (key === 'd' || key === 'D' || key === 'ArrowRight') {
                    moved = this.selectedShip.rotate('cw', this.allShips);
                }
                
                if (moved) {
                    this.sound.play('move');
                }
            }
            
            if (key === 'Enter') {
                if (this.selectedShip) {
                    this.selectedShip.selected = false;
                    this.selectedShip = null;
                }
                this.state = GameState.PLAYER_FIRE;
                this.showMessage("SELECT SHIP TO FIRE", 2500);
                return;
            }
        }
        
        // Player 1 FIRE phase
        if (this.state === GameState.PLAYER_FIRE) {
            if (key === ' ' || key === 'f' || key === 'F') {
                if (this.selectedShip && !this.selectedShip.hasFired) {
                    const hits = this.combat.fireBroadside(this.selectedShip, this.allShips);
                    this.selectedShip.hasFired = true;
                    
                    if (hits.length > 0) {
                        const destroyedCount = hits.filter(h => h.destroyed).length;
                        const hitCount = hits.length - destroyedCount;
                        
                        if (destroyedCount > 0) {
                            this.showMessage(`${destroyedCount} SHIP(S) DESTROYED!`);
                            this.sound.play('destroy');
                        } else if (hitCount > 0) {
                            this.showMessage(`${hitCount} HIT(S)!`, 2500);
                            this.sound.play('hit');
                        }
                        
                        this.checkGameOver();
                    } else {
                        this.showMessage("NO TARGETS IN RANGE!", 2500);
                    }
                    
                    this.sound.play('fire');
                    
                    this.selectedShip.selected = false;
                    this.selectedShip = null;
                    this.startEnemyTurn();
                }
            }
            
            if (key === 'Enter') {
                this.startEnemyTurn();
            }
        }
        
        // Player 2 MOVE phase
        if (this.state === GameState.PLAYER2_MOVE) {
            if (this.selectedShip) {
                let moved = false;
                
                if (key === 'w' || key === 'W' || key === 'ArrowUp') {
                    moved = this.selectedShip.move('forward', this.allShips);
                } else if (key === 's' || key === 'S' || key === 'ArrowDown') {
                    moved = this.selectedShip.move('backward', this.allShips);
                } else if (key === 'q' || key === 'Q') {
                    moved = this.selectedShip.rotate('ccw', this.allShips);
                } else if (key === 'e' || key === 'E') {
                    moved = this.selectedShip.rotate('cw', this.allShips);
                } else if (key === 'a' || key === 'A' || key === 'ArrowLeft') {
                    moved = this.selectedShip.rotate('ccw', this.allShips);
                } else if (key === 'd' || key === 'D' || key === 'ArrowRight') {
                    moved = this.selectedShip.rotate('cw', this.allShips);
                }
                
                if (moved) {
                    this.sound.play('move');
                }
            }
            
            if (key === 'Enter') {
                if (this.selectedShip) {
                    this.selectedShip.selected = false;
                    this.selectedShip = null;
                }
                this.state = GameState.PLAYER2_FIRE;
                this.showMessage("P2: SELECT SHIP TO FIRE", 1500);
                return;
            }
        }
        
        // Player 2 FIRE phase
        if (this.state === GameState.PLAYER2_FIRE) {
            if (key === ' ' || key === 'f' || key === 'F') {
                if (this.selectedShip && !this.selectedShip.hasFired) {
                    const hits = this.combat.fireBroadside(this.selectedShip, this.allShips);
                    this.selectedShip.hasFired = true;
                    
                    if (hits.length > 0) {
                        const destroyedCount = hits.filter(h => h.destroyed).length;
                        const hitCount = hits.length - destroyedCount;
                        
                        if (destroyedCount > 0) {
                            this.showMessage(`${destroyedCount} SHIP(S) DESTROYED!`);
                            this.sound.play('destroy');
                        } else if (hitCount > 0) {
                            this.showMessage(`${hitCount} HIT(S)!`, 2500);
                            this.sound.play('hit');
                        }
                        
                        this.checkGameOver();
                    } else {
                        this.showMessage("NO TARGETS IN RANGE!", 2500);
                    }
                    
                    this.sound.play('fire');
                    
                    this.selectedShip.selected = false;
                    this.selectedShip = null;
                    this.startPlayerTurn();
                    this.showMessage("PLAYER 1'S TURN!", 2500);
                }
            }
            
            if (key === 'Enter') {
                this.startPlayerTurn();
                this.showMessage("PLAYER 1'S TURN!", 1500);
            }
        }
        
        // Deselect
        if (key === 'Tab') {
            event.preventDefault();
            if (this.selectedShip) {
                this.selectedShip.selected = false;
                this.selectedShip = null;
                if (this.state === GameState.PLAYER_MOVE || this.state === GameState.PLAYER_FIRE) {
                    this.state = GameState.PLAYER_SELECT;
                } else if (this.state === GameState.PLAYER2_MOVE || this.state === GameState.PLAYER2_FIRE) {
                    this.state = GameState.PLAYER2_SELECT;
                }
            }
        }
    }
    
    update(dt) {
        // Update title screen if active
        if (this.state === GameState.TITLE) {
            this.titleScreen.update(dt);
            return;
        }
        
        // Update message timer
        if (this.messageTimer > 0) {
            this.messageTimer -= dt * 1000;
            if (this.messageTimer <= 0) {
                this.message = '';
            }
        }
        
        // Handle AI turn
        if (this.state === GameState.ENEMY_TURN) {
            this.aiActionTimer -= dt * 1000;
            
            if (this.aiActionTimer <= 0) {
                if (this.aiActionIndex < this.aiActions.length) {
                    const action = this.aiActions[this.aiActionIndex];
                    this.showMessage(action, 1000);
                    this.aiActionIndex++;
                    this.aiActionTimer = 800;
                } else {
                    // AI turn complete
                    if (!this.checkGameOver()) {
                        this.startPlayerTurn();
                        this.showMessage("YOUR TURN!", 1500);
                    }
                }
            }
        }
    }
    
    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
        
        // Render title screen if active
        if (this.state === GameState.TITLE) {
            this.titleScreen.render(this.ctx);
            return;
        }
        
        // Render board
        this.board.render(this.ctx);
        
        // Show fire zones if a ship is selected in fire phase
        if (this.selectedShip && (this.state === GameState.PLAYER_FIRE || this.state === GameState.PLAYER2_FIRE)) {
            if (!this.selectedShip.hasFired && this.selectedShip.cannonsPerSide > 0) {
                const fireZones = this.combat.getSideFireZones(this.selectedShip);
                this.board.clearHighlights();
                for (const zone of fireZones) {
                    this.board.addHighlight(zone.x, zone.y, 'rgb(255, 100, 100)', 0.3);
                }
            }
        } else {
            this.board.clearHighlights();
        }
        
        // Draw highlights
        for (const highlight of this.board.highlights) {
            const screenX = this.board.offsetX + highlight.x * this.board.cellSize;
            const screenY = this.board.offsetY + highlight.y * this.board.cellSize;
            
            this.ctx.fillStyle = highlight.color;
            this.ctx.globalAlpha = highlight.alpha;
            this.ctx.fillRect(screenX, screenY, this.board.cellSize, this.board.cellSize);
            this.ctx.globalAlpha = 1;
        }
        
        // Draw all ships
        for (const ship of this.allShips) {
            ship.render(this.ctx);
        }
        
        // Draw UI
        const isPlayer1Turn = [GameState.PLAYER_SELECT, GameState.PLAYER_MOVE, GameState.PLAYER_FIRE].includes(this.state);
        const isPlayer2Turn = [GameState.PLAYER2_SELECT, GameState.PLAYER2_MOVE, GameState.PLAYER2_FIRE].includes(this.state);
        
        if (this.gameMode === GameMode.TWO_PLAYER) {
            this.ui.renderTurnIndicator2P(this.ctx, isPlayer1Turn ? 1 : 2, this.state);
        } else {
            this.ui.renderTurnIndicator(this.ctx, this.state !== GameState.ENEMY_TURN, 
                this.state !== GameState.ENEMY_TURN ? this.state : '');
        }
        
        // Draw ship info panel if selected
        if (this.selectedShip) {
            this.ui.renderShipInfo(this.ctx, this.selectedShip, 10, SCREEN_HEIGHT - 100);
        }
        
        // Draw instructions
        let instructions = [];
        if (this.state === GameState.PLAYER_SELECT || this.state === GameState.PLAYER2_SELECT) {
            instructions = ["Click ship to select", "ENTER: End turn", "ESC: Menu"];
        } else if (this.state === GameState.PLAYER_MOVE || this.state === GameState.PLAYER2_MOVE) {
            instructions = ["WASD/Arrows: Move", "Q/E: Rotate", "ENTER: Confirm Move", "TAB: Deselect"];
        } else if (this.state === GameState.PLAYER_FIRE || this.state === GameState.PLAYER2_FIRE) {
            instructions = ["SPACE: Fire broadside", "Click target to fire", "ENTER: End turn"];
        }
        
        if (instructions.length > 0) {
            this.ui.renderInstructions(this.ctx, instructions);
        }
        
        // Draw message
        if (this.message) {
            this.ui.renderMessage(this.ctx, this.message);
        }
        
        // Draw game over screen
        if (this.state === GameState.GAME_OVER) {
            this.ui.renderGameOver(this.ctx, this.playerWon);
        }
    }
    
    gameLoop(timestamp) {
        const dt = (timestamp - this.lastTime) / 1000;
        this.lastTime = timestamp;
        
        this.update(dt);
        this.render();
        
        requestAnimationFrame(this.gameLoop.bind(this));
    }
    
    start() {
        // Add event listeners
        document.addEventListener('keydown', this.handleKeyDown);
        this.canvas.addEventListener('click', this.handleClick);
        
        // Start game loop
        this.lastTime = performance.now();
        requestAnimationFrame(this.gameLoop.bind(this));
    }
}
