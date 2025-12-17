"""
Move analyzer for evaluating move quality and classifying moves
Similar to chess analysis tools like Stockfish.
"""

class MoveAnalyzer:
    def __init__(self):
        """Initialize the move analyzer with classification thresholds"""
        # Classification thresholds (scaled to match evaluation system)
        # Evaluation uses: PAWN=100, KING=300, so thresholds should be proportional
        self.BEST_THRESHOLD = 20       # Best move (very small difference, ~0.2 pawns)
        self.GOOD_THRESHOLD = 80       # Good move (small advantage loss, ~0.8 pawns)
        self.INACCURACY_THRESHOLD = 150  # Inaccuracy (moderate advantage loss, ~1.5 pawns)
        # Anything worse is a blunder
        
        # Move quality descriptions
        self.CLASSIFICATIONS = {
            'best': 'Best',
            'good': 'Good', 
            'inaccuracy': 'Inaccuracy',
            'blunder': 'Blunder'
        }
    
    def analyze_move(self, board, move, evaluator, ai):
        """
        Analyze a move and classify its quality using AI's minimax search
        
        Args:
            board: Board object before the move
            move (dict): Move information {'from': (row, col), 'to': (row, col), 'player': str}
            evaluator: PositionEvaluator instance
            ai: AI instance
            
        Returns:
            dict: Analysis results
        """
        from_pos = move['from']
        to_pos = move['to']
        player = move['player']
        
        # Get all possible moves for the player
        all_moves = board.get_all_moves(player)
        
        if not all_moves:
            return {
                'classification': 'best',
                'score_difference': 0,
                'best_move_score': 0,
                'actual_move_score': 0,
                'move_number': move.get('move_number', 0),
                'player': player,
                'description': 'Only move available'
            }
        
        evaluated_moves = ai.get_all_move_evaluations(board, player)
        
        if not evaluated_moves:
            return {
                'classification': 'best',
                'score_difference': 0,
                'best_move_score': 0,
                'actual_move_score': 0,
                'move_number': move.get('move_number', 0),
                'player': player,
                'description': 'Only move available'
            }
        
        actual_evaluation = next((m for m in evaluated_moves 
                                 if m['from'] == from_pos and m['to'] == to_pos), None)
        
        if not actual_evaluation:
            return {
                'classification': 'blunder',
                'score_difference': 1000,
                'best_move_score': evaluated_moves[0]['score'],
                'actual_move_score': 0,
                'move_number': move.get('move_number', 0),
                'player': player,
                'description': 'Invalid move'
            }
        
        best_move_data = evaluated_moves[0]
        best_move_score = best_move_data['score']
        actual_move_score = actual_evaluation['score']
        
        best_player_score = best_move_score if player == 'red' else -best_move_score
        actual_player_score = actual_move_score if player == 'red' else -actual_move_score
        score_difference = max(0, best_player_score - actual_player_score)
        
        if actual_evaluation == best_move_data:
            classification = 'best'
            score_difference = 0
        else:
            classification = self._classify_move(score_difference)
        
        top_moves = evaluated_moves[:5]
        description = self._generate_description(classification, score_difference, top_moves)
        
        return {
            'classification': classification,
            'score_difference': score_difference,
            'best_move_score': best_move_score,
            'actual_move_score': actual_move_score,
            'move_number': move.get('move_number', 0),
            'player': player,
            'description': description,
            'all_moves': top_moves
        }
    
    def _analyze_move_simple(self, board, move, evaluator):
        """Fallback simple move analysis if AI search fails"""
        from_pos = move['from']
        to_pos = move['to']
        player = move['player']
        
        # Get all possible moves
        all_moves = board.get_all_moves(player)
        
        if not all_moves:
            return {
                'classification': 'best',
                'score_difference': 0,
                'best_move_score': 0,
                'actual_move_score': 0,
                'move_number': move.get('move_number', 0),
                'player': player,
                'description': 'Only move available'
            }
        
        # Evaluate all moves with simple 1-ply evaluation
        move_scores = []
        for possible_move in all_moves:
            temp_board = board.copy()
            temp_board.move_piece(possible_move[0], possible_move[1])
            
            # Check for kinging
            piece = temp_board.get_piece(possible_move[1][0], possible_move[1][1])
            if piece and not piece.is_king:
                if (player == 'red' and possible_move[1][0] == 0) or (player == 'blue' and possible_move[1][0] == 7):
                    piece.make_king()
            
            score = evaluator.evaluate(temp_board, 'red')
            move_scores.append((possible_move, score))
        
        # Sort by score
        if player == 'red':
            move_scores.sort(key=lambda x: x[1], reverse=True)
        else:
            move_scores.sort(key=lambda x: x[1])
        
        best_score = move_scores[0][1]
        actual_score = next((score for move_tuple, score in move_scores if move_tuple == (from_pos, to_pos)), None)
        
        if actual_score is None:
            return {
                'classification': 'blunder',
                'score_difference': 1000,
                'best_move_score': best_score,
                'actual_move_score': 0,
                'move_number': move.get('move_number', 0),
                'player': player,
                'description': 'Invalid move'
            }
        
        best_player_score = best_score if player == 'red' else -best_score
        actual_player_score = actual_score if player == 'red' else -actual_score
        score_difference = max(0, best_player_score - actual_player_score)
        classification = self._classify_move(score_difference)
        description = self._generate_description(classification, score_difference, None)
        
        return {
            'classification': classification,
            'score_difference': score_difference,
            'best_move_score': best_score,
            'actual_move_score': actual_score,
            'move_number': move.get('move_number', 0),
            'player': player,
            'description': description,
            'all_moves': []
        }
    
    def _classify_move(self, score_difference):
        """
        Classify a move based on score difference
        
        Args:
            score_difference (float): Difference from best move
            
        Returns:
            str: Move classification
        """
        if score_difference <= self.BEST_THRESHOLD:
            return 'best'
        elif score_difference <= self.GOOD_THRESHOLD:
            return 'good'
        elif score_difference <= self.INACCURACY_THRESHOLD:
            return 'inaccuracy'
        else:
            return 'blunder'
    
    def _generate_description(self, classification, score_difference, move_evaluations):
        """
        Generate a description for the move analysis
        
        Args:
            classification (str): Move classification
            score_difference (float): Score difference
            move_evaluations (list): All move evaluations (optional)
            
        Returns:
            str: Description of the move
        """
        # Convert score difference to approximate pawn equivalent
        pawn_equivalent = score_difference / 100.0
        
        if classification == 'best':
            alt_text = f" ({len(move_evaluations)} alternatives)" if move_evaluations else ""
            return f"Best move!{alt_text}"
        elif classification == 'good':
            return f"Good move, slight advantage loss ({score_difference:.0f} points, ~{pawn_equivalent:.1f} pawns)"
        elif classification == 'inaccuracy':
            return f"Inaccuracy, moderate advantage loss ({score_difference:.0f} points, ~{pawn_equivalent:.1f} pawns)"
        else:  # blunder
            return f"Blunder! Major advantage loss ({score_difference:.0f} points, ~{pawn_equivalent:.1f} pawns)"
    
    def calculate_player_stats(self, analysis_results, player):
        """
        Calculate statistics for a specific player
        
        Args:
            analysis_results (list): List of analysis results
            player (str): Player color ('red' or 'blue')
            
        Returns:
            dict: Player statistics
        """
        player_analyses = [analysis for analysis in analysis_results 
                          if analysis['player'] == player]
        
        if not player_analyses:
            return {
                'accuracy': 0,
                'best': 0,
                'good': 0,
                'inaccuracy': 0,
                'blunder': 0,
                'total_moves': 0
            }
        
        # Count classifications
        best_count = sum(1 for analysis in player_analyses if analysis['classification'] == 'best')
        good_count = sum(1 for analysis in player_analyses if analysis['classification'] == 'good')
        inaccuracy_count = sum(1 for analysis in player_analyses if analysis['classification'] == 'inaccuracy')
        blunder_count = sum(1 for analysis in player_analyses if analysis['classification'] == 'blunder')
        
        total_moves = len(player_analyses)
        
        # Calculate accuracy (best + good moves)
        accuracy = ((best_count + good_count) / total_moves) * 100 if total_moves > 0 else 0
        
        return {
            'accuracy': accuracy,
            'best': best_count,
            'good': good_count,
            'inaccuracy': inaccuracy_count,
            'blunder': blunder_count,
            'total_moves': total_moves
        }
    
    def get_move_quality_distribution(self, analysis_results):
        """
        Get move quality distribution across all players
        
        Args:
            analysis_results (list): List of analysis results
            
        Returns:
            dict: Distribution statistics
        """
        total_moves = len(analysis_results)
        if total_moves == 0:
            return {}
        
        classifications = [analysis['classification'] for analysis in analysis_results]
        
        distribution = {
            'best': classifications.count('best'),
            'good': classifications.count('good'),
            'inaccuracy': classifications.count('inaccuracy'),
            'blunder': classifications.count('blunder')
        }
        
        # Calculate percentages
        for key in distribution:
            distribution[f'{key}_percentage'] = (distribution[key] / total_moves) * 100
        
        return distribution
    
    def get_best_moves(self, analysis_results, player, limit=5):
        """
        Get the best moves made by a player
        
        Args:
            analysis_results (list): List of analysis results
            player (str): Player color
            limit (int): Maximum number of moves to return
            
        Returns:
            list: List of best moves
        """
        player_analyses = [analysis for analysis in analysis_results 
                          if analysis['player'] == player and analysis['classification'] == 'best']
        
        # Sort by move number
        player_analyses.sort(key=lambda x: x['move_number'])
        
        return player_analyses[:limit]
    
    def get_blunders(self, analysis_results, player, limit=5):
        """
        Get the blunders made by a player
        
        Args:
            analysis_results (list): List of analysis results
            player (str): Player color
            limit (int): Maximum number of moves to return
            
        Returns:
            list: List of blunders
        """
        player_analyses = [analysis for analysis in analysis_results 
                          if analysis['player'] == player and analysis['classification'] == 'blunder']
        
        # Sort by score difference (worst first)
        player_analyses.sort(key=lambda x: x['score_difference'], reverse=True)
        
        return player_analyses[:limit]
    
    def get_inaccuracies(self, analysis_results, player, limit=5):
        """
        Get the inaccuracies made by a player
        
        Args:
            analysis_results (list): List of analysis results
            player (str): Player color
            limit (int): Maximum number of moves to return
            
        Returns:
            list: List of inaccuracies
        """
        player_analyses = [analysis for analysis in analysis_results 
                          if analysis['player'] == player and analysis['classification'] == 'inaccuracy']
        
        # Sort by score difference (worst first)
        player_analyses.sort(key=lambda x: x['score_difference'], reverse=True)
        
        return player_analyses[:limit]
    
    def generate_analysis_report(self, analysis_results):
        """
        Generate a comprehensive analysis report
        
        Args:
            analysis_results (list): List of analysis results
            
        Returns:
            str: Formatted analysis report
        """
        if not analysis_results:
            return "No moves to analyze."
        
        report = []
        report.append("MOVE ANALYSIS REPORT")
        report.append("=" * 50)
        
        # Overall statistics
        distribution = self.get_move_quality_distribution(analysis_results)
        report.append(f"Total Moves Analyzed: {len(analysis_results)}")
        report.append(f"Best Moves: {distribution.get('best', 0)} ({distribution.get('best_percentage', 0):.1f}%)")
        report.append(f"Good Moves: {distribution.get('good', 0)} ({distribution.get('good_percentage', 0):.1f}%)")
        report.append(f"Inaccuracies: {distribution.get('inaccuracy', 0)} ({distribution.get('inaccuracy_percentage', 0):.1f}%)")
        report.append(f"Blunders: {distribution.get('blunder', 0)} ({distribution.get('blunder_percentage', 0):.1f}%)")
        report.append("")
        
        # Player-specific statistics
        for player in ['red', 'blue']:
            stats = self.calculate_player_stats(analysis_results, player)
            report.append(f"{player.upper()} PLAYER:")
            report.append(f"  Accuracy: {stats['accuracy']:.1f}%")
            report.append(f"  Best Moves: {stats['best']}")
            report.append(f"  Good Moves: {stats['good']}")
            report.append(f"  Inaccuracies: {stats['inaccuracy']}")
            report.append(f"  Blunders: {stats['blunder']}")
            report.append("")
        
        return "\n".join(report)
