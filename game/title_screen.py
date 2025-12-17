"""
Title Screen - 8-bit style title screen and menu for Melee at Sea

Features sepia/navy 2-tone color scheme with 19th century sailing warship.
"""
import pyglet
from pyglet import shapes
from pyglet.window import key
import math


class TitleScreen:
    """8-bit style title screen with menu system."""
    
    # Menu states
    STATE_TITLE = 0
    STATE_MENU = 1
    STATE_NEWGAME = 2
    
    def __init__(self, screen_width, screen_height, sound_effects=None):
        """
        Initialize the title screen.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            sound_effects: Optional SoundEffects instance for menu sounds
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sound = sound_effects
        
        self.state = self.STATE_TITLE
        self.selected_index = 0
        self.blink_timer = 0
        self.show_prompt = True
        self.theme_playing = False
        
        # Sepia + Navy 2-tone color palette
        self.colors = {
            'bg': (15, 25, 55),              # Dark navy blue
            'bg_ocean': (20, 35, 70),        # Slightly lighter navy for water
            'sepia_dark': (101, 67, 33),     # Dark sepia/brown
            'sepia_mid': (160, 120, 70),     # Medium sepia
            'sepia_light': (210, 180, 140),  # Light sepia/parchment
            'sepia_highlight': (240, 220, 180),  # Bright sepia for text
            'navy_dark': (10, 20, 45),       # Very dark navy
            'navy_mid': (40, 60, 100),       # Medium navy
            'navy_light': (70, 100, 150),    # Light navy
            'white': (255, 250, 240),        # Off-white/cream
            'cream': (255, 250, 235),        # Cream for sails
        }
        
        # Menu options
        self.main_menu = ['NEW GAME', 'QUIT']
        self.newgame_menu = ['SINGLE PLAYER', '2 PLAYER', 'BACK']
        
        # Use 8-bit style pixel fonts
        self._load_fonts()
        
        # Start playing theme song
        self.start_theme()
    
    def start_theme(self):
        """Start the 8-bit theme song."""
        if self.sound and not self.theme_playing:
            self.sound.play_theme()
            self.theme_playing = True
    
    def stop_theme(self):
        """Stop the theme song."""
        if self.sound and self.theme_playing:
            self.sound.stop_theme()
            self.theme_playing = False
    
    def _load_fonts(self):
        """Load 8-bit pixel-style fonts for authentic retro look."""
        # Prefer monospace/pixel fonts for 8-bit aesthetic
        pixel_fonts = [
            'Courier New',
            'Courier',
            'Monaco',
            'Consolas', 
            'Menlo',
            'DejaVu Sans Mono',
        ]
        
        self.pixel_font_name = None
        for font_name in pixel_fonts:
            if pyglet.font.have_font(font_name):
                self.pixel_font_name = font_name
                break
        
        # Cursive/script fonts for the title - pixelated but elegant
        cursive_fonts = [
            'Brush Script MT',
            'Snell Roundhand',
            'Lucida Handwriting',
            'Apple Chancery',
            'Zapfino',
            'Segoe Script',
            'Edwardian Script ITC',
        ]
        
        self.title_font_name = None
        for font_name in cursive_fonts:
            if pyglet.font.have_font(font_name):
                self.title_font_name = font_name
                break
        
        # Fallback to pixel font if no cursive found
        if not self.title_font_name:
            self.title_font_name = self.pixel_font_name
    
    def _draw_sailing_ship(self, batch, center_x, center_y, scale=3):
        """
        Draw a pixel-art 19th century sailing warship (frigate style).
        Uses sepia tones for the ship, navy for the water.
        Returns list of shape objects to keep them alive.
        """
        ps = scale  # pixel size
        ship_shapes = []
        
        # Ship hull - wooden brown sepia tones
        hull = [
            # Main hull body
            (-15, 4), (-14, 4), (-13, 4), (-12, 4), (-11, 4), (-10, 4), (-9, 4),
            (-8, 4), (-7, 4), (-6, 4), (-5, 4), (-4, 4), (-3, 4), (-2, 4), (-1, 4),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4),
            (9, 4), (10, 4), (11, 4), (12, 4), (13, 4), (14, 4), (15, 4),
            # Hull bottom curve
            (-14, 5), (-13, 5), (-12, 5), (-11, 5), (-10, 5), (-9, 5), (-8, 5),
            (-7, 5), (-6, 5), (-5, 5), (-4, 5), (-3, 5), (-2, 5), (-1, 5), (0, 5),
            (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5),
            (9, 5), (10, 5), (11, 5), (12, 5), (13, 5),
            # Keel
            (-12, 6), (-11, 6), (-10, 6), (-9, 6), (-8, 6), (-7, 6), (-6, 6),
            (-5, 6), (-4, 6), (-3, 6), (-2, 6), (-1, 6), (0, 6), (1, 6), (2, 6),
            (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6),
            # Bow extension
            (16, 4), (17, 3), (18, 2),
            # Hull deck line
            (-15, 3), (-14, 3), (-13, 3), (-12, 3), (-11, 3), (-10, 3), (-9, 3),
            (-8, 3), (-7, 3), (-6, 3), (-5, 3), (-4, 3), (-3, 3), (-2, 3), (-1, 3),
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3),
            (9, 3), (10, 3), (11, 3), (12, 3), (13, 3), (14, 3), (15, 3), (16, 3),
        ]
        
        # Draw hull (pyglet Y is inverted from pygame)
        for px, py in hull:
            color = self.colors['sepia_mid'] if py < 5 else self.colors['sepia_dark']
            # Flip Y coordinate for pyglet (origin bottom-left)
            rect = shapes.Rectangle(
                center_x + px * ps, 
                self.screen_height - (center_y + py * ps) - ps,
                ps, ps, color=color, batch=batch
            )
            ship_shapes.append(rect)
        
        # Masts (3 masts for frigate)
        # Masts (3 masts for frigate)
        mast_positions = [-8, 0, 10]
        for mx in mast_positions:
            # Main mast pole
            mast = shapes.Rectangle(
                center_x + mx * ps, 
                self.screen_height - (center_y - 15 * ps) - ps,
                ps, 8 * ps,  # Reduced height to match sails
                color=self.colors['sepia_dark'], batch=batch
            )
            ship_shapes.append(mast)
            
            # Yards (horizontal beams)
            yard_heights = [-5, -12, -18]
            yard_widths = [10, 8, 6]
            
            for i, yh in enumerate(yard_heights):
                yw = yard_widths[i]
                yard = shapes.Rectangle(
                    center_x + (mx - yw//2) * ps,
                    self.screen_height - (center_y + yh * ps) - ps,
                    yw * ps, ps,
                    color=self.colors['sepia_dark'], batch=batch
                )
                ship_shapes.append(yard)
                
                # Sails (cream/white)
                sail = shapes.Rectangle(
                    center_x + (mx - yw//2) * ps,
                    self.screen_height - (center_y + (yh + 4) * ps) - ps,
                    yw * ps, 4 * ps,
                    color=self.colors['cream'], batch=batch
                )
                ship_shapes.append(sail)

        return ship_shapes
    
    def _draw_waves(self, batch):
        """Draw animated wave pattern with shimmer effect. Returns list of shapes."""
        wave_shapes = []
        wave_y = self.screen_height // 2 + 60
        
        # Time-based animation
        time_offset = self.blink_timer * 0.003
        
        # Draw 15 wave layers with shimmer
        for layer in range(15):
            layer_y = wave_y + layer * 15
            for i in range(0, self.screen_width, 12):
                # Wave motion
                wave_offset = math.sin(i * 0.08 + time_offset + layer) * 4
                
                # Shimmer effect - brightness variation based on position and time
                shimmer = math.sin(i * 0.15 + time_offset * 2 + layer * 2)
                shimmer_brightness = int(20 + shimmer * 15)
                
                # Choose color based on shimmer (lighter blue for highlights)
                if shimmer > 0.5:
                    color = (50 + shimmer_brightness, 80 + shimmer_brightness, 120 + shimmer_brightness)
                else:
                    color = self.colors['navy_mid']
                
                line = shapes.Line(
                    i, self.screen_height - layer_y - wave_offset,
                    i + 8, self.screen_height - layer_y - wave_offset - 2,
                    color=color, batch=batch
                )
                wave_shapes.append(line)
        
        return wave_shapes
    
    def _draw_scanlines(self, batch):
        """Draw subtle scanline effect for CRT/DOS feel. Returns shapes."""
        scanline_shapes = []
        for y in range(0, self.screen_height, 3):
            line = shapes.Line(
                0, y, self.screen_width, y,
                color=self.colors['navy_dark'], batch=batch
            )
            scanline_shapes.append(line)
        return scanline_shapes
    
    def update(self, dt):
        """Update animations."""
        self.blink_timer += dt * 1000  # Convert to ms
        if self.blink_timer >= 500:
            self.blink_timer = self.blink_timer % 500
            self.show_prompt = not self.show_prompt
    
    def handle_key(self, symbol):
        """
        Handle key press events.
        
        Args:
            symbol: pyglet key symbol
        
        Returns:
            'start_single' - Start single player game
            'start_multi' - Start 2-player game
            'quit' - Quit game
            None - No action
        """
        if self.state == self.STATE_TITLE:
            if symbol == key.RETURN or symbol == key.ENTER:
                self.state = self.STATE_MENU
                self.selected_index = 0
                if self.sound:
                    self.sound.play('select')
                return None
        
        elif self.state == self.STATE_MENU:
            if symbol in (key.UP, key.W):
                self.selected_index = (self.selected_index - 1) % len(self.main_menu)
                if self.sound:
                    self.sound.play('select')
            elif symbol in (key.DOWN, key.S):
                self.selected_index = (self.selected_index + 1) % len(self.main_menu)
                if self.sound:
                    self.sound.play('select')
            elif symbol == key.RETURN or symbol == key.ENTER:
                if self.sound:
                    self.sound.play('select')
                selected = self.main_menu[self.selected_index]
                if selected == 'NEW GAME':
                    self.state = self.STATE_NEWGAME
                    self.selected_index = 0
                elif selected == 'QUIT':
                    return 'quit'
            elif symbol == key.ESCAPE:
                self.state = self.STATE_TITLE
        
        elif self.state == self.STATE_NEWGAME:
            if symbol in (key.UP, key.W):
                self.selected_index = (self.selected_index - 1) % len(self.newgame_menu)
                if self.sound:
                    self.sound.play('select')
            elif symbol in (key.DOWN, key.S):
                self.selected_index = (self.selected_index + 1) % len(self.newgame_menu)
                if self.sound:
                    self.sound.play('select')
            elif symbol == key.RETURN or symbol == key.ENTER:
                if self.sound:
                    self.sound.play('select')
                selected = self.newgame_menu[self.selected_index]
                if selected == 'SINGLE PLAYER':
                    self.stop_theme()
                    return 'start_single'
                elif selected == '2 PLAYER':
                    self.stop_theme()
                    return 'start_multi'
                elif selected == 'BACK':
                    self.state = self.STATE_MENU
                    self.selected_index = 0
            elif symbol == key.ESCAPE:
                self.state = self.STATE_MENU
                self.selected_index = 0
        
        return None
    
    def render(self):
        """Render the title screen. Returns all shapes/labels to keep alive."""
        render_objects = []
        batch = pyglet.graphics.Batch()
        
        # Fill with dark navy background using a rectangle
        bg = shapes.Rectangle(
            0, 0, self.screen_width, self.screen_height,
            color=self.colors['bg'], batch=batch
        )
        render_objects.append(bg)
        
        # Draw ocean/water area
        water_rect = shapes.Rectangle(
            0, 0, 
            self.screen_width, self.screen_height // 2 - 40,
            color=self.colors['bg_ocean'], batch=batch
        )
        render_objects.append(water_rect)
        
        # Draw scanlines
        render_objects.extend(self._draw_scanlines(batch))
        
        # Draw waves
        render_objects.extend(self._draw_waves(batch))
        
        # Draw the sailing ship
        # Ship bobbing animation
        bob_offset = math.sin(self.blink_timer * 0.005) * 5
        ship_shapes = self._draw_sailing_ship(
            batch,
            self.screen_width // 2, 
            500 + bob_offset,  # Lowered to sit on waves properly
            scale=4
        )
        render_objects.extend(ship_shapes)
        
        # Draw the batch first (background elements)
        batch.draw()
        
        # Draw title "Melee at Sea"
        self._render_cursive_title("Melee at Sea", self.screen_width // 2, self.screen_height - 80)
        
        # Draw based on state
        if self.state == self.STATE_TITLE:
            self._render_title_prompt()
        elif self.state == self.STATE_MENU:
            self._render_menu(self.main_menu)
        elif self.state == self.STATE_NEWGAME:
            self._render_menu(self.newgame_menu, "SELECT MODE")
    
    def _render_cursive_title(self, text, center_x, y):
        """Render the title with cursive pixel style matching reference images."""
        # Pixel patterns extracted from user's reference images
        pixel_letters = {
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
        }
        
        pixel_size = 4  # Larger pixels for elegant look
        spacing = 0     # Letters connect in cursive
        
        # Calculate total width
        total_width = 0
        for char in text:
            letter = pixel_letters.get(char, pixel_letters.get(char.lower(), pixel_letters[' ']))
            total_width += len(letter[0]) * pixel_size + spacing * pixel_size
        
        # Start position
        start_x = center_x - total_width // 2
        
        # Draw shadow first
        shadow_offset = 5
        x = start_x + shadow_offset
        for char in text:
            letter = pixel_letters.get(char, pixel_letters.get(char.lower(), pixel_letters[' ']))
            for row_idx, row in enumerate(letter):
                for col_idx, pixel in enumerate(row):
                    if pixel == '█':
                        rect = shapes.Rectangle(
                            x + col_idx * pixel_size,
                            y - row_idx * pixel_size - shadow_offset,
                            pixel_size, pixel_size,
                            color=self.colors['sepia_dark']
                        )
                        rect.draw()
                    elif pixel == '░':
                        rect = shapes.Rectangle(
                            x + col_idx * pixel_size,
                            y - row_idx * pixel_size - shadow_offset,
                            pixel_size, pixel_size,
                            color=self.colors['navy_dark']
                        )
                        rect.draw()
            x += (len(letter[0]) + spacing) * pixel_size
        
        # Draw main text
        x = start_x
        for char in text:
            letter = pixel_letters.get(char, pixel_letters.get(char.lower(), pixel_letters[' ']))
            for row_idx, row in enumerate(letter):
                for col_idx, pixel in enumerate(row):
                    if pixel == '█':
                        rect = shapes.Rectangle(
                            x + col_idx * pixel_size,
                            y - row_idx * pixel_size,
                            pixel_size, pixel_size,
                            color=self.colors['sepia_highlight']
                        )
                        rect.draw()
                    elif pixel == '░':
                        rect = shapes.Rectangle(
                            x + col_idx * pixel_size,
                            y - row_idx * pixel_size,
                            pixel_size, pixel_size,
                            color=self.colors['sepia_light']
                        )
                        rect.draw()
            x += (len(letter[0]) + spacing) * pixel_size
    
    def _render_title_prompt(self):
        """Render the 'Press ENTER' prompt."""
        if self.show_prompt:
            prompt = pyglet.text.Label(
                "~ Press ENTER ~",
                font_name=self.pixel_font_name,
                font_size=18,
                x=self.screen_width // 2, y=80,
                anchor_x='center', anchor_y='center',
                color=(*self.colors['sepia_light'], 255)
            )
            prompt.draw()
        
        # Tagline
        tagline = pyglet.text.Label(
            "A DOS-Style Naval Strategy Game",
            font_name=self.pixel_font_name,
            font_size=16,
            x=self.screen_width // 2, y=40,
            anchor_x='center', anchor_y='center',
            color=(*self.colors['sepia_mid'], 255)
        )
        tagline.draw()
    
    def _render_menu(self, menu_items, title=None):
        """Render a menu."""
        start_y = 180
        
        if title:
            title_label = pyglet.text.Label(
                title,
                font_name=self.pixel_font_name,
                font_size=20,
                x=self.screen_width // 2, y=start_y + 35,
                anchor_x='center', anchor_y='center',
                color=(*self.colors['sepia_light'], 255)
            )
            title_label.draw()
        
        for i, item in enumerate(menu_items):
            if i == self.selected_index:
                color = self.colors['sepia_highlight']
                prefix = ">> "
                suffix = " <<"
            else:
                color = self.colors['sepia_mid']
                prefix = "   "
                suffix = "   "
            
            text = f"{prefix}{item}{suffix}"
            label = pyglet.text.Label(
                text,
                font_name=self.pixel_font_name,
                font_size=24,
                x=self.screen_width // 2, y=start_y - i * 40,
                anchor_x='center', anchor_y='center',
                color=(*color, 255)
            )
            label.draw()
        
        # Navigation hint
        hint = pyglet.text.Label(
            "UP/DOWN: Select   ENTER: Confirm   ESC: Back",
            font_name=self.pixel_font_name,
            font_size=14,
            x=self.screen_width // 2, y=20,
            anchor_x='center', anchor_y='center',
            color=(*self.colors['sepia_dark'], 255)
        )
        hint.draw()
    
    def reset(self):
        """Reset to initial title state."""
        self.state = self.STATE_TITLE
        self.selected_index = 0
