"""
AI Opponent - Simple AI for enemy fleet control in Melee at Sea
"""
import random


class AI:
    """Simple AI that controls the enemy fleet."""
    
    def __init__(self, combat_system):
        """
        Initialize the AI.
        
        Args:
            combat_system: Reference to the combat system
        """
        self.combat = combat_system
    
    def place_ships(self, board, num_ships=5, ship_length=4):
        """
        Place AI ships on the right side of the board.
        
        Args:
            board: The game board
            num_ships: Number of ships to place
            ship_length: Length of each ship
            
        Returns:
            List of (x, y, orientation) tuples for ship placements
        """
        from game.ship import Ship, UP, DOWN, LEFT, RIGHT
        
        placements = []
        placed_cells = set()
        orientations = [UP, DOWN, LEFT, RIGHT]
        
        # Place ships on the right half of the board
        min_x = board.cols // 2 + 2
        max_x = board.cols - ship_length - 1
        
        attempts = 0
        while len(placements) < num_ships and attempts < 1000:
            attempts += 1
            
            orientation = random.choice(orientations)
            
            # Calculate valid position range based on orientation
            if orientation == UP:
                x = random.randint(min_x, max_x)
                y = random.randint(ship_length - 1, board.rows - 1)
            elif orientation == DOWN:
                x = random.randint(min_x, max_x)
                y = random.randint(0, board.rows - ship_length)
            elif orientation == RIGHT:
                x = random.randint(min_x, board.cols - ship_length)
                y = random.randint(0, board.rows - 1)
            else:  # LEFT
                x = random.randint(min_x + ship_length - 1, max_x + ship_length)
                y = random.randint(0, board.rows - 1)
            
            # Create temporary ship to get cells
            temp_ship = Ship(x, y, ship_length, orientation, 'enemy', board)
            cells = temp_ship.get_cells()
            
            # Check if all cells are valid and not occupied
            valid = True
            for cx, cy in cells:
                if not board.is_valid_cell(cx, cy):
                    valid = False
                    break
                if (cx, cy) in placed_cells:
                    valid = False
                    break
            
            if valid:
                placements.append((x, y, orientation))
                for cell in cells:
                    placed_cells.add(cell)
        
        return placements
    
    def take_turn(self, enemy_ships, player_ships, all_ships):
        """
        Execute the AI's turn - only ONE ship can move/rotate once per turn.
        
        Args:
            enemy_ships: List of AI-controlled ships
            player_ships: List of player's ships  
            all_ships: All ships on the board
            
        Returns:
            List of action descriptions for display
        """
        actions = []
        
        # Get list of alive ships that can act
        alive_ships = [ship for ship in enemy_ships if ship.is_alive]
        if not alive_ships:
            return actions
        
        # Shuffle to add unpredictability, then pick the best candidate
        random.shuffle(alive_ships)
        
        # Find a ship that can either fire or make a good move
        best_ship = None
        best_action = None
        best_priority = -1
        
        for ship in alive_ships:
            # Check if this ship can fire (highest priority)
            targets = self.combat.get_targets_in_range(ship, all_ships)
            if targets:
                if best_priority < 2:
                    best_priority = 2
                    best_ship = ship
                    best_action = ('fire', None)
            else:
                # Check if this ship can make a useful move
                move = self._find_best_move(ship, player_ships, all_ships)
                if move and best_priority < 1:
                    best_priority = 1
                    best_ship = ship
                    best_action = move
        
        # If no good action found, pick random ship to move toward enemies
        if not best_ship:
            best_ship = random.choice(alive_ships)
            best_action = self._find_best_move(best_ship, player_ships, all_ships)
        
        # Execute the action for the chosen ship
        if best_ship and best_action:
            action_type, action_dir = best_action
            
            if action_type == 'fire':
                hits = self.combat.fire_broadside(best_ship, all_ships)
                best_ship.has_fired = True
                if hits:
                    hit_names = [f"{'destroyed' if d else 'hit'} a ship" for _, d in hits]
                    actions.append(f"Enemy fired: {', '.join(hit_names)}!")
                else:
                    actions.append("Enemy ship fired but missed!")
            elif action_type == 'move':
                if best_ship.move(action_dir, all_ships):
                    best_ship.has_moved = True
                    actions.append("Enemy ship advanced")
            elif action_type == 'rotate':
                if best_ship.rotate(action_dir, all_ships):
                    best_ship.has_moved = True
                    actions.append("Enemy ship maneuvered")
        
        return actions
    
    def _evaluate_and_act(self, ship, player_ships, all_ships):
        """Evaluate the best action for a single ship."""
        # First check if we can fire
        targets = self.combat.get_targets_in_range(ship, all_ships)
        
        if targets:
            # We have targets, fire!
            hits = self.combat.fire_broadside(ship, all_ships)
            ship.has_fired = True
            
            if hits:
                hit_names = [f"{'destroyed' if d else 'hit'} a ship" for _, d in hits]
                return f"Enemy fired: {', '.join(hit_names)}!"
            return "Enemy ship fired but missed!"
        
        # No targets, try to maneuver into position
        best_move = self._find_best_move(ship, player_ships, all_ships)
        
        if best_move:
            move_type, move_dir = best_move
            if move_type == 'move':
                if ship.move(move_dir, all_ships):
                    ship.has_moved = True
                    return f"Enemy ship advanced"
            elif move_type == 'rotate':
                if ship.rotate(move_dir, all_ships):
                    ship.has_moved = True
                    return f"Enemy ship maneuvered"
        
        return None
    
    def _find_best_move(self, ship, player_ships, all_ships):
        """Find the best move to get into firing position."""
        best_score = -1
        best_move = None
        
        # Try all possible moves
        moves = [
            ('move', 'forward'),
            ('move', 'backward'),
            ('move', 'left'),
            ('move', 'right'),
            ('rotate', 'cw'),
            ('rotate', 'ccw')
        ]
        
        random.shuffle(moves)  # Add some unpredictability
        
        for move_type, move_dir in moves:
            # Save current state
            old_x, old_y = ship.x, ship.y
            old_orientation = ship.orientation
            
            # Try the move
            success = False
            if move_type == 'move':
                success = ship.move(move_dir, all_ships)
            elif move_type == 'rotate':
                success = ship.rotate(move_dir, all_ships)
            
            if success:
                # Evaluate new position
                score = self._evaluate_position(ship, player_ships, all_ships)
                
                # Restore state
                ship.x, ship.y = old_x, old_y
                ship.orientation = old_orientation
                
                if score > best_score:
                    best_score = score
                    best_move = (move_type, move_dir)
            else:
                # Restore state if move failed
                ship.x, ship.y = old_x, old_y
                ship.orientation = old_orientation
        
        return best_move
    
    def _evaluate_position(self, ship, player_ships, all_ships):
        """
        Score a position based on tactical value.
        
        Higher score = better position
        """
        score = 0
        
        # Bonus for having targets in range
        targets = self.combat.get_targets_in_range(ship, all_ships)
        for target_ship, hit_cells in targets:
            score += len(hit_cells) * 10
        
        # Penalty for being in enemy fire zones
        for player_ship in player_ships:
            if not player_ship.is_alive:
                continue
            enemy_fire_zones = player_ship.get_fire_zones()
            ship_cells = ship.get_cells()
            
            for cell in ship_cells:
                if cell in enemy_fire_zones:
                    score -= 5
        
        # Small bonus for being closer to enemies (aggressive AI)
        for player_ship in player_ships:
            if not player_ship.is_alive:
                continue
            distance = abs(ship.x - player_ship.x) + abs(ship.y - player_ship.y)
            score += max(0, 10 - distance)
        
        return score
