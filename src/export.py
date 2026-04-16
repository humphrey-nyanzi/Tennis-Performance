"""
Export functionality module for Tennis Performance Analysis.
Handles PDF report generation, CSV export, and shareable summaries.
"""

import pandas as pd
import numpy as np
from io import StringIO, BytesIO
from typing import Optional, Dict, List
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def _get_preferred_date_column(df: pd.DataFrame) -> Optional[str]:
    """Return the best available date column for sorting/export."""
    for col in ("t_date", "date", "t_year"):
        if col in df.columns:
            return col
    return None


def _sort_by_available_date(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    """Sort a DataFrame by the first available date-like column."""
    date_col = _get_preferred_date_column(df)
    if date_col:
        return df.sort_values(date_col, ascending=ascending)
    return df.sort_index(ascending=ascending)


def _generate_pdf_with_reportlab(title: str, sections: List[tuple]) -> bytes:
    """
    Generate a PDF report using reportlab.
    
    Args:
        title: PDF title
        sections: List of tuples (section_title, section_content)
        
    Returns:
        PDF as bytes
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        # Create PDF buffer
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        
        # Container for PDF elements
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Add title
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Add sections
        for section_title, section_content in sections:
            if section_title:
                elements.append(Paragraph(section_title, heading_style))
            
            # Handle different content types
            if isinstance(section_content, str):
                elements.append(Paragraph(section_content, styles['Normal']))
            elif isinstance(section_content, list):
                for item in section_content:
                    elements.append(Paragraph(item, styles['Normal']))
            
            elements.append(Spacer(1, 0.2*inch))
        
        # Add timestamp
        elements.append(Spacer(1, 0.3*inch))
        timestamp = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(timestamp, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    except ImportError:
        logger.error("reportlab not installed. Please install it with: pip install reportlab")
        return b"Error: reportlab not installed"


def generate_player_report_csv(match_data: pd.DataFrame, player: str, 
                              output_path: Optional[str] = None) -> str:
    """
    Generate a comprehensive CSV report for a player.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        output_path: Optional path to save CSV file
        
    Returns:
        CSV content as string (or None if saved to file)
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    player_matches = _sort_by_available_date(player_matches)
    
    if len(player_matches) == 0:
        return "No data available for player: " + player
    
    # Create output dataframe with relevant columns
    output_data = []
    for _, match in player_matches.iterrows():
        is_win = match["w_name"] == player
        opponent = match["l_name"] if is_win else match["w_name"]
        result = "WIN" if is_win else "LOSS"
        
        output_data.append({
            "Date": match.get("t_date", match.get("date", match.get("t_year", ""))),
            "Result": result,
            "Opponent": opponent,
            "Tournament": match["t_name"],
            "Level": match["t_level"],
            "Surface": match["surface"],
            "Round": match.get("round", "")
        })
    
    df_output = pd.DataFrame(output_data)
    
    # Summary section
    summary_lines = []
    summary_lines.append(f"# Tennis Performance Report")
    summary_lines.append(f"Player: {player}")
    summary_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    
    # Calculate summary stats
    wins = (player_matches["w_name"] == player).sum()
    total = len(player_matches)
    wp = (wins / total * 100) if total > 0 else 0
    
    summary_lines.append(f"Total Matches: {total}")
    summary_lines.append(f"Wins: {wins}")
    summary_lines.append(f"Losses: {total - wins}")
    summary_lines.append(f"Win Percentage: {wp:.1f}%")
    summary_lines.append("")
    
    # Surface breakdown
    summary_lines.append("Surface Breakdown:")
    for surface in sorted(player_matches["surface"].unique()):
        surface_matches = player_matches[player_matches["surface"] == surface]
        surface_wins = (surface_matches["w_name"] == player).sum()
        surface_total = len(surface_matches)
        surface_wp = (surface_wins / surface_total * 100) if surface_total > 0 else 0
        summary_lines.append(f"  {surface}: {surface_wins}-{surface_total - surface_wins} ({surface_wp:.1f}%)")
    
    summary_lines.append("")
    
    # Tournament level breakdown
    summary_lines.append("Tournament Level Breakdown:")
    for level in sorted(player_matches["t_level"].unique()):
        level_matches = player_matches[player_matches["t_level"] == level]
        level_wins = (level_matches["w_name"] == player).sum()
        level_total = len(level_matches)
        level_wp = (level_wins / level_total * 100) if level_total > 0 else 0
        summary_lines.append(f"  {level}: {level_wins}-{level_total - level_wins} ({level_wp:.1f}%)")
    
    summary_lines.append("")
    
    # Combine summary and match data
    summary_text = "\n".join(summary_lines)
    matches_csv = df_output.to_csv(index=False)
    full_csv = summary_text + "\n\n" + matches_csv
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(full_csv)
        logger.info(f"CSV report saved to {output_path}")
        return None
    
    return full_csv


def generate_tournament_report_csv(match_data: pd.DataFrame, tournament: str,
                                  output_path: Optional[str] = None) -> str:
    """
    Generate a comprehensive CSV report for a tournament.
    
    Args:
        match_data: Match DataFrame
        tournament: Tournament name
        output_path: Optional path to save CSV file
        
    Returns:
        CSV content as string
    """
    tournament_matches = match_data[match_data["t_name"] == tournament].copy()
    
    if len(tournament_matches) == 0:
        return "No data available for tournament: " + tournament
    
    # Summary section
    summary_lines = []
    summary_lines.append(f"# Tennis Tournament Report")
    summary_lines.append(f"Tournament: {tournament}")
    summary_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    
    # Tournament stats
    unique_players = pd.concat([
        tournament_matches["w_name"],
        tournament_matches["l_name"]
    ]).unique()
    
    summary_lines.append(f"Total Matches: {len(tournament_matches)}")
    summary_lines.append(f"Unique Players: {len(unique_players)}")
    summary_lines.append(f"Tournament Level: {tournament_matches['t_level'].iloc[0] if len(tournament_matches) > 0 else 'Unknown'}")
    summary_lines.append(f"Surface: {tournament_matches['surface'].iloc[0] if len(tournament_matches) > 0 else 'Unknown'}")
    summary_lines.append("")
    
    # Player standings
    summary_lines.append("Top Performers:")
    player_wins = tournament_matches["w_name"].value_counts()
    for rank, (player, wins) in enumerate(player_wins.head(10).items(), 1):
        summary_lines.append(f"  {rank}. {player}: {int(wins)} wins")
    
    summary_lines.append("")
    
    # Match details
    output_data = []
    for _, match in tournament_matches.iterrows():
        output_data.append({
            "Date": match.get("t_date", match.get("date", match.get("t_year", ""))),
            "Winner": match["w_name"],
            "Loser": match["l_name"],
            "Round": match.get("round", ""),
            "Surface": match["surface"]
        })
    
    df_output = pd.DataFrame(output_data)
    
    summary_text = "\n".join(summary_lines)
    matches_csv = df_output.to_csv(index=False)
    full_csv = summary_text + "\n\n" + matches_csv
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(full_csv)
        logger.info(f"CSV report saved to {output_path}")
        return None
    
    return full_csv


def generate_comparison_report_csv(match_data: pd.DataFrame, players: List[str],
                                   output_path: Optional[str] = None) -> str:
    """
    Generate comparison CSV report across multiple players.
    
    Args:
        match_data: Match DataFrame
        players: List of player names to compare
        output_path: Optional path to save CSV file
        
    Returns:
        CSV content as string
    """
    summary_lines = []
    summary_lines.append(f"# Multi-Player Comparison Report")
    summary_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    
    comparison_data = []
    
    for player in players:
        player_matches = match_data[
            (match_data["w_name"] == player) | (match_data["l_name"] == player)
        ]
        
        if len(player_matches) == 0:
            continue
        
        wins = (player_matches["w_name"] == player).sum()
        total = len(player_matches)
        wp = (wins / total * 100) if total > 0 else 0
        
        # Surface breakdown
        surface_wp = {}
        for surface in player_matches["surface"].unique():
            surf_matches = player_matches[player_matches["surface"] == surface]
            surf_wins = (surf_matches["w_name"] == player).sum()
            surf_wp = (surf_wins / len(surf_matches) * 100) if len(surf_matches) > 0 else 0
            surface_wp[surface] = surf_wp
        
        comparison_data.append({
            "Player": player,
            "Total Matches": total,
            "Wins": wins,
            "Losses": total - wins,
            "Win %": round(wp, 1),
            "Hard %": round(surface_wp.get("Hard", 0), 1),
            "Clay %": round(surface_wp.get("Clay", 0), 1),
            "Grass %": round(surface_wp.get("Grass", 1), 1)
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    
    summary_text = "\n".join(summary_lines)
    comparison_csv = df_comparison.to_csv(index=False)
    full_csv = summary_text + "\n\n" + comparison_csv
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(full_csv)
        logger.info(f"Comparison report saved to {output_path}")
        return None
    
    return full_csv


def generate_shareable_summary(match_data: pd.DataFrame, player: str) -> Dict:
    """
    Generate a JSON-serializable shareable summary of player performance.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        
    Returns:
        Dictionary with shareable performance summary
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return {"error": f"No data for player {player}"}
    
    wins = (player_matches["w_name"] == player).sum()
    total = len(player_matches)
    wp = (wins / total * 100) if total > 0 else 0
    
    # Recent form
    recent = _sort_by_available_date(player_matches, ascending=False).head(10)
    recent_wins = (recent["w_name"] == player).sum()
    recent_wp = (recent_wins / len(recent) * 100) if len(recent) > 0 else 0
    
    # Surface stats
    surface_stats = {}
    for surface in player_matches["surface"].unique():
        s_matches = player_matches[player_matches["surface"] == surface]
        s_wins = (s_matches["w_name"] == player).sum()
        surface_stats[surface] = {
            "matches": len(s_matches),
            "wins": int(s_wins),
            "win_percentage": round((s_wins / len(s_matches) * 100) if len(s_matches) > 0 else 0, 1)
        }
    
    return {
        "player": player,
        "generated": datetime.now().isoformat(),
        "career_stats": {
            "total_matches": int(total),
            "wins": int(wins),
            "losses": int(total - wins),
            "win_percentage": round(wp, 1)
        },
        "recent_form": {
            "matches": len(recent),
            "wins": int(recent_wins),
            "win_percentage": round(recent_wp, 1)
        },
        "surface_breakdown": surface_stats,
        "tournament_venues": sorted(player_matches["t_name"].unique().tolist())
    }


def generate_matchup_summary_csv(match_data: pd.DataFrame, player1: str, player2: str,
                                output_path: Optional[str] = None) -> str:
    """
    Generate CSV summary of head-to-head matchup between two players.
    
    Args:
        match_data: Match DataFrame
        player1: First player name
        player2: Second player name
        output_path: Optional path to save CSV file
        
    Returns:
        CSV content as string
    """
    h2h_matches = match_data[
        ((match_data["w_name"] == player1) & (match_data["l_name"] == player2)) |
        ((match_data["w_name"] == player2) & (match_data["l_name"] == player1))
    ].copy()
    h2h_matches = _sort_by_available_date(h2h_matches)
    
    if len(h2h_matches) == 0:
        return f"No head-to-head matches between {player1} and {player2}"
    
    # Summary section
    summary_lines = []
    summary_lines.append(f"# Head-to-Head Matchup Report")
    summary_lines.append(f"Player 1: {player1}")
    summary_lines.append(f"Player 2: {player2}")
    summary_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    
    # Calculate records
    p1_wins = ((h2h_matches["w_name"] == player1) & (h2h_matches["l_name"] == player2)).sum()
    p2_wins = ((h2h_matches["w_name"] == player2) & (h2h_matches["l_name"] == player1)).sum()
    total = len(h2h_matches)
    
    summary_lines.append(f"Total Matches: {total}")
    summary_lines.append(f"{player1} Record: {int(p1_wins)}-{int(p2_wins)}")
    summary_lines.append(f"{player2} Record: {int(p2_wins)}-{int(p1_wins)}")
    summary_lines.append("")
    
    # Surface breakdown
    summary_lines.append("Surface Breakdown:")
    for surface in sorted(h2h_matches["surface"].unique()):
        surf_matches = h2h_matches[h2h_matches["surface"] == surface]
        p1_surface_wins = ((surf_matches["w_name"] == player1) & (surf_matches["l_name"] == player2)).sum()
        p2_surface_wins = ((surf_matches["w_name"] == player2) & (surf_matches["l_name"] == player1)).sum()
        summary_lines.append(f"  {surface}: {player1} {int(p1_surface_wins)}-{int(p2_surface_wins)} {player2}")
    
    summary_lines.append("")
    
    # Match details
    output_data = []
    for _, match in h2h_matches.iterrows():
        winner = player1 if match["w_name"] == player1 else player2
        output_data.append({
            "Date": match.get("t_date", match.get("date", match.get("t_year", ""))),
            "Winner": winner,
            "Tournament": match["t_name"],
            "Surface": match["surface"],
            "Round": match.get("round", "")
        })
    
    df_output = pd.DataFrame(output_data)
    
    summary_text = "\n".join(summary_lines)
    matches_csv = df_output.to_csv(index=False)
    full_csv = summary_text + "\n\n" + matches_csv
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(full_csv)
        logger.info(f"H2H report saved to {output_path}")
        return None
    
    return full_csv


def export_to_json(report_data: Dict, output_path: str) -> None:
    """
    Export report data to JSON format.
    
    Args:
        report_data: Dictionary containing report data
        output_path: Path to save JSON file
    """
    with open(output_path, "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    logger.info(f"JSON report exported to {output_path}")


def create_email_summary(player: str, performance_summary: Dict) -> str:
    """
    Create an email-friendly text summary of player performance.
    
    Args:
        player: Player name
        performance_summary: Dictionary with performance data
        
    Returns:
        Formatted email text
    """
    email_lines = []
    email_lines.append(f"Tennis Performance Summary: {player}")
    email_lines.append("=" * 50)
    email_lines.append("")
    
    if "career_stats" in performance_summary:
        stats = performance_summary["career_stats"]
        email_lines.append(f"Career Statistics:")
        email_lines.append(f"  Total Matches: {stats['total_matches']}")
        email_lines.append(f"  Record: {stats['wins']}-{stats['losses']}")
        email_lines.append(f"  Win Rate: {stats['win_percentage']}%")
        email_lines.append("")
    
    if "recent_form" in performance_summary:
        recent = performance_summary["recent_form"]
        email_lines.append(f"Recent Form (Last {recent['matches']} matches):")
        email_lines.append(f"  Record: {recent['wins']}-{recent['matches'] - recent['wins']}")
        email_lines.append(f"  Win Rate: {recent['win_percentage']}%")
        email_lines.append("")
    
    if "surface_breakdown" in performance_summary:
        email_lines.append("Performance by Surface:")
        for surface, stats in performance_summary["surface_breakdown"].items():
            email_lines.append(f"  {surface}: {stats['win_percentage']}% ({stats['wins']}/{stats['matches']} matches)")
        email_lines.append("")
    
    email_lines.append("Report generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    email_lines.append("")
    email_lines.append("Tennis Performance Analysis Dashboard")
    
    return "\n".join(email_lines)


def generate_player_report_pdf(match_data: pd.DataFrame, player: str) -> bytes:
    """
    Generate a comprehensive PDF report for a player.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        
    Returns:
        PDF as bytes
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return b"No data available for player: " + player.encode()
    
    # Calculate stats
    wins = (player_matches["w_name"] == player).sum()
    total = len(player_matches)
    wp = (wins / total * 100) if total > 0 else 0
    
    # Surface breakdown
    surface_lines = []
    for surface in sorted(player_matches["surface"].unique()):
        if pd.notna(surface):
            surface_matches = player_matches[player_matches["surface"] == surface]
            surface_wins = (surface_matches["w_name"] == player).sum()
            surface_total = len(surface_matches)
            surface_wp = (surface_wins / surface_total * 100) if surface_total > 0 else 0
            surface_lines.append(f"<b>{surface}:</b> {surface_wins}-{surface_total - surface_wins} ({surface_wp:.1f}%)")
    
    # Tournament level breakdown
    level_lines = []
    for level in sorted(player_matches["t_level"].unique()):
        if pd.notna(level):
            level_matches = player_matches[player_matches["t_level"] == level]
            level_wins = (level_matches["w_name"] == player).sum()
            level_total = len(level_matches)
            level_wp = (level_wins / level_total * 100) if level_total > 0 else 0
            level_lines.append(f"<b>{level}:</b> {level_wins}-{level_total - level_wins} ({level_wp:.1f}%)")
    
    # Build PDF sections
    sections = [
        ("Career Overview", [
            f"<b>Player:</b> {player}",
            f"<b>Total Matches:</b> {total}",
            f"<b>Record:</b> {wins}-{total - wins}",
            f"<b>Win Rate:</b> {wp:.1f}%"
        ]),
        ("Surface Performance", surface_lines if surface_lines else ["No surface data available"]),
        ("Tournament Level Performance", level_lines if level_lines else ["No level data available"])
    ]
    
    return _generate_pdf_with_reportlab(f"Tennis Performance Report: {player}", sections)


def generate_tournament_report_pdf(match_data: pd.DataFrame, tournament: str) -> bytes:
    """
    Generate a PDF report for a tournament.
    
    Args:
        match_data: Match DataFrame
        tournament: Tournament name
        
    Returns:
        PDF as bytes
    """
    tournament_matches = match_data[match_data["t_name"] == tournament].copy()
    
    if len(tournament_matches) == 0:
        return b"No data available for tournament: " + tournament.encode()
    
    # Tournament stats
    unique_players = pd.concat([
        tournament_matches["w_name"],
        tournament_matches["l_name"]
    ]).unique()
    
    # Player standings
    player_wins = tournament_matches["w_name"].value_counts()
    standing_lines = []
    for rank, (player, wins) in enumerate(player_wins.head(10).items(), 1):
        standing_lines.append(f"{rank}. <b>{player}</b>: {int(wins)} wins")
    
    tournament_level = tournament_matches['t_level'].iloc[0] if len(tournament_matches) > 0 else 'Unknown'
    tournament_surface = tournament_matches['surface'].iloc[0] if len(tournament_matches) > 0 else 'Unknown'
    
    sections = [
        ("Tournament Overview", [
            f"<b>Tournament:</b> {tournament}",
            f"<b>Total Matches:</b> {len(tournament_matches)}",
            f"<b>Unique Players:</b> {len(unique_players)}",
            f"<b>Level:</b> {tournament_level}",
            f"<b>Surface:</b> {tournament_surface}"
        ]),
        ("Top Performers", standing_lines if standing_lines else ["No performance data available"])
    ]
    
    return _generate_pdf_with_reportlab(f"Tournament Report: {tournament}", sections)


def generate_h2h_report_pdf(match_data: pd.DataFrame, player1: str, player2: str) -> bytes:
    """
    Generate a PDF report for head-to-head matchup.
    
    Args:
        match_data: Match DataFrame
        player1: First player name
        player2: Second player name
        
    Returns:
        PDF as bytes
    """
    h2h_matches = match_data[
        ((match_data["w_name"] == player1) & (match_data["l_name"] == player2)) |
        ((match_data["w_name"] == player2) & (match_data["l_name"] == player1))
    ].copy()
    
    if len(h2h_matches) == 0:
        return b"No head-to-head data available"
    
    # Calculate records
    p1_wins = ((h2h_matches["w_name"] == player1) & (h2h_matches["l_name"] == player2)).sum()
    p2_wins = ((h2h_matches["w_name"] == player2) & (h2h_matches["l_name"] == player1)).sum()
    
    # Surface breakdown
    surface_lines = []
    for surface in sorted(h2h_matches["surface"].unique()):
        if pd.notna(surface):
            surf_matches = h2h_matches[h2h_matches["surface"] == surface]
            p1_surface_wins = ((surf_matches["w_name"] == player1) & (surf_matches["l_name"] == player2)).sum()
            p2_surface_wins = ((surf_matches["w_name"] == player2) & (surf_matches["l_name"] == player1)).sum()
            surface_lines.append(f"<b>{surface}:</b> {player1} {p1_surface_wins}-{p2_surface_wins} {player2}")
    
    sections = [
        ("Head-to-Head Record", [
            f"<b>{player1} vs {player2}</b>",
            f"<b>Total Meetings:</b> {len(h2h_matches)}",
            f"<b>{player1} Record:</b> {int(p1_wins)}-{int(p2_wins)}",
            f"<b>{player2} Record:</b> {int(p2_wins)}-{int(p1_wins)}"
        ]),
        ("By Surface", surface_lines if surface_lines else ["No surface data available"])
    ]
    
    return _generate_pdf_with_reportlab(f"Head-to-Head: {player1} vs {player2}", sections)
