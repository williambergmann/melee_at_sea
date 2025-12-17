// Title Screen - 8-bit style title screen and menu
import { SCREEN_WIDTH, SCREEN_HEIGHT, TITLE_COLORS } from './constants.js';

export class TitleScreen {
    static STATE_TITLE = 0;
    static STATE_MENU = 1;
    static STATE_NEWGAME = 2;
    
    constructor(screenWidth = SCREEN_WIDTH, screenHeight = SCREEN_HEIGHT, sound = null) {
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.sound = sound;
        
        this.state = TitleScreen.STATE_TITLE;
        this.selectedIndex = 0;
        this.blinkTimer = 0;
        this.showPrompt = true;
        
        this.mainMenu = ['NEW GAME', 'QUIT'];
        this.newgameMenu = ['SINGLE PLAYER', '2 PLAYER', 'BACK'];
        
        // Pixel letter definitions for "Melee at Sea"
        this.pixelLetters = this.initPixelLetters();
    }
    
    initPixelLetters() {
        return {
            'M': [
                "██          ██",
                "███        ███",
                "█ ██      ██ █",
                "█  ██    ██  █",
                "█   ██  ██   █",
                "█    ████    █",
                "█     ██     █",
                "█            █",
                "█            █",
                "█            █",
                " █          █ ",
                "  ██      ██  ",
            ],
            'e': [
                "            ",
                "            ",
                "            ",
                "   ████     ",
                "  █    █    ",
                " █      █   ",
                " ████████   ",
                " █          ",
                "  █         ",
                "   ████     ",
                "       ██   ",
                "            ",
            ],
            'l': [
                "  ██   ",
                "   █   ",
                "   █   ",
                "   █   ",
                "   █   ",
                "   █   ",
                "   █   ",
                "   █   ",
                "   █   ",
                "    █  ",
                "     █ ",
                "      █",
            ],
            'a': [
                "             ",
                "             ",
                "             ",
                "             ",
                "    ████     ",
                "        █    ",
                "    █████    ",
                "   █    █    ",
                "  █     █    ",
                "   █████ █   ",
                "          █  ",
                "             ",
            ],
            't': [
                "  ██      ",
                "   █      ",
                "   █      ",
                " ██████   ",
                "   █      ",
                "   █      ",
                "   █      ",
                "   █      ",
                "    █     ",
                "     ██   ",
                "       █  ",
                "        ██",
            ],
            'S': [
                "     ████      ",
                "   ██    ██    ",
                "  █        █   ",
                "  █            ",
                "   ██          ",
                "     ████      ",
                "         ██    ",
                "           █   ",
                "           █   ",
                "  █        █   ",
                "   ██    ██    ",
                "     ████      ",
            ],
            ' ': [
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
            ],
        };
    }
    
    update(dt) {
        this.blinkTimer += dt * 1000;
        if (this.blinkTimer >= 500) {
            this.blinkTimer = this.blinkTimer % 500;
            this.showPrompt = !this.showPrompt;
        }
    }
    
    handleKey(key) {
        if (this.state === TitleScreen.STATE_TITLE) {
            if (key === 'Enter') {
                this.state = TitleScreen.STATE_MENU;
                this.selectedIndex = 0;
                if (this.sound) this.sound.play('select');
                return null;
            }
        } else if (this.state === TitleScreen.STATE_MENU) {
            if (key === 'ArrowUp' || key === 'w' || key === 'W') {
                this.selectedIndex = (this.selectedIndex - 1 + this.mainMenu.length) % this.mainMenu.length;
                if (this.sound) this.sound.play('select');
            } else if (key === 'ArrowDown' || key === 's' || key === 'S') {
                this.selectedIndex = (this.selectedIndex + 1) % this.mainMenu.length;
                if (this.sound) this.sound.play('select');
            } else if (key === 'Enter') {
                if (this.sound) this.sound.play('select');
                const selected = this.mainMenu[this.selectedIndex];
                if (selected === 'NEW GAME') {
                    this.state = TitleScreen.STATE_NEWGAME;
                    this.selectedIndex = 0;
                } else if (selected === 'QUIT') {
                    return 'quit';
                }
            } else if (key === 'Escape') {
                this.state = TitleScreen.STATE_TITLE;
            }
        } else if (this.state === TitleScreen.STATE_NEWGAME) {
            if (key === 'ArrowUp' || key === 'w' || key === 'W') {
                this.selectedIndex = (this.selectedIndex - 1 + this.newgameMenu.length) % this.newgameMenu.length;
                if (this.sound) this.sound.play('select');
            } else if (key === 'ArrowDown' || key === 's' || key === 'S') {
                this.selectedIndex = (this.selectedIndex + 1) % this.newgameMenu.length;
                if (this.sound) this.sound.play('select');
            } else if (key === 'Enter') {
                if (this.sound) this.sound.play('select');
                const selected = this.newgameMenu[this.selectedIndex];
                if (selected === 'SINGLE PLAYER') {
                    return 'start_single';
                } else if (selected === '2 PLAYER') {
                    return 'start_multi';
                } else if (selected === 'BACK') {
                    this.state = TitleScreen.STATE_MENU;
                    this.selectedIndex = 0;
                }
            } else if (key === 'Escape') {
                this.state = TitleScreen.STATE_MENU;
                this.selectedIndex = 0;
            }
        }
        return null;
    }
    
