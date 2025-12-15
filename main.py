#!/usr/bin/env python3
"""
Melee at Sea - A DOS-style turn-based naval strategy game

Controls:
- Click to select a ship
- W/A/S/D or Arrow keys to move
- Q/E to rotate
- SPACE or F to fire broadside
- ENTER to end turn
- R to restart (game over)
- ESC to quit
"""
import pyglet
from pyglet.window import key
from pyglet import shapes
import sys

from game.board import Board
from game.ship import Ship, UP, DOWN, LEFT, RIGHT
from game.combat import Combat
from game.ai import AI
from game.ui import UI
from game.sound import SoundSystem
from game.title_screen import TitleScreen


# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# DOS-style background color (cream/off-white like the reference)
BG_COLOR = (240, 235, 220)
DOT_COLOR = (40, 40, 40)


class GameState:
    """Enum-like class for game states."""
    TITLE = "TITLE"
    PLAYER_SELECT = "SELECT SHIP"
    PLAYER_MOVE = "MOVE/ROTATE"
    PLAYER_FIRE = "FIRE"
    ENEMY_TURN = "ENEMY TURN"
    PLAYER2_SELECT = "P2 SELECT SHIP"
    PLAYER2_MOVE = "P2 MOVE/ROTATE"
    PLAYER2_FIRE = "P2 FIRE"
    GAME_OVER = "GAME OVER"


class GameMode:
    """Enum-like class for game modes."""
    SINGLE_PLAYER = "single"
    TWO_PLAYER = "two_player"


