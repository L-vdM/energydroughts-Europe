# energydroughts-Europe

## Overview

energydroughts-Europe is a repository dedicated to the analysis of energy droughts as a result from processes that cause (temporally) compounding impacts in the energy and meteorological system as discussed in the paper titled "Temporally compounding energy droughts in European electricity systems with hydropower".


## Anonymity for Review
This repository is currently anonymous for double-blind review purposes. Upon completion of the review process, it will be published under the personal account of the author(s). If you are reviewing this repository and require any specific information or have questions, please reach out through the appropriate channels of journal.

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

# Future Contact
Post-review, this project will be moved to the personal GitHub account of the author(s). Future updates and correspondence will take place there. Watch this space for the updated link post-review.





