# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
#
# from curvefit.models.core_model import CoreModel
# from curvefit.core.functions import expit, normal_loss
# from curvefit.core.data import Data
# from curvefit.core.parameter import Variable, Parameter, ParameterSet
# from curvefit.solvers.solvers import ScipyOpt
#
# # from curvefit.core.model import CurveModel
# # from curvefit.core.functions import ln_gaussian_cdf
# # TODO: Import * (for above)? To make other functions available to user (accept other values for `model_args_dict['fun']`)
#
# # Using CurveFit package from: https://github.com/ihmeuw-msca/CurveFit
#
# # Install the CurveFit package in your virtual environment by running:
# # `python -m pip install git+https://github.com/ihmeuw-msca/CurveFit.git@b7178a07441abc4695b80f83ad71ebbda2ca2cff` from the command line.
#
# # NOTE: CurveFit requires Python 3.6+, as it uses f-strings in its error handling.
#
# # NOTE: The CurveFit package uses scipy's optimization functions, which in turn use numpy's linear algebra functions.
# # This presents significant issues on Windows, since the Windows OS lacks certain base dependencies for handling
# # linear algebra (more details can be found here: https://stackoverflow.com/a/51091218). One solution is to install the
# # Windows-binary versions of numpy and pandas (here: https://www.lfd.uci.edu/~gohlke/pythonlibs/, also use pipwin), but
# # it's easier to just use a Linux/Unix machine (Mac).
#
#
# def fit_model_predict(model_args_dict, verbose=False, charts=False):
#     # Parse model arguments from model_args_dict
#     if verbose:
#         print("Getting model arguments/params from model_args_dict...")
#     obs_df = model_args_dict['df']
#     col_t = model_args_dict['col_t']
#     col_obs = model_args_dict['col_obs']
#     col_group = model_args_dict['col_group']
#     col_covs = model_args_dict['col_covs']
#     param_names = model_args_dict['param_names']
#     link_fun = model_args_dict['link_fun']
#     var_link_fun = model_args_dict['var_link_fun']
#     fun = ln_gaussian_cdf  # TODO -- set this as default? How to change from full_run.py?
#     fe_init = model_args_dict['fe_init']
#     fe_gprior = model_args_dict['fe_gprior']
#     fe_bounds = model_args_dict['fe_bounds']
#     num_time_predict = model_args_dict['num_time_predict']
#
#     # Set up the CurveModel
#     if verbose:
#         print("Instantiating the model...")
#     model = CurveModel(
#         df=obs_df,
#         col_t=col_t,
#         col_obs=col_obs,
#         col_group=col_group,
#         col_covs=col_covs,
#         param_names=param_names,
#         link_fun=link_fun,
#         var_link_fun=var_link_fun,
#         fun=fun
#     )
#
#     # Fit the model to estimate parameters
#     if verbose:
#         print("Fitting the model...")
#     if len(obs_df[col_group].unique().tolist()) == 1:  # Can't pass `smart_initialization=True` with only 1 group of data
#         model.fit_params(fe_init=fe_init,
#                          fe_gprior=fe_gprior)
#     else:
#         model.fit_params(fe_init=fe_init,
#                          fe_gprior=fe_gprior,
#                          smart_initialize=True)
#
#     # Get predictions
#     if verbose:
#         print("Getting model predictions...")
#     pred_df = pd.DataFrame()
#     pred_df['time_pred'] = np.arange(obs_df[col_t].max()+1, obs_df[col_t].max()+num_time_predict+1)
#     y_predictions = model.predict(
#         t=pred_df['time_pred'],
#         group_name=obs_df[col_group].unique()
#     )
#
#     y_pred_df = pd.DataFrame(data=y_predictions, columns=['prediction_ln_death_rate'])
#     pred_df_full = pd.concat([pred_df, y_pred_df], axis=1, sort=False)
#     # print(pred_df_full)
#
#     # TODO:
#     # if charts:
#     #     if verbose:
#     #         print("Plotting the fitted model...")
#     #     # Plot results
#     #     plt.plot(y_pred_df[col_t], y_pred_df, '-')
#     #     plt.plot(y_pred_df[col_t], obs_df[col_obs], '.')
#     #     plt.show()
#
#     return model, pred_df_full
