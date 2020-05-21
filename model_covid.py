import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt

# from curvefit.core.model import CurveModel
from curvefit.core.functions import ln_gaussian_cdf

# Issues with numpy on Windows: https://stackoverflow.com/a/51091218

# TODO:
#  Run get_anaplan_params.py
#  Parse chunk_data_parsed_array (set var name = its accompanying value)
#  Plug vars into curvefit model (COVID deaths?)
#  Get resulting projections (as CSV?)
#  Import projections into Anaplan


np.random.seed(1234)

# Create example data -- both death rate and log death rate
df = pd.DataFrame()
df['time'] = np.arange(100)
df['death_rate'] = np.exp(.1 * (df.time - 20)) / (1 + np.exp(.1 * (df.time - 20))) + \
                   np.random.normal(0, 0.1, size=100).cumsum()
df['ln_death_rate'] = np.log(df['death_rate'])
df['group'] = 'all'
df['intercept'] = 1.0
print(df)

# Set up the CurveModel
model = CurveModel(
    df=df,
    col_t='time',
    col_obs='ln_death_rate',
    col_group='group',
    col_covs=[['intercept'], ['intercept'], ['intercept']],
    param_names=['alpha', 'beta', 'p'],
    link_fun=[lambda x: x, lambda x: x, lambda x: x],
    var_link_fun=[lambda x: x, lambda x: x, lambda x: x],
    fun=ln_gaussian_cdf
)

# Fit the model to estimate parameters
model.fit_params(fe_init=[0, 0, 1.],
                 fe_gprior=[[0, np.inf], [0, np.inf], [1., np.inf]])

# Get predictions
y_pred = model.predict(
    t=df.time,
    group_name=df.group.unique()
)

# Plot results
plt.plot(df.time, y_pred, '-')
plt.plot(df.time, df.ln_death_rate, '.')
