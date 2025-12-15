"""
UI - DOS-style user interface elements for Melee at Sea (Pyglet version)
"""
import pyglet
from pyglet import shapes


class UI:
    """DOS-style user interface renderer."""
    
    def __init__(self, screen_width, screen_height):
        """
        Initialize the UI.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # DOS-style colors
        self.colors = {
            'text': (255, 255, 255, 255),
            'text_dim': (150, 150, 150, 255),
            'highlight': (255, 255, 0, 255),
            'player': (0, 100, 255, 255),
            'enemy': (255, 0, 200, 255),
            'fire_zone': (255, 100, 100),
            'move_zone': (100, 255, 100),
            'background': (20, 20, 30, 255),
            'panel': (40, 40, 60, 255)
        }
        
        # Labels (will be created as needed)
        self.labels = {}
        self.render_elements = []
    
    def _create_label(self, text, x, y, font_size=24, color=(255, 255, 255, 255), 
                      anchor_x='center', anchor_y='center', bold=False):
        """Create a pyglet label."""
        # Note: bold parameter not supported in pyglet 2.x, ignored
        return pyglet.text.Label(
            text,
            font_name='Courier New',  # Mono font for DOS feel
            font_size=font_size,
            x=x, y=y,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            color=color
        )
    
    def render_title(self, text, y_offset=None):
        """Render a title at the top of the screen."""
        if y_offset is None:
            y_offset = self.screen_height - 30
        
        label = self._create_label(
            text,
            self.screen_width // 2,
            y_offset,
            font_size=32,
            color=self.colors['text'],
            bold=True
        )
        return [label]
    
    def render_turn_indicator(self, is_player_turn, state=""):
        """Render the current turn indicator."""
        if is_player_turn:
            text = "YOUR TURN"
            if state:
                text += f" - {state}"
            color = self.colors['player']
        else:
            text = "ENEMY TURN"
            color = self.colors['enemy']
        
        label = self._create_label(
            text,
            self.screen_width // 2,
            self.screen_height - 25,
            font_size=28,
            color=color,
            bold=True
        )
        label.draw()
    
    def render_turn_indicator_2p(self, current_player, state=""):
        """Render turn indicator for 2-player mode."""
        if current_player == 1:
            text = "PLAYER 1's TURN"
            color = self.colors['player']
        else:
            text = "PLAYER 2's TURN"
            color = self.colors['enemy']
        
        if state:
            text += f" - {state}"
        
        label = self._create_label(
            text,
            self.screen_width // 2,
            self.screen_height - 25,
            font_size=28,
            color=color,
            bold=True
        )
        label.draw()
    
    def render_instructions(self, instructions):
        """Render control instructions at the bottom."""
        text = " | ".join(instructions)
        label = self._create_label(
            text,
            self.screen_width // 2,
            20,
            font_size=14,
            color=self.colors['text_dim']
        )
        label.draw()
    
    def render_ship_info(self, ship, x, y):
        """Render information about a selected ship."""
        if not ship:
            return
        
        # Background panel
        panel = shapes.Rectangle(
            x, y, 160, 90,
            color=(40, 40, 60)
        )
        panel.draw()
        
        border = shapes.BorderedRectangle(
            x, y, 160, 90,
            border=2,
            color=(40, 40, 60),
            border_color=(150, 150, 150)
        )
        border.draw()
        
        # Ship info
        team_text = "YOUR SHIP" if ship.team == 'player' else "ENEMY SHIP"
        team_color = self.colors['player'] if ship.team == 'player' else self.colors['enemy']
        
        team_label = self._create_label(
            team_text, x + 10, y + 70,
            font_size=14, color=team_color,
            anchor_x='left'
        )
        team_label.draw()
        
        # Cannon display - shows remaining cannons per side
        cannon_text = f"Cannons: {'█' * ship.cannons_per_side}{'░' * (ship.max_cannons_per_side - ship.cannons_per_side)}"
        cannon_label = self._create_label(
            cannon_text, x + 10, y + 45,
            font_size=14, color=self.colors['text'],
            anchor_x='left'
        )
        cannon_label.draw()
        
        # Status
        status_parts = []
        if ship.has_moved:
            status_parts.append("Moved")
        if ship.has_fired:
            status_parts.append("Fired")
        
        if status_parts:
            status_text = ", ".join(status_parts)
            status_label = self._create_label(
                status_text, x + 10, y + 20,
                font_size=12, color=self.colors['text_dim'],
                anchor_x='left'
            )
            status_label.draw()
    
    def render_game_over(self, player_won):
        """Render the game over screen."""
        # Darken overlay
        overlay = shapes.Rectangle(
            0, 0, self.screen_width, self.screen_height,
            color=(0, 0, 0)
        )
        overlay.opacity = 180
        overlay.draw()
        
        # Victory/Defeat text
        if player_won:
            text = "VICTORY!"
            color = self.colors['player']
            subtext = "All enemy ships destroyed!"
        else:
            text = "DEFEAT!"
            color = self.colors['enemy']
            subtext = "Your fleet has been destroyed!"
        
        main_label = self._create_label(
            text,
            self.screen_width // 2,
            self.screen_height // 2 + 40,
            font_size=48,
            color=color,
            bold=True
        )
        main_label.draw()
        
        sub_label = self._create_label(
            subtext,
            self.screen_width // 2,
            self.screen_height // 2 - 10,
            font_size=24,
            color=self.colors['text']
        )
        sub_label.draw()
        
        restart_label = self._create_label(
            "Press R to restart or ESC to quit",
            self.screen_width // 2,
            self.screen_height // 2 - 60,
            font_size=16,
            color=self.colors['text_dim']
        )
        restart_label.draw()
    
    def render_message(self, message):
        """Render a temporary message in the center of the screen."""
        if not message:
            return
        
        # Background
        text_width = len(message) * 12 + 40
        bg = shapes.Rectangle(
            (self.screen_width - text_width) // 2,
            self.screen_height // 2 - 20,
            text_width,
            40,
            color=(40, 40, 60)
        )
        bg.draw()
        
        border = shapes.BorderedRectangle(
            (self.screen_width - text_width) // 2,
            self.screen_height // 2 - 20,
            text_width,
            40,
            border=2,
            color=(40, 40, 60),
            border_color=(255, 255, 0)
        )
        border.draw()
        
        label = self._create_label(
            message,
            self.screen_width // 2,
            self.screen_height // 2,
            font_size=20,
            color=self.colors['highlight'],
            bold=True
        )
        label.draw()
    
    def render_placement_info(self, ships_remaining, current_orientation):
        """Render ship placement phase information."""
        elements = []
        
        # Title
        title = self._create_label(
            "PLACE YOUR FLEET",
            self.screen_width // 2,
            self.screen_height - 25,
            font_size=28,
            color=self.colors['player'],
            bold=True
        )
        elements.append(title)
        
        # Ships remaining
        remaining = self._create_label(
            f"Ships remaining: {ships_remaining}",
            self.screen_width // 2,
            self.screen_height - 55,
            font_size=18,
            color=self.colors['text']
        )
        elements.append(remaining)
        
        # Orientation
        orient_names = {0: "UP", 90: "RIGHT", 180: "DOWN", 270: "LEFT"}
        orient_text = f"Direction: {orient_names.get(current_orientation, '?')}"
        orient_label = self._create_label(
            orient_text,
            self.screen_width // 2,
            self.screen_height - 80,
            font_size=16,
            color=self.colors['text_dim']
        )
        elements.append(orient_label)
        
        return elements
