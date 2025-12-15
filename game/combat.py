"""
Combat System - Handles firing and damage for Melee at Sea
Ships can only hit enemies that are directly adjacent (within 1 cell).
"""


class Combat:
    """Manages combat interactions between ships."""
    
    def __init__(self, board):
        """
        Initialize the combat system.
        
        Args:
            board: Reference to the game board
        """
        self.board = board
    
    def get_side_fire_zones(self, ship):
        """
        Get cells that can be fired upon - only to the SIDES of the ship.
        Ships fire perpendicular to their orientation, not front or back.
        Only one cell away from each segment.
        """
        from game.ship import UP, DOWN, LEFT, RIGHT
        
        side_cells = set()
        ship_cells = ship.get_cells()
        
        # Determine perpendicular directions based on ship orientation
        if ship.orientation in (UP, DOWN):
            # Vertical ship fires left and right
            side_offsets = [(-1, 0), (1, 0)]
        else:
            # Horizontal ship fires up and down
            side_offsets = [(0, -1), (0, 1)]
        
        # Only fire from segments that have cannons
        # Cannons are on body segments (not bow), distributed based on cannons_per_side
        body_segments = len(ship_cells) - 1
        cannon_count = min(ship.cannons_per_side, body_segments)
        
        for i, (cell_x, cell_y) in enumerate(ship_cells):
            # Skip bow (i=0), only body segments (i >= 1) have cannons
            if i == 0:
                continue
            # Only include segments that still have cannons
            if i > cannon_count:
                continue
            
            for dx, dy in side_offsets:
                target_x = cell_x + dx
                target_y = cell_y + dy
                if self.board.is_valid_cell(target_x, target_y):
                    side_cells.add((target_x, target_y))
        
        return list(side_cells)
    
    def get_targets_in_range(self, attacker, all_ships):
        """
        Get all enemy ships that are in the attacker's side fire zones.
        
        Returns:
            List of (ship, hit_cells) tuples where hit_cells are 
            the cells of that ship that are in range
        """
        fire_zones = self.get_side_fire_zones(attacker)
        targets = []
        
        for ship in all_ships:
            if ship is attacker or ship.team == attacker.team:
                continue
            if not ship.is_alive:
                continue
            
            ship_cells = ship.get_cells()
            hit_cells = [cell for cell in ship_cells if cell in fire_zones]
            
            if hit_cells:
                targets.append((ship, hit_cells))
        
        return targets
    
    def fire(self, attacker, target_cell, all_ships):
        """
        Fire at a specific cell.
        
        Args:
            attacker: The ship that is firing
            target_cell: (x, y) grid cell to fire at
            all_ships: List of all ships
            
        Returns:
            (hit_ship, destroyed) tuple or (None, False) if miss
        """
        fire_zones = self.get_side_fire_zones(attacker)
        
        if target_cell not in fire_zones:
            return None, False
        
        # Check if any enemy ship occupies this cell
        for ship in all_ships:
            if ship is attacker or ship.team == attacker.team:
                continue
            if not ship.is_alive:
                continue
            
            if target_cell in ship.get_cells():
                destroyed = ship.take_damage()
                return ship, destroyed
        
        return None, False
    
    def fire_broadside(self, attacker, all_ships):
        """
        Fire at all enemy ships to the sides.
        
        Returns:
            List of (ship, destroyed) tuples for all hits
        """
        # Check if ship has any cannons to fire
        if attacker.cannons_per_side <= 0:
            return []
        
        hits = []
        targets = self.get_targets_in_range(attacker, all_ships)
        
        # Each ship can only be hit once per broadside
        for ship, hit_cells in targets:
            if hit_cells:
                destroyed = ship.take_damage()
                hits.append((ship, destroyed))
        
        return hits
