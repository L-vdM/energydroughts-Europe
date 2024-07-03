# energydroughts-Europe


## Overview

energydroughts-Europe is a repository dedicated to the analysis of energy droughts as a result from processes that cause (temporally) compounding impacts in the energy and meteorological system as discussed in the paper titled "Temporally compounding energy droughts in European electricity systems with hydropower". This work has been accepted for publication in Nature Energy. 

## Citing
If you use this code, or adapt it for your work, please cite our publication. Lieke van der Most, Karin van der Wiel, Winnie Gerbens-Leenes et al. Temporally compounding energy droughts in European electricity systems with hydropower, 10 January 2024, PREPRINT (Version 1) available at Research Square [https://doi.org/10.21203/rs.3.rs-3796061/v1]


## Repository Structure

- `select_EDW.py`: Script to select Energy Drought Windows (EDW) based on predefined criteria related to energy production and demand.
- `select_PEDs.py`: Script to identify Persistent Energy Droughts (PEDs) from the identified EDW.
- `risk_ratios.py`: Script for calculating Risk Ratios (RR) to quantify the probability and impact of energy drought events.
- `config.py`: Configuration file for setting paths to the energy input files (Note: Input files need to be provided by the user).
- results of the runs as used in the publication can be found in the `data` folder

## Configuration

Set up the required paths in the `config.py` file to point to the energy data files.

```python
# example configuration in config.py
FOLDER = "/path/to/your/energy/data/files"

```

## Usage
To execute the scripts, navigate to the repository directory and run:
```bash
python select_EDW.py
python select_PEDs.py
python risk_ratios.py
```

# questions or Contributions to this work
Contributions to this work are appreciated and encouraged.

To contribute an update or if you have any other questions feel free to contact me.




