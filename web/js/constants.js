// Game constants
export const SCREEN_WIDTH = 800;
export const SCREEN_HEIGHT = 600;
export const FPS = 60;

// Grid settings
export const GRID_COLS = 20;
export const GRID_ROWS = 15;
export const CELL_SIZE = 40;

// Ship orientations (in degrees, clockwise from up)
export const UP = 0;
export const RIGHT = 90;
export const DOWN = 180;
export const LEFT = 270;

// Direction vectors for each orientation
export const DIRECTION_VECTORS = {
    [UP]: { dx: 0, dy: -1 },    // In canvas, Y increases downward
    [RIGHT]: { dx: 1, dy: 0 },
    [DOWN]: { dx: 0, dy: 1 },
    [LEFT]: { dx: -1, dy: 0 }
};

// Game states
export const GameState = {
    TITLE: 'TITLE',
    PLAYER_SELECT: 'SELECT SHIP',
    PLAYER_MOVE: 'MOVE/ROTATE',
    PLAYER_FIRE: 'FIRE',
    ENEMY_TURN: 'ENEMY TURN',
    PLAYER2_SELECT: 'P2 SELECT SHIP',
    PLAYER2_MOVE: 'P2 MOVE/ROTATE',
    PLAYER2_FIRE: 'P2 FIRE',
    GAME_OVER: 'GAME OVER'
};

// Game modes
export const GameMode = {
    SINGLE_PLAYER: 'single',
    TWO_PLAYER: 'two_player'
};

// DOS-style colors
export const BG_COLOR = 'rgb(240, 235, 220)';
export const DOT_COLOR = 'rgb(40, 40, 40)';

// Ship colors
export const COLORS = {
    player: 'rgb(0, 100, 255)',
    enemy: 'rgb(200, 50, 50)',
    cannon: 'rgb(20, 20, 20)',
    selected: 'rgb(255, 255, 0)',
    fireZone: 'rgba(255, 100, 100, 0.3)',
    text: 'rgb(255, 255, 255)',
    textDim: 'rgb(150, 150, 150)',
    highlight: 'rgb(255, 255, 0)',
    panel: 'rgb(40, 40, 60)'
};

// Title screen colors (sepia + navy)
export const TITLE_COLORS = {
    bg: 'rgb(15, 25, 55)',
    bgOcean: 'rgb(20, 35, 70)',
    sepiaDark: 'rgb(101, 67, 33)',
    sepiaMid: 'rgb(160, 120, 70)',
    sepiaLight: 'rgb(210, 180, 140)',
    sepiaHighlight: 'rgb(240, 220, 180)',
    navyDark: 'rgb(10, 20, 45)',
    navyMid: 'rgb(40, 60, 100)',
    navyLight: 'rgb(70, 100, 150)',
    white: 'rgb(255, 250, 240)',
    cream: 'rgb(255, 250, 235)'
};
