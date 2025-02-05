import pytest
import pandas as pd
import plotly.graph_objects as go
from pide_lib import plotly_figs  # Ensure this imports the function correctly

# Test data setup
def generate_sample_df():
    # Create a sample dataframe with dummy data for testing
    data = {
        'timestamp': pd.date_range(start='2025-01-01', periods=5, freq='H'),
        'Close': [100, 105, 103, 107, 110],
        'LSR_top': [50, 52, 51, 55, 58],
        'LSR_pos': [30, 32, 31, 34, 36]
    }
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df

# Test case for drawing line traces
def test_draw_line_traces():
    # Generate a sample dataframe
    df = generate_sample_df()
    
    # Call the function to generate the plot
    fig = plotly_figs.draw_line_traces(df, columns=['LSR_top', 'LSR_pos'], colors=['blue', 'red'])
    
    # Check that the figure is a plotly figure object
    assert isinstance(fig, go.Figure), "Output is not a plotly figure"
    
    # Check that the number of traces matches the number of columns passed
    assert len(fig.data) == 2, f"Expected 2 traces, got {len(fig.data)}"
    
    # Check if the colors of the traces match the expected ones
    assert fig.data[0].line.color == 'blue', f"Expected blue for first trace, got {fig.data[0].line.color}"
    assert fig.data[1].line.color == 'red', f"Expected red for second trace, got {fig.data[1].line.color}"

# Test case for separate y-axes
def test_draw_line_traces_separate_y():
    # Generate a sample dataframe
    df = generate_sample_df()
    
    # Call the function to generate the plot with separate y-axes
    fig = plotly_figs.draw_line_traces(df, columns=['LSR_top', 'LSR_pos'], colors=['blue', 'red'], separate_y=True)
    
    # Check that the figure is a plotly figure object
    assert isinstance(fig, go.Figure), "Output is not a plotly figure"
    
    # Check that the number of y-axes is equal to the number of columns (2 axes for 2 traces)
    assert len(fig.layout) >= 3, "Expected at least 2 y-axes"

    # Check if the y-axis titles match the column names
    assert 'LSR_top' in fig.layout['yaxis2'].title.text, "Y-axis 2 title does not match expected"
    assert 'LSR_pos' in fig.layout['yaxis3'].title.text, "Y-axis 3 title does not match expected"
    
# Run the tests
if __name__ == "__main__":
    pytest.main()
