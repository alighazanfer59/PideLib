import plotly.graph_objects as go

def draw_line_traces(df, columns=[], colors=None, separate_y=False, fig=None):
    """
    Plots line traces from specified columns on a candlestick chart.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        columns (list, optional): List of column names to plot as lines. Defaults to [].
        colors (list, optional): List of colors for the lines. Defaults to None (uses blue).
        separate_y (bool, optional): Whether to use separate y-axes for the lines. Defaults to False.
        fig (go.Figure, optional): Existing figure to add traces to. Defaults to None.

    Returns:
        go.Figure: The updated figure with additional line traces.
        
    Example usage for new plot:
    df should be your DataFrame
    fig = draw_line_traces(df, columns=['LSR_top', 'LSR_pos'], colors=['blue', 'red'], separate_y=True)
    fig.show()

    Example usage for adding to existing plot:
    existing_fig = go.Figure()  # Or your existing figure
    updated_fig = draw_line_traces(df, columns=['LSR_top', 'LSR_pos'], colors=['blue', 'red'], separate_y=True, fig=existing_fig)
    updated_fig.show()
        
    """
    data = []
    layout = {}

    if colors is None:
        colors = ['blue'] * len(columns)  # Default to blue for all lines

    for i, col in enumerate(columns):
        line = go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col,
            line=dict(color=colors[i])
        )

        if separate_y:
            position = 1.0 - (i * 0.05)  # Corrected position calculation
            y_axis = dict(
                title=col,
                anchor='x',
                overlaying='y',
                side='right',
                showgrid=False,
                position=position
            )
            layout[f"yaxis{i + 2}"] = y_axis
            line.update(yaxis=f'y{i + 2}')
            data.append(line)
        else:
            data.append(line)

    if fig is None:
        # Create a new figure if none is provided
        fig = go.Figure(data=data)
        fig.update_layout(layout)
    else:
        # Add traces to the existing figure
        for trace in data:
            fig.add_trace(trace)
        fig.update_layout(**layout)

    return fig