class Game(pyglet.window.Window):
    """Main game class for Melee at Sea."""
    
    def __init__(self):
        """Initialize the game."""
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, caption="Melee at Sea")
        
        # Initialize game components - use larger cells to fill screen
        # 800/20 = 40 for width, 600/15 = 40 for height
        self.board = Board(cols=20, rows=15, cell_size=40)
        self.board.set_offset(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.combat = Combat(self.board)
        self.ai = AI(self.combat)
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Initialize sound effects
        self.sound = SoundSystem()
        
        # Initialize title screen
        self.title_screen = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT, self.sound)
        
        # Game state - start at title screen
        self.state = GameState.TITLE
        self.selected_ship = None
        self.player_won = False
        
        # Game mode (single player vs 2-player)
        self.game_mode = GameMode.SINGLE_PLAYER
        
        # Message system
        self.message = ""
        self.message_timer = 0
        
        # AI turn timing
        self.ai_action_timer = 0
        self.ai_actions = []
        self.ai_action_index = 0
        
        # Initialize ships
        self.init_ships()
        
        # Schedule update
        pyglet.clock.schedule_interval(self.update, 1.0 / FPS)
    
    def init_ships(self):
        """Set up initial ship positions with randomized y-order."""
        import random
        
        self.player_ships = []
        self.enemy_ships = []
        
        # Board is 20 cols x 15 rows (valid: 0-19, 0-14)
        # Ship configs: (length, count)
        ship_configs = [(2, 2), (3, 3), (4, 2)]  # 2x L2, 3x L3, 2x L4
        
        # Create all ship lengths in random order
        all_lengths = []
        for length, count in ship_configs:
            all_lengths.extend([length] * count)
        random.shuffle(all_lengths)
        
        # Available y positions (0-14, spaced by 2 to avoid overlap)
        player_y_positions = list(range(0, 14, 2))  # 0, 2, 4, 6, 8, 10, 12
        enemy_y_positions = list(range(0, 14, 2))
        random.shuffle(player_y_positions)
        random.shuffle(enemy_y_positions)
        
        # Place player ships on left side (facing RIGHT, bow at x=0, body extends left... wait no)
        # For RIGHT-facing ships: body extends to lower x values
        # So bow at x=length-1 means body goes from length-1 down to 0
        for i, length in enumerate(all_lengths):
            y = player_y_positions[i % len(player_y_positions)]
            # Bow position for RIGHT-facing: x = length-1 so body extends to x=0
            self.player_ships.append(Ship(length - 1, y, length, RIGHT, 'player', self.board))
        
        # Place enemy ships on right side (facing LEFT)
        # For LEFT-facing ships: body extends to higher x values
        # So bow at x = 19 - (length-1) = 20-length means body extends to x=19
        random.shuffle(all_lengths)
        for i, length in enumerate(all_lengths):
            y = enemy_y_positions[i % len(enemy_y_positions)]
            bow_x = 20 - length  # So rightmost segment is at x=19
            self.enemy_ships.append(Ship(bow_x, y, length, LEFT, 'enemy', self.board))
        
        self.all_ships = self.player_ships + self.enemy_ships
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.state = GameState.PLAYER_SELECT
        self.selected_ship = None
        self.player_won = False
        self.message = ""
        self.message_timer = 0
        self.init_ships()
    
    def start_game(self, mode):
        """Start a new game with the specified mode."""
        self.game_mode = mode
        self.reset_game()
        if mode == GameMode.TWO_PLAYER:
            self.show_message("PLAYER 1'S TURN - Select a ship!", 3000)
        else:
            self.show_message("Select a ship to begin!", 3000)
    
    def show_message(self, text, duration=2000):
        """Show a temporary message."""
        self.message = text
        self.message_timer = duration
    
    def start_player_turn(self):
        """Begin a new player turn."""
        self.state = GameState.PLAYER_SELECT
        self.selected_ship = None
        
        # Reset ship action flags
        for ship in self.player_ships:
            ship.has_moved = False
            ship.has_fired = False
            ship.selected = False
    
    def start_enemy_turn(self):
        """Begin the enemy's turn (AI or Player 2)."""
        if self.game_mode == GameMode.TWO_PLAYER:
            # In 2-player mode, switch to Player 2's turn
            self.start_player2_turn()
        else:
            # AI turn in single player mode
            self.state = GameState.ENEMY_TURN
            self.selected_ship = None
            
            # Reset enemy ship flags
            for ship in self.enemy_ships:
                ship.has_moved = False
                ship.has_fired = False
            
            # Get AI actions
            self.ai_actions = self.ai.take_turn(self.enemy_ships, self.player_ships, self.all_ships)
            self.ai_action_index = 0
            self.ai_action_timer = 500  # Delay before showing actions
    
    def start_player2_turn(self):
        """Begin Player 2's turn in 2-player mode."""
        self.state = GameState.PLAYER2_SELECT
        self.selected_ship = None
        
        # Reset Player 2 (enemy) ship action flags
        for ship in self.enemy_ships:
            ship.has_moved = False
            ship.has_fired = False
            ship.selected = False
        
        self.show_message("PLAYER 2'S TURN!", 1500)
    
    def check_game_over(self):
        """Check if the game has ended."""
        player_alive = any(s.is_alive for s in self.player_ships)
        enemy_alive = any(s.is_alive for s in self.enemy_ships)
        
        if not enemy_alive:
            self.state = GameState.GAME_OVER
            self.player_won = True
            return True
        elif not player_alive:
            self.state = GameState.GAME_OVER
            self.player_won = False
            return True
        return False
    
    def handle_click(self, x, y):
        """Handle mouse click."""
        if self.state == GameState.GAME_OVER:
            return
        
        grid_x, grid_y = self.board.screen_to_grid(x, y)
        
        if self.state == GameState.PLAYER_SELECT:
            # Try to select a player 1 ship
            for ship in self.player_ships:
                if not ship.is_alive:
                    continue
                if (grid_x, grid_y) in ship.get_cells():
                    self.select_ship(ship, player=1)
                    break
        
        elif self.state == GameState.PLAYER2_SELECT:
            # Try to select a player 2 ship (enemy ships in 2P mode)
            for ship in self.enemy_ships:
                if not ship.is_alive:
                    continue
                if (grid_x, grid_y) in ship.get_cells():
                    self.select_ship(ship, player=2)
                    break
        
        elif self.state == GameState.PLAYER_FIRE:
            # Player 1 Try to fire at clicked cell
            if self.selected_ship and not self.selected_ship.has_fired:
                fire_zones = self.selected_ship.get_fire_zones()
                if (grid_x, grid_y) in fire_zones:
                    hit_ship, destroyed = self.combat.fire(
                        self.selected_ship, (grid_x, grid_y), self.all_ships
                    )
                    self.selected_ship.has_fired = True
                    
                    if hit_ship:
                        if destroyed:
                            self.show_message("SHIP DESTROYED!")
                        else:
                            self.show_message("HIT!")
                        self.check_game_over()
                    else:
                        self.show_message("MISS!")
        
        elif self.state == GameState.PLAYER2_FIRE:
            # Player 2 Try to fire at clicked cell
            if self.selected_ship and not self.selected_ship.has_fired:
                fire_zones = self.selected_ship.get_fire_zones()
                if (grid_x, grid_y) in fire_zones:
                    hit_ship, destroyed = self.combat.fire(
                        self.selected_ship, (grid_x, grid_y), self.all_ships
                    )
                    self.selected_ship.has_fired = True
                    
                    if hit_ship:
                        if destroyed:
                            self.show_message("SHIP DESTROYED!")
                        else:
                            self.show_message("HIT!")
                        self.check_game_over()
                    else:
                        self.show_message("MISS!")
    
    def select_ship(self, ship, player=1):
        """Select a ship for control."""
        if self.selected_ship:
            self.selected_ship.selected = False
        
        self.selected_ship = ship
        ship.selected = True
        
        if player == 1:
            self.state = GameState.PLAYER_MOVE
        else:
            self.state = GameState.PLAYER2_MOVE

    
    def on_key_press(self, symbol, modifiers):
        """Handle keyboard input."""
        # Title screen handling
        if self.state == GameState.TITLE:
            result = self.title_screen.handle_key(symbol)
            if result == 'start_single':
                self.start_game(GameMode.SINGLE_PLAYER)
            elif result == 'start_multi':
                self.start_game(GameMode.TWO_PLAYER)
            elif result == 'quit':
                self.close()
            if symbol == key.ESCAPE:
                if self.title_screen.state == self.title_screen.STATE_TITLE:
                    self.close()
            return
        
        if self.state == GameState.GAME_OVER:
            if symbol == key.R:
                # Restart with same game mode
                self.start_game(self.game_mode)
            elif symbol == key.ESCAPE:
                self.close()
            return
        
        if symbol == key.ESCAPE:
            self.close()
            return

        # Player 1 SELECT phase - simple enter to end turn
        if self.state == GameState.PLAYER_SELECT:
            if symbol == key.RETURN or symbol == key.ENTER:
                self.start_enemy_turn()
                
        # Player 1 MOVE phase - free movement until ENTER confirms
        if self.state == GameState.PLAYER_MOVE:
            if self.selected_ship:
                moved = False
                
                # Movement - forward/backward (1 space per keypress, unlimited presses)
                if symbol in (key.W, key.UP):
                    moved = self.selected_ship.move('forward', self.all_ships)
                elif symbol in (key.S, key.DOWN):
                    moved = self.selected_ship.move('backward', self.all_ships)
                
                # Rotation - 90 degrees per keypress (can rotate multiple times)
                elif symbol == key.Q:
                    moved = self.selected_ship.rotate('ccw', self.all_ships)
                elif symbol == key.E:
                    moved = self.selected_ship.rotate('cw', self.all_ships)
                elif symbol in (key.A, key.LEFT):
                    moved = self.selected_ship.rotate('ccw', self.all_ships)
                elif symbol in (key.D, key.RIGHT):
                    moved = self.selected_ship.rotate('cw', self.all_ships)
                
                if moved:
                    self.sound.play('move')
            
            # ENTER confirms move and goes to fire phase
            if symbol == key.RETURN or symbol == key.ENTER:
                if self.selected_ship:
                    self.selected_ship.selected = False
                    self.selected_ship = None
                self.state = GameState.PLAYER_FIRE
                self.show_message("SELECT SHIP TO FIRE", 2500)
                return  # Prevent fall-through to other handlers
        
        # Player 1 FIRE phase - select any ship to fire
        if self.state == GameState.PLAYER_FIRE:
            # Fire with selected ship
            if symbol in (key.SPACE, key.F):
                if self.selected_ship and not self.selected_ship.has_fired:
                    hits = self.combat.fire_broadside(self.selected_ship, self.all_ships)
                    self.selected_ship.has_fired = True
                    
                    if hits:
                        destroyed_count = sum(1 for _, d in hits if d)
                        hit_count = len(hits) - destroyed_count
                        
                        if destroyed_count > 0:
                            self.show_message(f"{destroyed_count} SHIP(S) DESTROYED!")
                            self.sound.play('destroy')
                        elif hit_count > 0:
                            self.show_message(f"{hit_count} HIT(S)!", 2500)
                            self.sound.play('hit')
                        
                        self.check_game_over()
                    else:
                        self.show_message("NO TARGETS IN RANGE!", 2500)
                    
                    self.sound.play('fire')
                    
                    # End turn after firing
                    self.selected_ship.selected = False
                    self.selected_ship = None
                    self.selected_ship = None
                    self.start_enemy_turn()
                    
            # ENTER ends turn without firing
            if symbol == key.RETURN or symbol == key.ENTER:
                self.start_enemy_turn()
        
        # Player 2 MOVE phase - free movement until ENTER confirms
        if self.state == GameState.PLAYER2_MOVE:
            if self.selected_ship:
                moved = False
                
                if symbol in (key.W, key.UP):
                    moved = self.selected_ship.move('forward', self.all_ships)
                elif symbol in (key.S, key.DOWN):
                    moved = self.selected_ship.move('backward', self.all_ships)
                elif symbol == key.Q:
                    moved = self.selected_ship.rotate('ccw', self.all_ships)
                elif symbol == key.E:
                    moved = self.selected_ship.rotate('cw', self.all_ships)
                elif symbol in (key.A, key.LEFT):
                    moved = self.selected_ship.rotate('ccw', self.all_ships)
                elif symbol in (key.D, key.RIGHT):
                    moved = self.selected_ship.rotate('cw', self.all_ships)
                
                if moved:
                    self.sound.play('move')
            
            # ENTER confirms move and goes to fire phase
            if symbol == key.RETURN or symbol == key.ENTER:
                if self.selected_ship:
                    self.selected_ship.selected = False
                    self.selected_ship = None
                self.state = GameState.PLAYER2_FIRE
                self.show_message("P2: SELECT SHIP TO FIRE", 1500)
                return  # Prevent fall-through
        
        # Player 2 FIRE phase
        if self.state == GameState.PLAYER2_FIRE:
            if symbol in (key.SPACE, key.F):
                if self.selected_ship and not self.selected_ship.has_fired:
                    hits = self.combat.fire_broadside(self.selected_ship, self.all_ships)
                    self.selected_ship.has_fired = True
                    
                    if hits:
                        destroyed_count = sum(1 for _, d in hits if d)
                        hit_count = len(hits) - destroyed_count
                        
                        if destroyed_count > 0:
                            self.show_message(f"{destroyed_count} SHIP(S) DESTROYED!")
                            self.sound.play('destroy')
                        elif hit_count > 0:
                            self.show_message(f"{hit_count} HIT(S)!", 2500)
                            self.sound.play('hit')
                        
                        self.check_game_over()
                    else:
                        self.show_message("NO TARGETS IN RANGE!", 2500)
                    
                    self.sound.play('fire')
                    
                    self.selected_ship.selected = False
                    self.selected_ship = None
                    self.start_player_turn()
                    self.show_message("PLAYER 1'S TURN!", 2500)
            
            # ENTER ends turn without firing
            if symbol == key.RETURN or symbol == key.ENTER:
                self.start_player_turn()
                self.show_message("PLAYER 1'S TURN!", 1500)
        

        
        # Deselect
        if symbol == key.TAB:
            if self.selected_ship:
                self.selected_ship.selected = False
                self.selected_ship = None
                if self.state in (GameState.PLAYER_MOVE, GameState.PLAYER_FIRE):
                    self.state = GameState.PLAYER_SELECT
                elif self.state in (GameState.PLAYER2_MOVE, GameState.PLAYER2_FIRE):
                    self.state = GameState.PLAYER2_SELECT
    
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click."""
        if button == 1:  # Left click
            self.handle_click(x, y)
    
    def update(self, dt):
        """Update game state."""
        # Convert dt to milliseconds for consistency
        dt_ms = dt * 1000
        
        # Update title screen if active
        if self.state == GameState.TITLE:
            self.title_screen.update(dt)
            return
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt_ms
            if self.message_timer <= 0:
                self.message = ""
        
        # Handle AI turn
        if self.state == GameState.ENEMY_TURN:
            self.ai_action_timer -= dt_ms
            
            if self.ai_action_timer <= 0:
                if self.ai_action_index < len(self.ai_actions):
                    action = self.ai_actions[self.ai_action_index]
                    self.show_message(action, 1000)
                    self.ai_action_index += 1
                    self.ai_action_timer = 800
                else:
                    # AI turn complete
                    if not self.check_game_over():
                        self.start_player_turn()
                        self.show_message("YOUR TURN!", 1500)
    
    def on_draw(self):
        """Render the game."""
        self.clear()
        
        # Render title screen if active
        if self.state == GameState.TITLE:
            self.title_screen.render()
            return
        
        # Clear screen with DOS-style background
        bg = shapes.Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, color=BG_COLOR)
        bg.draw()
        
        # Draw the dot grid
        self.board.render()
        
        # Draw fire zones if a ship is selected and can fire
        if self.selected_ship and self.state in (GameState.PLAYER_FIRE, GameState.PLAYER2_FIRE):
            if not self.selected_ship.has_fired and self.selected_ship.cannons_per_side > 0:
                # Show side fire zones (perpendicular to ship)
                fire_zones = self.combat.get_side_fire_zones(self.selected_ship)
                self.board.clear_highlights()
                for fx, fy in fire_zones:
                    self.board.add_highlight(fx, fy, (255, 100, 100), 80)
        else:
            self.board.clear_highlights()
        
        # Draw highlights
        for highlight in self.board.highlights:
            highlight.draw()
        
        # Draw all ships
        for ship in self.all_ships:
            ship.render()
        
        # Draw UI - determine whose turn it is
        is_player1_turn = self.state in (GameState.PLAYER_SELECT, GameState.PLAYER_MOVE, GameState.PLAYER_FIRE)
        is_player2_turn = self.state in (GameState.PLAYER2_SELECT, GameState.PLAYER2_MOVE, GameState.PLAYER2_FIRE)
        
        if self.game_mode == GameMode.TWO_PLAYER:
            self.ui.render_turn_indicator_2p(
                1 if is_player1_turn else 2,
                self.state
            )
        else:
            self.ui.render_turn_indicator(
                self.state != GameState.ENEMY_TURN,
                self.state if self.state != GameState.ENEMY_TURN else ""
            )
        
        # Draw ship info panel if a ship is selected
        if self.selected_ship:
            self.ui.render_ship_info(self.selected_ship, 10, SCREEN_HEIGHT - 60)
        
        # Draw instructions
        if self.state in (GameState.PLAYER_SELECT, GameState.PLAYER2_SELECT):
            instructions = ["Click ship to select", "ENTER: End turn", "ESC: Quit"]
        elif self.state in (GameState.PLAYER_MOVE, GameState.PLAYER2_MOVE):
            instructions = ["WASD/Arrows: Move", "Q/E: Rotate", "ENTER: Confirm Move", "TAB: Deselect"]
        elif self.state in (GameState.PLAYER_FIRE, GameState.PLAYER2_FIRE):
            instructions = ["SPACE: Fire broadside", "Click target to fire", "ENTER: End turn"]
        else:
            instructions = []
        
        if instructions:
            self.ui.render_instructions(instructions)
        
        # Draw message
        if self.message:
            self.ui.render_message(self.message)
        
        # Draw game over screen
        if self.state == GameState.GAME_OVER:
            self.ui.render_game_over(self.player_won)


def main():
    """Entry point."""
    game = Game()
    pyglet.app.run()


if __name__ == "__main__":
    main()
