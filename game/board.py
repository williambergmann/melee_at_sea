"""
Game Board - Dot-grid game board for Melee at Sea (Pyglet version)
"""
import pyglet
from pyglet import shapes


class Board:
    """Represents the game board with a dot-grid pattern."""
    
    def __init__(self, cols=20, rows=15, cell_size=32):
        """
        Initialize the game board.
        
        Args:
            cols: Number of columns in the grid
            rows: Number of rows in the grid
            cell_size: Size of each cell in pixels
        """
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.width = cols * cell_size
        self.height = rows * cell_size
        
        # Offset to center the grid on screen
        self.offset_x = 0
        self.offset_y = 0
        
        # Batch for efficient rendering
        self.batch = pyglet.graphics.Batch()
        self.dots = []
        self.highlights = []
    
    def set_offset(self, screen_width, screen_height):
        """Center the grid on the screen."""
        self.offset_x = (screen_width - self.width) // 2
        self.offset_y = (screen_height - self.height) // 2
        self._create_dots()
    
    def _create_dots(self):
        """Create dot shapes for the grid."""
        self.dots = []
        dot_color = (40, 40, 40)
        
        for row in range(self.rows + 1):
            for col in range(self.cols + 1):
                x = self.offset_x + col * self.cell_size
                y = self.offset_y + row * self.cell_size
                dot = shapes.Circle(x, y, 2, color=dot_color, batch=self.batch)
                self.dots.append(dot)
    
    def grid_to_screen(self, grid_x, grid_y):
        """Convert grid coordinates to screen coordinates."""
        screen_x = self.offset_x + grid_x * self.cell_size + self.cell_size // 2
        screen_y = self.offset_y + grid_y * self.cell_size + self.cell_size // 2
        return screen_x, screen_y
    
    def screen_to_grid(self, screen_x, screen_y):
        """Convert screen coordinates to grid coordinates."""
        grid_x = (screen_x - self.offset_x) // self.cell_size
        grid_y = (screen_y - self.offset_y) // self.cell_size
        return grid_x, grid_y
    
    def is_valid_cell(self, grid_x, grid_y):
        """Check if a cell is within the grid bounds."""
        return 0 <= grid_x < self.cols and 0 <= grid_y < self.rows
    
    def clear_highlights(self):
        """Clear all cell highlights."""
        self.highlights = []
    
    def add_highlight(self, grid_x, grid_y, color, alpha=100):
        """Add a highlight to a cell."""
        if not self.is_valid_cell(grid_x, grid_y):
            return
        
        screen_x = self.offset_x + grid_x * self.cell_size
        screen_y = self.offset_y + grid_y * self.cell_size
        
        rect = shapes.Rectangle(
            screen_x, screen_y, 
            self.cell_size, self.cell_size,
            color=(*color, alpha)
        )
        self.highlights.append(rect)
    
    def render(self):
        """Render the board (dots and highlights)."""
        # Draw highlights first (behind dots)
        for highlight in self.highlights:
            highlight.draw()
        
        # Draw the dot grid
        self.batch.draw()
