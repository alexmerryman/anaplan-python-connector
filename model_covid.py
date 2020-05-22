import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Using CurveFit package from: https://github.com/ihmeuw-msca/CurveFit
# Install the CurveFit package in your virtual environment by running `pip install git+https://github.com/ihmeuw-msca/CurveFit.git` from the command line
# NOTE: CurveFit requires Python 3.6+, as it uses f strings in its error handling
from curvefit.core.model import CurveModel
from curvefit.core.functions import ln_gaussian_cdf

# Issues with numpy (specifically optimization functions in scipy, which is based on numpy) on Windows: https://stackoverflow.com/a/51091218 -- easier to just run on Linux/Unix

# TODO:
#  Run get_anaplan_params.py
#  Parse chunk_data_parsed_array (set var name = its accompanying value)
#  Plug vars into curvefit model (COVID deaths?)
#  Get resulting projections (as CSV?)
#  Import projections into Anaplan


# np.random.seed(1234)
#
# # Create example data -- both death rate and log death rate  # TODO: Get this from Anaplan? Just death rate -- log death rate can be calculated
# df = pd.DataFrame()
# df['time'] = np.arange(100)
# df['death_rate'] = np.exp(.1 * (df.time - 20)) / (1 + np.exp(.1 * (df.time - 20))) + \
#                    np.random.normal(0, 0.1, size=100).cumsum()
# df['ln_death_rate'] = np.log(df['death_rate'])
# df['group'] = 'all'
# df['intercept'] = 1.0  # Default to 1.0 ?
# print(df)


def main(model_args_dict, verbose=False, charts=False):
    # TODO: Create dict to hold param values, pass dict as single arg to this main() function
    # parse model args from dict
    df = model_args_dict['df']
    col_t = model_args_dict['col_t']
    col_obs = model_args_dict['col_obs']
    col_group = model_args_dict['col_group']
    col_covs = model_args_dict['col_covs']
    param_names = model_args_dict['param_names']
    link_fun = model_args_dict['link_fun']
    var_link_fun = model_args_dict['var_link_fun']
    fun = model_args_dict['fun']
    fe_init = model_args_dict['fe_init']
    fe_gprior = model_args_dict['fe_gprior']

    # Set up the CurveModel
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

    # Fit the model to estimate parameters  # TODO: Get these init params from Anaplan
    # Can't pass `smart_initialization=True` with only 1 group of data
    if len(df[col_group].unique.tolist()) == 1:
        model.fit_params(fe_init=fe_init,
                         fe_gprior=fe_gprior)
    else:
        model.fit_params(fe_init=fe_init,
                         fe_gprior=fe_gprior,
                         smart_initialize=True)


    # Get predictions
    y_pred = model.predict(
        t=df[col_t],
        group_name=df[col_group].unique()
    )

    # TODO: Join y_pred with time?
    print(y_pred)

    if charts:
        # Plot results
        plt.plot(df[col_t], y_pred, '-')
        plt.plot(df[col_t], df[col_obs], '.')
        plt.show()

    return model, y_pred
