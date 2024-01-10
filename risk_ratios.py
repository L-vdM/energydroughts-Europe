
import xarray as xr
import numpy as np
import math
import pandas as pd

from config import RUNNAME, FOLDER,OFOLDER

import matplotlib.pyplot as plt
import seaborn as sns

def open_energy_dataset(country, months, timestep='months'):
    ds2 = xr.open_dataset(FOLDER + f'{country}_{RUNNAME}.nc')
    ## drop first and last couple of months because of 
    clime = ds2.mean(dim='runs').groupby('time.dayofyear').mean()
    ds3 = ds2.stack(z=('runs', 'time')).groupby('time.dayofyear') -clime
    ds3 = ds3.unstack()
    ds3['runs']=np.arange(0,160)
    # select summer events (jan _ feb)
    if timestep == 'months':
        ds3 = ds3.sel(time=ds3.time.dt.month.isin(months)).groupby('time.year').mean()
    elif timestep == 'days':
        ds3 = ds3.sel(time=ds3.time.dt.dayofyear.isin(months)).groupby('time.year').mean()
    dse = ds3.stack(z=('runs', 'year'))
    return dse

def calculate_95CI_RR(a, b, c, d):
    """
    Calculate the 95% Confidence Interval for a Risk Ratio.

    :param a: Number of events in the exposed group
    :param b: Number of non-events in the exposed group
    :param c: Number of events in the non-exposed group
    :param d: Number of non-events in the non-exposed group
    :return: A tuple containing the lower and upper limits of the 95% CI
    """
    # Calculate Risk Ratio (RR)
    RR = (a / (a + b)) / (c / (c + d))

    # Calculate the natural log of the Risk Ratio
    lnRR = math.log(RR)

    # Calculate the Standard Error (SE) of ln(RR)
    SE_lnRR = math.sqrt((1/a) - (1/(a + b)) + (1/c) - (1/(c + d)))

    # Calculate the lower and upper limits of the 95% CI for ln(RR)
    lower_lnRR = lnRR - 1.96 * SE_lnRR
    upper_lnRR = lnRR + 1.96 * SE_lnRR

    # Transform the CI back to the RR scale
    lower_CI = math.exp(lower_lnRR)
    upper_CI = math.exp(upper_lnRR)

    return lower_CI, upper_CI

def compute_risk_ratios(countries, q_values, year_later,
                        q_event, flip_sign,
                        dse_event, var_of_event,
                        dse_poi, var_of_poi,):
    
    """
    Compute the risk ratios and the 95% confidence interval for temporally compounding events
    """
    # initiate
    dfhm = pd.DataFrame(index=countries)
    dfSI = pd.DataFrame(index=countries)
    chances = {}
    chances_all = {}
    SI = {}
    for q2 in q_values:
        for country in countries:
            dse = dse_event[country]
            dsa = dse[[var_of_event]]
            # when is it an event?
            event_threshold = float(dsa[var_of_event].quantile(dim='z', q=q_event).values)
            dsevents = dsa.where((flip_sign*dsa)>(flip_sign*event_threshold), drop=True) 

            # get the timestamps during event
            timestamps2 = dsevents.z.values
            ds_poi = dse_poi[country]
            dsro = ds_poi[[var_of_poi]]
            if year_later:
                # drop one year so I can analyse the year after
                dsro = dsro.unstack().sel(year = range(2001,2009)).stack(z=('runs', 'year'))
            # the variable of interests lower than a certain threshold
            drought = dsro.where((flip_sign*dsro)<(flip_sign*dsro.quantile(dim='z', q=q2)), drop=True)

            # Timestamps period of interest above or below threshold
            timestamps = [ts for ts in drought.z.values if ts in list(dsa.z.values)]

            # one year later timestamps
            if year_later:
                timestamps2 = [(ts[0], ts[1]+1) for ts in timestamps]
                timestamps2 = [ts for ts in timestamps2 if ts in list(dsa.z.values)]
            else:
                timestamps2 = timestamps

            if len(timestamps) != len(timestamps2):
                print('ERROR: different amount of events')
                print(f'timestamps1 amount of events {len(timestamps)}')
                print(f'timestamps2 amount of events {len(timestamps2)}')

            # is there an event the period after?
            isevent = (flip_sign*dsa.sel(z=timestamps2)[var_of_event].values) > (flip_sign*event_threshold)
            allevents = (flip_sign*dsa[var_of_event].values) > (flip_sign*event_threshold)

            # save in dictionary
            chances[country] = isevent.sum()/len(isevent)
            chances_all[country] = allevents.sum()/len(allevents)

            # compute statistical significance
            a = isevent.sum()
            b = len(isevent)-isevent.sum()
            c = allevents.sum()
            d = len(allevents)-allevents.sum()
            lower_CI, upper_CI = calculate_95CI_RR(a, b, c, d)
            SI[country] = False if lower_CI > 1 else True

        df = pd.DataFrame([chances, chances_all], index=['after drought', 'all years']).T
        df['risk_ratio'] = df['after drought']/ df['all years']
        # add to dataframes for each country
        dfhm.loc[:, q2] = df['risk_ratio']
        dfSI.loc[:, q2] = pd.DataFrame(SI, index=[q2]).T
    return dfhm, dfSI

