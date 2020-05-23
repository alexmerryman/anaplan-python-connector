import numpy as np
import pandas as pd
import connect_anaplan


def full_run(input1, input2, input3, etc, sim_data=False):
    if sim_data:
        np.random.seed(1234)

        # Create example data -- both death rate and log death rate  # TODO: Get this from Anaplan? Just death rate -- log death rate can be calculated
        df = pd.DataFrame()
        df['time'] = np.arange(100)
        df['death_rate'] = np.exp(.1 * (df.time - 20)) / (1 + np.exp(.1 * (df.time - 20))) + \
                           np.random.normal(0, 0.1, size=100).cumsum()
        df['ln_death_rate'] = np.log(df['death_rate'])
        df['group'] = 'all'
        df['intercept'] = 1.0  # Default to 1.0 ?

    else:
        # get data from Anaplan
        df = connect_anaplan()  # TODO

    model_args_dict = {
        'df': df,
        'col_t': 'time',
        'col_obs': 'ln_death_rate',
        'col_group': 'group',
        'col_covs': [['intercept'], ['intercept'], ['intercept']],
        'param_names': ['alpha', 'beta', 'p'],
        'link_fun': [lambda x: x, lambda x: x, lambda x: x],
        'var_link_fun': [lambda x: x, lambda x: x, lambda x: x],
        'fun': 'ln_gaussian_cdf',
        'fe_init': [0, 0, 1.],
        'fe_gprior': [[0, np.inf], [0, np.inf], [1., np.inf]]
    }