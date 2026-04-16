"""
Report generation module - Creates exportable reports and PDF outputs.
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_player_report(
    player: str,
    match_data: pd.DataFrame,
    analysis: Dict
) -> Dict:
    """
    Generate a comprehensive player report.

    Args:
        player: Player name
        match_data: Match DataFrame
        analysis: Player analysis dictionary

    Returns:
        Report dictionary with all sections
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    wins = len(player_matches[player_matches["w_name"] == player])
    total = len(player_matches)
    
    report = {
        "title": f"Player Report: {player}",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player": player,
        "overview": {
            "total_matches": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": f"{(wins/total*100):.1f}%" if total > 0 else "N/A",
        },
        "strengths": analysis.get("strengths", []),
        "weaknesses": analysis.get("weaknesses", []),
        "surface_breakdown": {},
    }
    
    # Surface statistics
    for surface in player_matches["surface"].unique():
        surf_matches = player_matches[player_matches["surface"] == surface]
        surf_wins = len(surf_matches[surf_matches["w_name"] == player])
        report["surface_breakdown"][surface] = {
            "matches": len(surf_matches),
            "wins": surf_wins,
            "win_rate": f"{(surf_wins/len(surf_matches)*100):.1f}%"
        }
    
    return report


def generate_comparison_report(
    players: List[str],
    comparison_data: pd.DataFrame
) -> Dict:
    """
    Generate a comparison report for multiple players.

    Args:
        players: List of player names
        comparison_data: Comparison DataFrame

    Returns:
        Report dictionary
    """
    report = {
        "title": f"Player Comparison: {', '.join(players)}",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "players": players,
        "comparison_metrics": comparison_data.to_dict("records"),
        "top_performer": comparison_data.loc[comparison_data["win_rate"].idxmax()].to_dict() if not comparison_data.empty else {},
    }
    
    return report


def export_report_to_dict(report: Dict) -> Dict:
    """
    Convert report to exportable dictionary format.

    Args:
        report: Report dictionary

    Returns:
        Formatted report dictionary
    """
    return report


def format_report_markdown(report: Dict) -> str:
    """
    Format report as markdown for display or export.

    Args:
        report: Report dictionary

    Returns:
        Markdown formatted report
    """
    markdown = f"""
# {report['title']}

**Generated:** {report['generated_at']}

## Overview

- **Total Matches:** {report['overview']['total_matches']}
- **Wins:** {report['overview']['wins']}
- **Losses:** {report['overview']['losses']}
- **Win Rate:** {report['overview']['win_rate']}

## Strengths

"""
    
    if report.get('strengths'):
        for strength in report['strengths']:
            markdown += f"- ✓ {strength}\n"
    else:
        markdown += "- No major strengths identified.\n"
    
    markdown += "\n## Weaknesses\n\n"
    
    if report.get('weaknesses'):
        for weakness in report['weaknesses']:
            markdown += f"- ✗ {weakness}\n"
    else:
        markdown += "- No major weaknesses identified.\n"
    
    if report.get('surface_breakdown'):
        markdown += "\n## Surface Breakdown\n\n"
        for surface, stats in report['surface_breakdown'].items():
            markdown += f"### {surface.title()}\n"
            markdown += f"- Matches: {stats['matches']}\n"
            markdown += f"- Wins: {stats['wins']}\n"
            markdown += f"- Win Rate: {stats['win_rate']}\n\n"
    
    return markdown