countries = ['NOR', 'CHE','SWE','ITA','ESP', 'FRA']
# days of interest for TCCI (inflow before summer event)
pois_TCCI = {'CHE':(-65,-35),  
       'NOR':(-65,-35),
       'SWE':(-65,-35),
       'ITA':(-90,-60),
       'ESP':(-90,-60),
       'FRA':(-90,-60),}
start_event = 213 #doy on which event starts
doy_pois_TCCI = {k:(start_event+i, start_event+j) for k, (i,j) in pois_TCCI.items()}
moy_pois_TCCI =  {'CHE': 6,'NOR': 6, 'SWE': 6,
                  'ITA': 5,'ESP': 5, 'FRA':5}

# days of interest for figure 4 (inflow before winter event)
pois_TCCII = {'CHE':(-290,-250),  
       'NOR':(-260,-220),
       'SWE':(-250,-210),
       'ITA':(-275,-240),
       'ESP':(-275,-240),
       'FRA':(-275,-240),}
start_event = 31 #doy on which event starts
doy_pois_TCCII = {k:(365+start_event+i, 365+start_event+j) for k, (i,j) in pois_TCCII.items()}

# days of intrest for figure 5
pois_TCCIII = {'CHE': (90,150), 
             'FRA': (90,150),
             'ITA': (90,150),
             'SWE': (90,150), 
             'NOR': (90,150),
             'ESP': (90,150)
       }
start_event = 31 #doy on which event starts
doy_pois_TCCIII= {k:(start_event+i, start_event+j) for k, (i,j) in pois_TCCIII.items()}

# Variables during the selected winter Energy Drought Window (Februari)
dsewinter = {country:open_energy_dataset(country, (2)) for country in countries}
print('computing winter done')
# Variables during the selected summer Energy Drought Window (August)
dsesummer = {country:open_energy_dataset(country, (8)) for country in countries}
print('computing summer done')

# Variables during temporally compounding conditions I
dse_poi_TCCI = {country:open_energy_dataset(country, 
                                            range(doy_pois_TCCI[country][0],doy_pois_TCCI[country][1])
                                            , timestep='days') for country in countries}

print('computing TCCI done')
# Variables during temporally compounding conditions II
dse_poi_TCCII = {country:open_energy_dataset(country, 
                                            range(doy_pois_TCCII[country][0],doy_pois_TCCII[country][1])
                                            , timestep='days') for country in countries}
print('computing TCCII done')
# Variables during temporally compounding conditions III
dse_poi_TCCIII = {country:open_energy_dataset(country, 
                                            range(doy_pois_TCCIII[country][0],doy_pois_TCCIII[country][1])
                                            , timestep='days') for country in countries}
print('computing TCCIII done')

## Compute the risk ratios for the three temporally compouning conditions
dfhm_TCCI, dfSI_TCCI = compute_risk_ratios(countries, [0.1, 0.2, 0.3, 0.4, 0.5], False, 0.9, 1, 
                                           dsesummer, 'residual', dse_poi_TCCI, 'Ein')
dfhm_TCCII, dfSI_TCCII = compute_risk_ratios(countries, [0.1, 0.2, 0.3, 0.4, 0.5], True, 0.9, 1, 
                                             dsewinter, 'residual',dse_poi_TCCII, 'Ein')
dfhm_TCCIII, dfSI_TCCIII = compute_risk_ratios(countries, [0.9,0.8,0.7,0.6,0.5], False, 0.1, -1, 
                                               dse_poi_TCCIII, 'Ein', dsewinter, 'residual')

RRs = [dfhm_TCCI, dfhm_TCCII, dfhm_TCCIII]
CIs = [dfSI_TCCI, dfSI_TCCII, dfSI_TCCIII]

for i, tcc in enumerate(['TCCI', 'TCCII', 'TCCIII']):
    RRs[i].to_csv(f'{OFOLDER}rr_{tcc}_{RUNNAME}.csv')
    CIs[i].to_csv(f'{OFOLDER}ci95_{tcc}_{RUNNAME}.csv')
    

# plot the heatmaps
fig,axs = plt.subplots(1,3, figsize=(17,5))

cmaps = ['Blues','Reds','Blues']
xlabels = ['reservoir inflow percentile','reservoir inflow percentile', 'percentile of Feb residual load']
ylabels = ['risk ratio of 1-in-10 year August EDW [-]', 
           'risk ratio of 1-in-10 year Februari EDW [-]',
           'risk ratio of 1-in-10 year low inflow event [-]']
for i, tcc in enumerate(['TCCI', 'TCCII', 'TCCIII']):
    axs[i].set_title(tcc)
    sns.heatmap(RRs[i], annot=True, ax=axs[i], cmap = cmaps[i],
               cbar_kws={'label': ylabels[i], })
    axs[i].set_xlabel(xlabels[i])
    # Overlaying texture on True values
    for y in range(CIs[i].shape[0]):
        for x in range(CIs[i].shape[1]):
            if CIs[i].iloc[y, x]:
                axs[i].add_patch(plt.Rectangle((x, y), 1, 1, fill=False, hatch='//', edgecolor='lightgrey'))
plt.savefig(f'{OFOLDER}TCC_risk_ratios.png')