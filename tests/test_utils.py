import pytest
import pandas as pd

import sys
import os
# Add the root directory to the path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
print(os.path.abspath(__file__))  # Print the current path to verify the directory is added
from pide_lib import getData  # Ensure this imports the function correctly


# test getData function in the utils file
def test_getData():
    ticker = "BTCUSDT"
    interval = "1m"
    start_str = "2023-01-01 00:00:00"
    end_str = "2023-01-02 00:00:00"
    trading_type = "futures"
    klines = getData(ticker, interval, start_str, end_str, trading_type)
    assert isinstance(klines, list), "Output is not a list"     # check if the output is a list
    assert len(klines) > 0, "Output list is empty"              # check if the list is not empty
    assert isinstance(klines[0], list), "Output list does not contain lists"  # check if the elements of the list are lists
    assert len(klines[0]) == 12, "Output list does not contain 12 elements"   # check if the lists contain 12 elements
    
    # check if the first element of the list is a timestamp
    assert isinstance(klines[0][0], pd.Timestamp), "First element of the list is not a timestamp"
    return klines

# test the getData function with invalid inputs
# def test_getData_invalid():
#     ticker = "BTCUSDT"
#     interval = "1m"
#     start_str = "2023-01-01 00:00:00"
#     end_str = "2023-01-02 00:00:00"
#     trading_type = "invalid"
#     klines = getData(ticker, interval, start_str, end_str, trading_type)
#     assert klines is None, "Output is not None"  # check if the output is None

#     ticker = "BTCUSDT"
#     interval = "1m"
#     start_str = "2023-01-01 00:00:00"
#     end_str = "2023-01-02 00:00:00"
#     trading_type = "spot"
#     klines = getData(ticker, interval, start_str, end_str, trading_type)
#     assert klines is None, "Output is not None"  # check if the output is None

#     ticker = "invalid"
#     interval = "1m"
#     start_str = "2023-01-01 00:00:00"
#     end_str = "2023-01-02 00:00:00"
#     trading_type = "futures"
#     klines = getData(ticker, interval, start_str, end_str, trading_type)
#     assert klines is None, "Output is not None"  # check if the output is None

#     ticker = "BTCUSDT"
#     interval = "invalid"
#     start_str = "2023-01-01 00:00:00"
#     end_str = "2023-01-02 00:00:00"
#     trading_type = "futures"
#     klines = getData(ticker, interval, start_str, end_str, trading_type)
#     assert klines is None, "Output is not None"  # check if the output is None

#     ticker = "BTCUSDT"
#     interval = "1m"
#     start_str = "invalid"
#     end_str = "2023-01-02 00:00:00"
#     trading_type = "futures"
#     klines = getData(ticker, interval, start_str, end_str, trading_type)
#     assert klines is None, "Output is not None"  # check if the output is None

#     return klines

# test the getData function with valid input
def test_getData_valid():
    ticker = "BTCUSDT"
    interval = "1m"
    start_str = "2023-01-01 00:00:00"
    end_str = "2023-01-02 00:00:00"
    trading_type = "futures"
    klines = getData(ticker, interval, start_str, end_str, trading_type)
    assert klines is not None, "Output is None"  # check if the output is not None
    return klines

if __name__ == "__main__":
    test_getData()
    # test_getData_invalid()
    # test_getData_valid()
    print("All tests passed")


