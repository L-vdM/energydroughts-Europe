import os
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm
from config import RUNNAME, FOLDER, OFOLDER

# Constants
RUNS = [f"h{number:03d}" for number in range(10, 170)]
VAR0 = 'residual'
COUNTRIES = ['NOR', 'SWE', 'CHE', 'ITA', 'FRA', 'ESP']
NR_OF_EVENTS = 160 
SEASONS = ['winter', 'summer', 'all']
EVENT_LENGTHS = [30]


def open_energy_dataset(country, folder):
    """Opens the energy dataset for a given country."""
    file_path = os.path.join(folder, f'/{country}_{RUNNAME}.nc')
    return xr.open_dataset(file_path)

def select_season_data(dataset, season):
    """Filters dataset based on the specified season."""
    season_months = {
        'summer': [6, 7, 8, 9],
        'winter': [1, 2, 3, 4, 5, 10, 11, 12]
    }
    if season in season_months:
        return dataset.where(dataset.time.dt.month.isin(season_months[season]), drop=True)
    return dataset

def process_events(dataset, variable, event_length, num_events):
    """Processes and identifies energy events in the dataset."""
    events = []
    timestamps = []

    if variable == 'residual_pvwind':
        dataset[variable] = (dataset['demand'] 
                             - dataset['pv_util'] - dataset['pv_roof'] 
                             - dataset['wind_offshore'] - dataset['wind_onshore'])
    
    var_data = dataset[variable]

    for _ in tqdm(range(num_events)):
        rolling_sum = var_data.rolling(time=event_length).sum()
        max_event = rolling_sum.where(rolling_sum == rolling_sum.max(), drop=True)
        
        max_run = max_event.runs.values[0]
        max_timestamp = max_event.time.values[0]
        min_timestamp = max_timestamp - np.timedelta64(event_length - 1, 'D')

        timeslice = slice(min_timestamp, max_timestamp)
        events.append((max_run, timeslice))
        timestamps.append((max_run, min_timestamp, max_timestamp))

        event_data = dataset[variable].sel(time=timeslice, runs=max_run).expand_dims('runs')
        event_data.name = 'residual_event'
        
        merged_data = xr.merge([var_data, event_data])
        var_data = var_data.where((merged_data[variable] - merged_data['residual_event']) != 0)

    return events, timestamps

def main():
    """Main function to process energy datasets."""
    for season in SEASONS:
        for event_length in EVENT_LENGTHS:
            data_frames = []
            for country in COUNTRIES:
                print(f'Processing {NR_OF_EVENTS} {event_length}-day events for {country}')
                dataset = open_energy_dataset(country, FOLDER)
                season_data = select_season_data(dataset, season)
                events, timestamps = process_events(season_data, VAR0, event_length, NR_OF_EVENTS)

                df = pd.DataFrame(timestamps, columns=['runs', 'start_time', 'end_time'])
                df['country'] = country
                data_frames.append(df)

            all_events_df = pd.concat(data_frames).reset_index()
            all_events_df = all_events_df.rename({'index': 'event_number'}, axis=1)
            all_events_df['event_number'] += 1

            output_file = f'{OFOLDER}{VAR0}_el{event_length}_{season}_{RUNNAME}_2.csv'
            all_events_df.to_csv(output_file)
            print(f'Saved to {output_file}')

if __name__ == "__main__":
    main()
