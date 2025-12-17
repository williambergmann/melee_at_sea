"""
Ship - Warship entity for Melee at Sea (Pyglet version)
"""
import pyglet
from pyglet import shapes
import math


# Ship orientations (in degrees, clockwise from up)
UP = 0
RIGHT = 90
DOWN = 180
LEFT = 270

# Direction vectors for each orientation
DIRECTION_VECTORS = {
    UP: (0, 1),      # In pyglet, Y increases upward
    RIGHT: (1, 0),
    DOWN: (0, -1),
    LEFT: (-1, 0)
}


class Ship:
    """Represents a warship on the game board."""
    
    def __init__(self, x, y, length, orientation, team, board):
        """
        Initialize a ship.
        
        Args:
            x, y: Grid position of the ship's bow
            length: Length of the ship (2, 3, or 4)
            orientation: Direction the ship faces (UP, RIGHT, DOWN, LEFT)
            team: 'player' or 'enemy'
            board: Reference to the game board
        """
        self.x = x
        self.y = y
        self.length = length
        self.max_length = length
        self.orientation = orientation
        self.team = team
        self.board = board
        self.selected = False
        self.has_moved = False
        self.has_fired = False
        
        # Cannons per side based on length: L2=1, L3=2, L4=3
        self.max_cannons_per_side = length - 1
        self.cannons_per_side = self.max_cannons_per_side
        
        # Colors (DOS-style)
        self.colors = {
            'player': (0, 100, 255),      # Blue
            'enemy': (200, 50, 50)         # Red
        }
        self.cannon_color = (20, 20, 20)  # Black cannons
    
    @property
    def is_alive(self):
        """Check if the ship is still alive."""
        return self.cannons_per_side > 0
    
    @property
    def total_cannons(self):
        """Total number of cannons (both sides)."""
        return self.cannons_per_side * 2
    
    def get_cells(self):
        """Get all grid cells occupied by this ship."""
        cells = []
        dx, dy = DIRECTION_VECTORS[self.orientation]
        
        # Ship extends backwards from the bow position
        for i in range(self.length):
            cell_x = self.x - dx * i
            cell_y = self.y - dy * i
            cells.append((cell_x, cell_y))
        
        return cells
    
    def get_fire_zones(self, max_range=3):
        """
        Get all cells this ship can fire at (broadside zones).
        
        Returns cells perpendicular to the ship's orientation.
        """
        fire_cells = []
        ship_cells = self.get_cells()
        
        # Get perpendicular directions
        if self.orientation in (UP, DOWN):
            # Ship is vertical, fire left and right
            perp_dirs = [(1, 0), (-1, 0)]
        else:
            # Ship is horizontal, fire up and down
            perp_dirs = [(0, 1), (0, -1)]
        
        # For each ship cell, add fire zones in perpendicular directions
        for cell_x, cell_y in ship_cells:
            for pdx, pdy in perp_dirs:
                for distance in range(1, max_range + 1):
                    fire_x = cell_x + pdx * distance
                    fire_y = cell_y + pdy * distance
                    if self.board.is_valid_cell(fire_x, fire_y):
                        if (fire_x, fire_y) not in fire_cells:
                            fire_cells.append((fire_x, fire_y))
        
        return fire_cells
    
    def can_occupy(self, cells, all_ships):
        """Check if the ship can occupy the given cells."""
        # Check all cells are valid
        for cell_x, cell_y in cells:
            if not self.board.is_valid_cell(cell_x, cell_y):
                return False
        
        # Check for collisions with other ships
        for ship in all_ships:
            if ship is self or not ship.is_alive:
                continue
            other_cells = ship.get_cells()
            for cell in cells:
                if cell in other_cells:
                    return False
        
        return True
    
    def get_cells_at(self, new_x, new_y, new_orientation=None):
        """Get cells the ship would occupy at a different position/orientation."""
        if new_orientation is None:
            new_orientation = self.orientation
        
        cells = []
        dx, dy = DIRECTION_VECTORS[new_orientation]
        
        for i in range(self.length):
            cell_x = new_x - dx * i
            cell_y = new_y - dy * i
            cells.append((cell_x, cell_y))
        
        return cells
    
    def can_move_to(self, new_x, new_y, all_ships):
        """Check if the ship can move to a new position."""
        new_cells = self.get_cells_at(new_x, new_y)
        return self.can_occupy(new_cells, all_ships)
    
    def move(self, direction, all_ships):
        """
        Move the ship in a direction.
        
        Args:
            direction: 'forward', 'backward', 'left', 'right'
            all_ships: List of all ships for collision detection
            
        Returns:
            True if move was successful
        """
        dx, dy = 0, 0
        
        if direction == 'forward':
            dx, dy = DIRECTION_VECTORS[self.orientation]
        elif direction == 'backward':
            fx, fy = DIRECTION_VECTORS[self.orientation]
            dx, dy = -fx, -fy
        elif direction == 'left':
            if self.orientation == UP:
                dx, dy = -1, 0
            elif self.orientation == RIGHT:
                dx, dy = 0, 1
            elif self.orientation == DOWN:
                dx, dy = 1, 0
            elif self.orientation == LEFT:
                dx, dy = 0, -1
        elif direction == 'right':
            if self.orientation == UP:
                dx, dy = 1, 0
            elif self.orientation == RIGHT:
                dx, dy = 0, -1
            elif self.orientation == DOWN:
                dx, dy = -1, 0
            elif self.orientation == LEFT:
                dx, dy = 0, 1
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        if self.can_move_to(new_x, new_y, all_ships):
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def move_absolute(self, dx, dy, all_ships):
        """
        Move the ship in an absolute screen direction.
        
        Args:
            dx: Horizontal movement (-1=left, 1=right)
            dy: Vertical movement (-1=down, 1=up)
            all_ships: List of all ships for collision detection
            
        Returns:
            True if move was successful
        """
        new_x = self.x + dx
        new_y = self.y + dy
        
        if self.can_move_to(new_x, new_y, all_ships):
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def can_rotate_to(self, new_orientation, all_ships):
        """Check if the ship can rotate to a new orientation."""
        new_cells = self.get_cells_at(self.x, self.y, new_orientation)
        return self.can_occupy(new_cells, all_ships)
    
    def rotate(self, direction, all_ships):
        """
        Rotate the ship.
        
        Args:
            direction: 'cw' (clockwise) or 'ccw' (counter-clockwise)
            all_ships: List of all ships for collision detection
            
        Returns:
            True if rotation was successful
        """
        if direction == 'cw':
            new_orientation = (self.orientation + 90) % 360
        else:
            new_orientation = (self.orientation - 90) % 360
        
        if self.can_rotate_to(new_orientation, all_ships):
            self.orientation = new_orientation
            return True
        return False
    
    def take_damage(self, amount=1):
        """Apply damage to the ship, reducing cannons. Ship sinks when no cannons remain."""
        self.cannons_per_side = max(0, self.cannons_per_side - amount)
        return self.cannons_per_side <= 0  # Returns True if ship is destroyed
    
    def render(self, batch=None):
        """Render the ship on the game board - matching reference design."""
        if not self.is_alive:
            return []
        
        color = self.colors.get(self.team, (128, 128, 128))
        cells = self.get_cells()
        cell_size = self.board.cell_size
        render_shapes = []
        
        # Determine which segments get cannons (skip bow, distribute on body)
        body_segments = len(cells) - 1
        cannon_positions = []
        if self.cannons_per_side > 0 and body_segments > 0:
            for c in range(min(self.cannons_per_side, body_segments)):
                cannon_positions.append(1 + c)
        
        # Ship dimensions - wider body to match reference
        body_width = cell_size * 0.6  # Wider body
        cannon_length = cell_size * 0.4  # Longer cannons
        cannon_thickness = cell_size * 0.15
        
        for i, (cell_x, cell_y) in enumerate(cells):
            screen_x, screen_y = self.board.grid_to_screen(cell_x, cell_y)
            
            if self.orientation in (UP, DOWN):
                # Vertical ship
                half_width = body_width / 2
                segment_height = cell_size * 0.9
                
                if i == 0:  # Bow (pointed triangle)
                    if self.orientation == UP:
                        # Triangle pointing up
                        triangle = shapes.Triangle(
                            screen_x, screen_y + segment_height / 2,  # Top point
                            screen_x - half_width, screen_y - segment_height / 3,
                            screen_x + half_width, screen_y - segment_height / 3,
                            color=color, batch=batch
                        )
                    else:  # DOWN
                        # Triangle pointing down
                        triangle = shapes.Triangle(
                            screen_x, screen_y - segment_height / 2,  # Bottom point
                            screen_x - half_width, screen_y + segment_height / 3,
                            screen_x + half_width, screen_y + segment_height / 3,
                            color=color, batch=batch
                        )
                    render_shapes.append(triangle)
                else:
                    # Body segment (wide rectangle)
                    rect = shapes.Rectangle(
                        screen_x - half_width,
                        screen_y - segment_height / 2,
                        body_width,
                        segment_height,
                        color=color, batch=batch
                    )
                    render_shapes.append(rect)
                
                # Black cannons on sides (horizontal)
                if i in cannon_positions:
                    # Left cannon
                    left_cannon = shapes.Rectangle(
                        screen_x - half_width - cannon_length,
                        screen_y - cannon_thickness / 2,
                        cannon_length, cannon_thickness,
                        color=self.cannon_color, batch=batch
                    )
                    # Right cannon
                    right_cannon = shapes.Rectangle(
                        screen_x + half_width,
                        screen_y - cannon_thickness / 2,
                        cannon_length, cannon_thickness,
                        color=self.cannon_color, batch=batch
                    )
                    render_shapes.extend([left_cannon, right_cannon])
            
            else:  # LEFT or RIGHT
                # Horizontal ship
                half_height = body_width / 2
                segment_width = cell_size * 0.9
                
                if i == 0:  # Bow (pointed triangle)
                    if self.orientation == RIGHT:
                        # Triangle pointing right
                        triangle = shapes.Triangle(
                            screen_x + segment_width / 2, screen_y,  # Right point
                            screen_x - segment_width / 3, screen_y + half_height,
                            screen_x - segment_width / 3, screen_y - half_height,
                            color=color, batch=batch
                        )
                    else:  # LEFT
                        # Triangle pointing left
                        triangle = shapes.Triangle(
                            screen_x - segment_width / 2, screen_y,  # Left point
                            screen_x + segment_width / 3, screen_y + half_height,
                            screen_x + segment_width / 3, screen_y - half_height,
                            color=color, batch=batch
                        )
                    render_shapes.append(triangle)
                else:
                    # Body segment (wide rectangle)
                    rect = shapes.Rectangle(
                        screen_x - segment_width / 2,
                        screen_y - half_height,
                        segment_width,
                        body_width,
                        color=color, batch=batch
                    )
                    render_shapes.append(rect)
                
                # Black cannons (vertical for horizontal ships)
                if i in cannon_positions:
                    # Top cannon
                    top_cannon = shapes.Rectangle(
                        screen_x - cannon_thickness / 2,
                        screen_y + half_height,
                        cannon_thickness, cannon_length,
                        color=self.cannon_color, batch=batch
                    )
                    # Bottom cannon
                    bottom_cannon = shapes.Rectangle(
                        screen_x - cannon_thickness / 2,
                        screen_y - half_height - cannon_length,
                        cannon_thickness, cannon_length,
                        color=self.cannon_color, batch=batch
                    )
                    render_shapes.extend([top_cannon, bottom_cannon])
        
        # Draw selection indicator
        if self.selected:
            bow_x, bow_y = self.board.grid_to_screen(self.x, self.y)
            # Draw circle around selected ship
            circle = shapes.Arc(
                bow_x, bow_y, cell_size // 2 + 4,
                color=(255, 255, 0), batch=batch
            )
            render_shapes.append(circle)
        
        # If no batch was provided, draw all shapes immediately
        if batch is None:
            for shape in render_shapes:
                shape.draw()
        
        return render_shapes
