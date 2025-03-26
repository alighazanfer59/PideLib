# PideLib 📈

PideLib is a personal Python library containing frequently used functions, starting with data visualization using Plotly.

## Features
✅ Plotly-based visualization functions  
✅ Easy integration with pandas DataFrames  
✅ Modular structure for future additions  

## Installation

### Install via GitHub:
You can install the latest version directly from GitHub:
```bash
pip install git+https://github.com/alighazanfer59/PideLib.git
```

Install Locally for Development:
Clone the repository and install it in editable mode:

```bash
git clone https://github.com/alighazanfer59/PideLib.git
cd PideLib
pip install -e .
```
### Example Usage:

```bash
import pandas as pd
import plotly.graph_objects as go
from pide_lib import plotly_figs

#### Example DataFrame

df = pd.DataFrame({
    'timestamp': pd.date_range(start="2024-01-01", periods=100, freq='D'),
    'LSR_top': range(100),
    'LSR_pos': range(100, 200)
})
df.set_index('timestamp', inplace=True)

#### Plot lines
fig = plotly_figs.draw_line_traces(df, columns=['LSR_top', 'LSR_pos'], colors=['blue', 'red'], separate_y=True)
fig.show()
```

### Example Usage2:

```bash
import pandas as pd
from pide_lib import getData

#### Get Data from binance
df = getData("BTCUSDT", "1h", "2021-01-01", "2025-12-31", "futures")
```