    render(ctx) {
        // Fill with dark navy background
        ctx.fillStyle = TITLE_COLORS.bg;
        ctx.fillRect(0, 0, this.screenWidth, this.screenHeight);
        
        // Draw ocean/water area
        ctx.fillStyle = TITLE_COLORS.bgOcean;
        ctx.fillRect(0, this.screenHeight / 2 + 40, this.screenWidth, this.screenHeight / 2 - 40);
        
        // Draw scanlines
        this.drawScanlines(ctx);
        
        // Draw waves
        this.drawWaves(ctx);
        
        // Draw sailing ship
        const bobOffset = Math.sin(this.blinkTimer * 0.005) * 5;
        this.drawSailingShip(ctx, this.screenWidth / 2, 400 + bobOffset, 4);
        
        // Draw title
        this.renderCursiveTitle(ctx, "Melee at Sea", this.screenWidth / 2, 80);
        
        // Draw based on state
        if (this.state === TitleScreen.STATE_TITLE) {
            this.renderTitlePrompt(ctx);
        } else if (this.state === TitleScreen.STATE_MENU) {
            this.renderMenu(ctx, this.mainMenu);
        } else if (this.state === TitleScreen.STATE_NEWGAME) {
            this.renderMenu(ctx, this.newgameMenu, "SELECT MODE");
        }
    }
    
    drawScanlines(ctx) {
        ctx.fillStyle = TITLE_COLORS.navyDark;
        for (let y = 0; y < this.screenHeight; y += 3) {
            ctx.fillRect(0, y, this.screenWidth, 1);
        }
    }
    
    drawWaves(ctx) {
        const waveY = this.screenHeight / 2 + 60;
        const timeOffset = this.blinkTimer * 0.003;
        
        for (let layer = 0; layer < 15; layer++) {
            const layerY = waveY + layer * 15;
            for (let i = 0; i < this.screenWidth; i += 12) {
                const waveOffset = Math.sin(i * 0.08 + timeOffset + layer) * 4;
                const shimmer = Math.sin(i * 0.15 + timeOffset * 2 + layer * 2);
                const shimmerBrightness = 20 + shimmer * 15;
                
                if (shimmer > 0.5) {
                    ctx.strokeStyle = `rgb(${50 + shimmerBrightness}, ${80 + shimmerBrightness}, ${120 + shimmerBrightness})`;
                } else {
                    ctx.strokeStyle = TITLE_COLORS.navyMid;
                }
                
                ctx.beginPath();
                ctx.moveTo(i, layerY + waveOffset);
                ctx.lineTo(i + 8, layerY + waveOffset + 2);
                ctx.stroke();
            }
        }
    }
    
    drawSailingShip(ctx, centerX, centerY, scale) {
        const ps = scale;
        
        // Hull pixels
        const hull = [
            [-15,4],[-14,4],[-13,4],[-12,4],[-11,4],[-10,4],[-9,4],[-8,4],[-7,4],[-6,4],
            [-5,4],[-4,4],[-3,4],[-2,4],[-1,4],[0,4],[1,4],[2,4],[3,4],[4,4],[5,4],[6,4],
            [7,4],[8,4],[9,4],[10,4],[11,4],[12,4],[13,4],[14,4],[15,4],
            [-14,5],[-13,5],[-12,5],[-11,5],[-10,5],[-9,5],[-8,5],[-7,5],[-6,5],[-5,5],
            [-4,5],[-3,5],[-2,5],[-1,5],[0,5],[1,5],[2,5],[3,5],[4,5],[5,5],[6,5],[7,5],
            [8,5],[9,5],[10,5],[11,5],[12,5],[13,5],
            [-12,6],[-11,6],[-10,6],[-9,6],[-8,6],[-7,6],[-6,6],[-5,6],[-4,6],[-3,6],
            [-2,6],[-1,6],[0,6],[1,6],[2,6],[3,6],[4,6],[5,6],[6,6],[7,6],[8,6],[9,6],[10,6],
            [16,4],[17,3],[18,2],
            [-15,3],[-14,3],[-13,3],[-12,3],[-11,3],[-10,3],[-9,3],[-8,3],[-7,3],[-6,3],
            [-5,3],[-4,3],[-3,3],[-2,3],[-1,3],[0,3],[1,3],[2,3],[3,3],[4,3],[5,3],[6,3],
            [7,3],[8,3],[9,3],[10,3],[11,3],[12,3],[13,3],[14,3],[15,3],[16,3],
        ];
        
        // Draw hull
        for (const [px, py] of hull) {
            ctx.fillStyle = py < 5 ? TITLE_COLORS.sepiaMid : TITLE_COLORS.sepiaDark;
            ctx.fillRect(centerX + px * ps, centerY + py * ps, ps, ps);
        }
        
        // Masts
        const mastPositions = [-8, 0, 10];
        for (const mx of mastPositions) {
            ctx.fillStyle = TITLE_COLORS.sepiaDark;
            ctx.fillRect(centerX + mx * ps, centerY - 15 * ps, ps, 18 * ps);
            
            const yardHeights = [-5, -12, -18];
            const yardWidths = [10, 8, 6];
            
            for (let i = 0; i < yardHeights.length; i++) {
                const yh = yardHeights[i];
                const yw = yardWidths[i];
                
                ctx.fillStyle = TITLE_COLORS.sepiaDark;
                ctx.fillRect(centerX + (mx - yw/2) * ps, centerY + yh * ps, yw * ps, ps);
                
                ctx.fillStyle = TITLE_COLORS.cream;
                ctx.fillRect(centerX + (mx - yw/2) * ps, centerY + (yh + 1) * ps, yw * ps, 4 * ps);
            }
        }
    }
    
