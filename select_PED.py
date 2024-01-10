import pandas as pd
import xarray as xr
from config import RUNNAME, FOLDER, OFOLDER

# settings
COUNTRIES = ['NOR', 'FRA', 'ITA', 'SWE', 'CHE', 'ESP']
VAR = 'residual'
QSET = 0.97
NR_OF_EVENTS = 160
SEASONS = ['all', 'winter', 'summer']

def group_as_event(df, daygap=3):
    """
    give all events in a run a number. Consider days within percentile that are less 
    than 2 days apart as the same event 

    parameters
    ----------
    group (pd.group): a grouped panda series

    returns
    -------
    an index for all consequative date with a max of daygap days apart
    """
    dt = df
    day = pd.Timedelta(f'{daygap}d')
    breaks = (dt.diff() > day)
    return breaks.cumsum() + 1

def main():
    all_events = {}
    for season in SEASONS:
        for country in COUNTRIES:
            # open energy data 
            ds = xr.open_dataset(FOLDER + f'{country}_{RUNNAME}.nc')[[VAR]]
            # move to pandas dataframe
            df = ds.drop('country').to_dataframe()

            # reset the index
            dft = df.reset_index()

            # cut per season
            if season == 'summer':
                dft = dft.loc[dft.time.dt.dayofyear >= 152].loc[dft.time.dt.dayofyear <274]   
            if season == 'winter':
                dft0 = dft.loc[dft.time.dt.dayofyear < 152]
                dft1 = dft.loc[dft.time.dt.dayofyear >= 274]
                dft = pd.concat([dft0, dft1])

            # select all days within defined percentile q (QSET)
            dft = dft.loc[dft[VAR]>dft[VAR].quantile(QSET)]
            # give all events in a run a number. 
            # Consider days within percentile that are less than x days apart as the same event 
            dft['event_of_run'] = dft.groupby('runs')['time'].transform(group_as_event)
            # index the events over all the runs (not per run)
            dft['event_nr'] = dft.groupby(['runs', 'event_of_run']).ngroup()
            # take the mean residual per event
            dft[f'event_mean_{VAR}'] = dft.groupby('event_nr')[VAR].transform('mean')
            dft[f'event_total_{VAR}'] = dft.groupby('event_nr')[VAR].transform('sum')
            # assign event_nr based on level of total residual load
            dft = dft.sort_values([f'event_total_{VAR}', 'time'], ascending=[False, True])
            dft['event_nr'] = dft.groupby(['runs', 'event_of_run'], sort=False).ngroup()
            dft['event_nr'] = dft['event_nr']+1
            # count the number of days an event lasts
            dft['nr_of_days'] = dft.groupby('event_nr')[[VAR]].transform('count')
            # make a seperate dataset of the nr of days that the events last
            nr_of_days = dft.groupby('event_nr').count()[[VAR]]  
            # only select n-events
            dft = dft.loc[dft.event_nr<(NR_OF_EVENTS)+1]
            events = dft 
            # add some data
            events['month'] = events.time.dt.month
            events['doy'] = events.time.dt.dayofyear
            events['month'] = events.groupby('event_nr')['month'].transform(lambda x: x.mode().iloc[0])
            events['week'] = events.time.dt.isocalendar().week
            events['week'] = events.groupby('event_nr')['week'].transform(lambda x: x.mode().iloc[0])
            all_events[country] = events
        # merge into dataframe and save
        df_all_events = pd.concat(
            [all_events[country][all_events[country].event_nr <= NR_OF_EVENTS].assign(country=country) for country in COUNTRIES]
        ).reset_index()
        df_all_events.to_csv(f'{OFOLDER}PED_{VAR}_q{QSET}_{season}_{RUNNAME}.csv')

if __name__ == "__main__":
    main()