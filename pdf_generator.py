"""
PDF Report Generator for Checkers Game Analysis
Generates detailed PDF reports with move analysis and statistics.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os


class PDFReportGenerator:
    def __init__(self):
        """Initialize the PDF report generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.player_names = {'red': 'You', 'blue': 'Gukesh'}
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Move classification styles
        self.styles.add(ParagraphStyle(
            name='BestMove',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#27ae60'),
            fontSize=11,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='GoodMove',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#3498db'),
            fontSize=11,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='InaccuracyMove',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#f39c12'),
            fontSize=11,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='BlunderMove',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#e74c3c'),
            fontSize=11,
            fontName='Helvetica-Bold'
        ))
    
    def _get_classification_style(self, classification):
        """Get paragraph style based on move classification"""
        style_map = {
            'best': 'BestMove',
            'good': 'GoodMove',
            'inaccuracy': 'InaccuracyMove',
            'blunder': 'BlunderMove'
        }
        return style_map.get(classification, 'Normal')
    
    def _get_classification_color(self, classification):
        """Get color for classification badge"""
        color_map = {
            'best': colors.HexColor('#27ae60'),
            'good': colors.HexColor('#3498db'),
            'inaccuracy': colors.HexColor('#f39c12'),
            'blunder': colors.HexColor('#e74c3c')
        }
        return color_map.get(classification, colors.black)
    
    def _get_player_label(self, player):
        if not player:
            return "Unknown"
        return self.player_names.get(player, str(player).title())
    
    def _format_move(self, move_or_analysis):
        """Format a move for display - accepts either move dict or analysis dict"""
        # Handle both move dict and analysis dict structures
        if 'from' in move_or_analysis and 'to' in move_or_analysis:
            from_pos = move_or_analysis.get('from', (0, 0))
            to_pos = move_or_analysis.get('to', (0, 0))
        else:
            # Try to get from move_history if this is an analysis result
            # For now, return a placeholder if we can't find the move
            return "N/A"
        
        # Convert to algebraic notation (simplified)
        from_col = chr(97 + from_pos[1])  # a-h
        from_row = str(8 - from_pos[0])    # 1-8
        to_col = chr(97 + to_pos[1])
        to_row = str(8 - to_pos[0])
        
        return f"{from_col}{from_row}-{to_col}{to_row}"
    
    def generate_report(self, move_history, analysis_results, winner, is_draw=False, output_path=None):
        """
        Generate a PDF report for the game
        
        Args:
            move_history (list): List of all moves made
            analysis_results (list): List of move analysis results
            winner (str): Winner of the game ('red', 'blue', or None)
            is_draw (bool): Whether the game was a draw
            output_path (str): Path to save the PDF (optional)
            
        Returns:
            str: Path to the generated PDF file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"checkers_report_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("CHECKERS GAME ANALYSIS REPORT", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Game information
        game_info = [
            ["Game Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Total Moves:", str(len(move_history))],
            ["Result:", self._format_result(winner, is_draw)]
        ]
        
        info_table = Table(game_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Player statistics
        story.append(Paragraph("PLAYER STATISTICS", self.styles['CustomHeading']))
        
        red_stats = self._calculate_stats(analysis_results, 'red')
        blue_stats = self._calculate_stats(analysis_results, 'blue')
        
        stats_data = [
            ["Player", "Accuracy", "Best", "Good", "Inaccuracy", "Blunder"],
            [f"{self._get_player_label('red')} (Human)", 
             f"{red_stats['accuracy']:.1f}%",
             str(red_stats['best']),
             str(red_stats['good']),
             str(red_stats['inaccuracy']),
             str(red_stats['blunder'])],
            [f"{self._get_player_label('blue')} (AI)",
             f"{blue_stats['accuracy']:.1f}%",
             str(blue_stats['best']),
             str(blue_stats['good']),
             str(blue_stats['inaccuracy']),
             str(blue_stats['blunder'])]
        ]
        
        stats_table = Table(stats_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 0.8*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Move-by-move analysis
        story.append(Paragraph("MOVE-BY-MOVE ANALYSIS", self.styles['CustomHeading']))
        
        # Create move analysis table
        move_data = [["Move", "Player", "Move", "Classification", "Score Diff", "Description"]]
        
        # Ensure we have matching lengths
        min_length = min(len(move_history), len(analysis_results))
        
        for i in range(min_length):
            move = move_history[i]
            analysis = analysis_results[i]
            move_num = str(move.get('move_number', i + 1))
            player = self._get_player_label(move.get('player', 'unknown'))
            move_str = self._format_move(move)
            classification = analysis.get('classification', 'unknown').title()
            score_diff = f"{analysis.get('score_difference', 0):.1f}cp"
            description = analysis.get('description', '')
            
            move_data.append([
                move_num,
                player,
                move_str,
                classification,
                score_diff,
                description[:50] + "..." if len(description) > 50 else description
            ])
        
        move_table = Table(move_data, colWidths=[0.5*inch, 0.8*inch, 1*inch, 1.2*inch, 1*inch, 2.5*inch])
        
        # Style the table
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (5, 0), (5, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]
        
        # Color code classification column
        for i in range(1, len(move_data)):
            classification = move_data[i][3].lower()
            color = self._get_classification_color(classification)
            table_style.append(('TEXTCOLOR', (3, i), (3, i), color))
            table_style.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))
        
        move_table.setStyle(TableStyle(table_style))
        story.append(move_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Best moves and blunders
        story.append(Paragraph("KEY HIGHLIGHTS", self.styles['CustomHeading']))
        
        # Get best moves and blunders (pass move_history for formatting)
        red_best = self._get_best_moves(analysis_results, 'red', 3)
        blue_best = self._get_best_moves(analysis_results, 'blue', 3)
        red_blunders = self._get_blunders(analysis_results, 'red', 3)
        blue_blunders = self._get_blunders(analysis_results, 'blue', 3)
        
        highlights = []
        red_label = self._get_player_label('red')
        blue_label = self._get_player_label('blue')
        
        if red_best:
            highlights.append(Paragraph(f"<b>{red_label}'s Best Moves:</b>", self.styles['Normal']))
            for analysis in red_best:
                # Find corresponding move in move_history
                move_num = analysis.get('move_number', 0)
                move = None
                if move_num > 0 and move_num <= len(move_history):
                    move = move_history[move_num - 1]
                
                if move:
                    move_str = self._format_move(move)
                    highlights.append(Paragraph(
                        f"• Move {move_num}: {move_str} - {analysis.get('description', '')}",
                        self.styles['Normal']
                    ))
            highlights.append(Spacer(1, 0.1*inch))
        
        if red_blunders:
            highlights.append(Paragraph(f"<b>{red_label}'s Blunders:</b>", self.styles['Normal']))
            for analysis in red_blunders:
                # Find corresponding move in move_history
                move_num = analysis.get('move_number', 0)
                move = None
                if move_num > 0 and move_num <= len(move_history):
                    move = move_history[move_num - 1]
                
                if move:
                    move_str = self._format_move(move)
                    highlights.append(Paragraph(
                        f"• Move {move_num}: {move_str} - Loss: {analysis.get('score_difference', 0):.1f}cp",
                        self.styles['BlunderMove']
                    ))
            highlights.append(Spacer(1, 0.1*inch))
        
        if blue_best:
            highlights.append(Paragraph(f"<b>{blue_label}'s Best Moves:</b>", self.styles['Normal']))
            for analysis in blue_best:
                # Find corresponding move in move_history
                move_num = analysis.get('move_number', 0)
                move = None
                if move_num > 0 and move_num <= len(move_history):
                    move = move_history[move_num - 1]
                
                if move:
                    move_str = self._format_move(move)
                    highlights.append(Paragraph(
                        f"• Move {move_num}: {move_str} - {analysis.get('description', '')}",
                        self.styles['Normal']
                    ))
            highlights.append(Spacer(1, 0.1*inch))
        
        if blue_blunders:
            highlights.append(Paragraph(f"<b>{blue_label}'s Blunders:</b>", self.styles['Normal']))
            for analysis in blue_blunders:
                # Find corresponding move in move_history
                move_num = analysis.get('move_number', 0)
                move = None
                if move_num > 0 and move_num <= len(move_history):
                    move = move_history[move_num - 1]
                
                if move:
                    move_str = self._format_move(move)
                    highlights.append(Paragraph(
                        f"• Move {move_num}: {move_str} - Loss: {analysis.get('score_difference', 0):.1f}cp",
                        self.styles['BlunderMove']
                    ))
        
        for item in highlights:
            story.append(item)
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _format_result(self, winner, is_draw):
        """Format game result string"""
        if is_draw:
            return "Draw"
        elif winner:
            return f"{self._get_player_label(winner)} Wins"
        else:
            return "Unknown"
    
    def _calculate_stats(self, analysis_results, player):
        """Calculate statistics for a player"""
        player_analyses = [a for a in analysis_results if a.get('player') == player]
        
        if not player_analyses:
            return {
                'accuracy': 0,
                'best': 0,
                'good': 0,
                'inaccuracy': 0,
                'blunder': 0
            }
        
        best = sum(1 for a in player_analyses if a.get('classification') == 'best')
        good = sum(1 for a in player_analyses if a.get('classification') == 'good')
        inaccuracy = sum(1 for a in player_analyses if a.get('classification') == 'inaccuracy')
        blunder = sum(1 for a in player_analyses if a.get('classification') == 'blunder')
        
        total = len(player_analyses)
        accuracy = ((best + good) / total * 100) if total > 0 else 0
        
        return {
            'accuracy': accuracy,
            'best': best,
            'good': good,
            'inaccuracy': inaccuracy,
            'blunder': blunder
        }
    
    def _get_best_moves(self, analysis_results, player, limit=3):
        """Get best moves for a player"""
        player_analyses = [
            a for a in analysis_results 
            if a.get('player') == player and a.get('classification') == 'best'
        ]
        player_analyses.sort(key=lambda x: x.get('move_number', 0))
        return player_analyses[:limit]
    
    def _get_blunders(self, analysis_results, player, limit=3):
        """Get blunders for a player"""
        player_analyses = [
            a for a in analysis_results 
            if a.get('player') == player and a.get('classification') == 'blunder'
        ]
        player_analyses.sort(key=lambda x: x.get('score_difference', 0), reverse=True)
        return player_analyses[:limit]

