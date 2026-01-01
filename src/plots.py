"""
Plotting and visualization utilities for Tennis Performance Analysis.
Creates charts and figures for the dashboard.
"""

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Set default seaborn style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 7)


def create_bar_comparison(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: str = None,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> go.Figure:
    """
    Create a comparative bar chart using Plotly.

    Args:
        data: Input DataFrame
        x: X-axis column
        y: Y-axis column
        color: Column to color by (optional)
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label

    Returns:
        Plotly Figure object
    """
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        barmode="group" if color else "relative",
    )

    fig.update_layout(
        xaxis_title=x_label or x,
        yaxis_title=y_label or y,
        showlegend=True,
        hovermode="x unified",
    )

    return fig


def create_line_plot(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: str = None,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> go.Figure:
    """
    Create a line plot using Plotly.

    Args:
        data: Input DataFrame
        x: X-axis column
        y: Y-axis column
        color: Column to color by (optional)
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label

    Returns:
        Plotly Figure object
    """
    fig = px.line(data, x=x, y=y, color=color, title=title, markers=True)

    fig.update_layout(
        xaxis_title=x_label or x,
        yaxis_title=y_label or y,
        showlegend=True,
        hovermode="x unified",
    )

    return fig


def create_pie_chart(
    data: pd.DataFrame, names: str, values: str, title: str = ""
) -> go.Figure:
    """
    Create a pie chart using Plotly.

    Args:
        data: Input DataFrame
        names: Column for pie labels
        values: Column for pie values
        title: Chart title

    Returns:
        Plotly Figure object
    """
    fig = px.pie(data, names=names, values=values, title=title)

    fig.update_layout(showlegend=True, hovermode="closest")

    return fig


def create_win_loss_comparison_matplotlib(
    data: pd.DataFrame, x: str, y: str, title: str = ""
) -> plt.Figure:
    """
    Create a win/loss comparison using Matplotlib.

    Args:
        data: Input DataFrame
        x: X-axis column
        y: Y-axis column
        title: Chart title

    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    sns.lineplot(data=data, x=x, y=y, marker="o", ax=ax)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(x, fontsize=12)
    ax.set_ylabel(y, fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def create_multiline_comparison(
    data: pd.DataFrame, x: str, y: str, hue: str, title: str = ""
) -> plt.Figure:
    """
    Create a multi-line comparison using Seaborn/Matplotlib.

    Args:
        data: Input DataFrame
        x: X-axis column
        y: Y-axis column
        hue: Column to split by (for multiple lines)
        title: Chart title

    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    sns.lineplot(data=data, x=x, y=y, hue=hue, marker="o", ax=ax)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(x, fontsize=12)
    ax.set_ylabel(y, fontsize=12)
    ax.legend(title=hue, bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def create_surface_distribution(
    match_data: pd.DataFrame, tournament: str = None
) -> go.Figure:
    """
    Create a surface distribution pie chart.

    Args:
        match_data: Match DataFrame
        tournament: Optional tournament filter

    Returns:
        Plotly Figure object
    """
    if tournament:
        data = match_data[match_data["t_name"] == tournament]
    else:
        data = match_data

    surface_stats = data["surface"].value_counts().reset_index()
    surface_stats.columns = ["surface", "count"]

    fig = px.pie(
        surface_stats, names="surface", values="count", title="Surface Distribution"
    )

    return fig


def create_heatmap_correlation(data: pd.DataFrame, title: str = "") -> plt.Figure:
    """
    Create a correlation heatmap.

    Args:
        data: Input DataFrame (should contain numeric columns)
        title: Chart title

    Returns:
        Matplotlib Figure object
    """
    numeric_data = data.select_dtypes(include=["float64", "int64"])

    fig, ax = plt.subplots(figsize=(12, 10))

    correlation_matrix = numeric_data.corr()
    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        ax=ax,
        cbar_kws={"label": "Correlation"},
    )

    ax.set_title(title, fontsize=14, fontweight="bold")

    plt.tight_layout()
    return fig


def create_player_comparison_metrics(
    data1: pd.DataFrame, data2: pd.DataFrame, player1: str, player2: str, metrics: list
) -> go.Figure:
    """
    Create a grouped bar chart comparing two players across multiple metrics.

    Args:
        data1: First player DataFrame
        data2: Second player DataFrame
        player1: First player name
        player2: Second player name
        metrics: List of metric columns to compare

    Returns:
        Plotly Figure object
    """
    comparison_data = []

    for metric in metrics:
        if metric in data1.columns and metric in data2.columns:
            val1 = data1[metric].iloc[0] if len(data1) > 0 else 0
            val2 = data2[metric].iloc[0] if len(data2) > 0 else 0

            comparison_data.append({"Player": player1, "Metric": metric, "Value": val1})
            comparison_data.append({"Player": player2, "Metric": metric, "Value": val2})

    df_comparison = pd.DataFrame(comparison_data)

    fig = px.bar(
        df_comparison,
        x="Metric",
        y="Value",
        color="Player",
        barmode="group",
        title=f"Player Comparison: {player1} vs {player2}",
    )

    fig.update_layout(hovermode="x unified")

    return fig


def create_trend_with_bounds(
    data: pd.DataFrame,
    x: str,
    y_mean: str,
    y_lower: str = None,
    y_upper: str = None,
    title: str = "",
) -> go.Figure:
    """
    Create a line plot with optional confidence bounds.

    Args:
        data: Input DataFrame
        x: X-axis column
        y_mean: Column for mean line
        y_lower: Column for lower bound (optional)
        y_upper: Column for upper bound (optional)
        title: Chart title

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Add mean line
    fig.add_trace(
        go.Scatter(
            x=data[x],
            y=data[y_mean],
            mode="lines+markers",
            name="Mean",
            line=dict(color="blue", width=2),
        )
    )

    # Add bounds if provided
    if y_upper and y_upper in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data[x],
                y=data[y_upper],
                mode="lines",
                name="Upper Bound",
                line=dict(color="rgba(0,0,255,0)"),
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=data[x],
                y=data[y_lower],
                mode="lines",
                name="Lower Bound",
                line=dict(color="rgba(0,0,255,0)"),
                fillcolor="rgba(0,0,255,0.2)",
                fill="tonexty",
                showlegend=False,
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title=x,
        yaxis_title=y_mean,
        hovermode="x unified",
        showlegend=True,
    )

    return fig


def close_all_figures():
    """Close all matplotlib figures to free memory."""
    plt.close("all")
    logger.info("Closed all matplotlib figures")