    renderCursiveTitle(ctx, text, centerX, y) {
        const pixelSize = 4;
        const spacing = 0;
        
        // Calculate total width
        let totalWidth = 0;
        for (const char of text) {
            const letter = this.pixelLetters[char] || this.pixelLetters[char.toLowerCase()] || this.pixelLetters[' '];
            totalWidth += letter[0].length * pixelSize + spacing * pixelSize;
        }
        
        // Draw shadow
        let x = centerX - totalWidth / 2 + 5;
        for (const char of text) {
            const letter = this.pixelLetters[char] || this.pixelLetters[char.toLowerCase()] || this.pixelLetters[' '];
            for (let row = 0; row < letter.length; row++) {
                for (let col = 0; col < letter[row].length; col++) {
                    if (letter[row][col] === '█') {
                        ctx.fillStyle = TITLE_COLORS.sepiaDark;
                        ctx.fillRect(x + col * pixelSize, y + row * pixelSize + 5, pixelSize, pixelSize);
                    }
                }
            }
            x += (letter[0].length + spacing) * pixelSize;
        }
        
        // Draw main text
        x = centerX - totalWidth / 2;
        for (const char of text) {
            const letter = this.pixelLetters[char] || this.pixelLetters[char.toLowerCase()] || this.pixelLetters[' '];
            for (let row = 0; row < letter.length; row++) {
                for (let col = 0; col < letter[row].length; col++) {
                    if (letter[row][col] === '█') {
                        ctx.fillStyle = TITLE_COLORS.sepiaHighlight;
                        ctx.fillRect(x + col * pixelSize, y + row * pixelSize, pixelSize, pixelSize);
                    }
                }
            }
            x += (letter[0].length + spacing) * pixelSize;
        }
    }
    
    renderTitlePrompt(ctx) {
        if (this.showPrompt) {
            ctx.font = '18px "Courier New", monospace';
            ctx.fillStyle = TITLE_COLORS.sepiaLight;
            ctx.textAlign = 'center';
            ctx.fillText("~ Press ENTER ~", this.screenWidth / 2, this.screenHeight - 80);
        }
        
        ctx.font = '16px "Courier New", monospace';
        ctx.fillStyle = TITLE_COLORS.sepiaMid;
        ctx.textAlign = 'center';
        ctx.fillText("A DOS-Style Naval Strategy Game", this.screenWidth / 2, this.screenHeight - 40);
    }
    
    renderMenu(ctx, menuItems, title = null) {
        const startY = this.screenHeight - 180;
        
        if (title) {
            ctx.font = '20px "Courier New", monospace';
            ctx.fillStyle = TITLE_COLORS.sepiaLight;
            ctx.textAlign = 'center';
            ctx.fillText(title, this.screenWidth / 2, startY - 35);
        }
        
        for (let i = 0; i < menuItems.length; i++) {
            let color, prefix, suffix;
            if (i === this.selectedIndex) {
                color = TITLE_COLORS.sepiaHighlight;
                prefix = ">> ";
                suffix = " <<";
            } else {
                color = TITLE_COLORS.sepiaMid;
                prefix = "   ";
                suffix = "   ";
            }
            
            ctx.font = '24px "Courier New", monospace';
            ctx.fillStyle = color;
            ctx.textAlign = 'center';
            ctx.fillText(`${prefix}${menuItems[i]}${suffix}`, this.screenWidth / 2, startY + i * 40);
        }
        
        ctx.font = '14px "Courier New", monospace';
        ctx.fillStyle = TITLE_COLORS.sepiaDark;
        ctx.textAlign = 'center';
        ctx.fillText("UP/DOWN: Select   ENTER: Confirm   ESC: Back", this.screenWidth / 2, this.screenHeight - 20);
    }
    
    reset() {
        this.state = TitleScreen.STATE_TITLE;
        this.selectedIndex = 0;
    }
}
