import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from curvefit.core.model import CurveModel
from curvefit.core.functions import ln_gaussian_cdf
# TODO: Import * (for above)? To make other functions available to user (accept other values for `model_args_dict['fun']`)

# Using CurveFit package from: https://github.com/ihmeuw-msca/CurveFit

# Install the CurveFit package in your virtual environment by running:
# `pip install git+https://github.com/ihmeuw-msca/CurveFit.git` from the command line.

# NOTE: CurveFit requires Python 3.6+, as it uses f-strings in its error handling.

# NOTE: The CurveFit package uses scipy's optimization functions, which in turn use numpy's linear algebra functions.
# This presents significant issues on Windows, since the Windows OS lacks certain base dependencies for handling
# linear algebra (more details can be found here: https://stackoverflow.com/a/51091218). One solution is to install the
# Windows-binary versions of numpy and pandas (here: https://www.lfd.uci.edu/~gohlke/pythonlibs/, also use pipwin), but
# it's probably easier to just use a Linux/Unix machine.


# np.random.seed(1234)
#
# # Create example data -- both death rate and log death rate
# df = pd.DataFrame()
# df['time'] = np.arange(100)
# df['death_rate'] = np.exp(.1 * (df.time - 20)) / (1 + np.exp(.1 * (df.time - 20))) + \
#                    np.random.normal(0, 0.1, size=100).cumsum()
# df['ln_death_rate'] = np.log(df['death_rate'])
# df['group'] = 'all'
# df['intercept'] = 1.0  # Default to 1.0 ?
# print(df)


def fit_model_predict(model_args_dict, verbose=False, charts=False):
    # Parse model arguments from model_args_dict
    if verbose:
        print("Getting model arguments/params from model_args_dict...")
    df = model_args_dict['df']
    col_t = model_args_dict['col_t']
    col_obs = model_args_dict['col_obs']
    col_group = model_args_dict['col_group']
    col_covs = model_args_dict['col_covs']
    param_names = model_args_dict['param_names']
    link_fun = model_args_dict['link_fun']
    var_link_fun = model_args_dict['var_link_fun']
    fun = ln_gaussian_cdf  # TODO -- set this as default? How to change from full_run.py?
    fe_init = model_args_dict['fe_init']
    fe_gprior = model_args_dict['fe_gprior']

    # Set up the CurveModel
    if verbose:
        print("Instantiating the model...")
    model = CurveModel(
        df=df,
        col_t=col_t,
        col_obs=col_obs,
        col_group=col_group,
        col_covs=col_covs,
        param_names=param_names,
        link_fun=link_fun,
        var_link_fun=var_link_fun,
        fun=fun
    )

    # Fit the model to estimate parameters
    if verbose:
        print("Fitting the model...")
    if len(df[col_group].unique().tolist()) == 1:  # Can't pass `smart_initialization=True` with only 1 group of data
        model.fit_params(fe_init=fe_init,
                         fe_gprior=fe_gprior)
    else:
        model.fit_params(fe_init=fe_init,
                         fe_gprior=fe_gprior,
                         smart_initialize=True)

    # Get predictions
    if verbose:
        print("Getting model predictions...")
    y_pred = model.predict(
        t=df[col_t],
        group_name=df[col_group].unique()
    )

    y_pred_df = pd.DataFrame(data=y_pred, columns=['prediction'])
    y_pred_df = pd.concat([df[col_t], y_pred_df], axis=1, sort=False)
    print(y_pred_df)

    if charts:
        if verbose:
            print("Plotting the fitted model...")
        # Plot results
        plt.plot(y_pred_df[col_t], y_pred_df, '-')
        plt.plot(y_pred_df[col_t], df[col_obs], '.')
        plt.show()

    return model, y_pred_df
