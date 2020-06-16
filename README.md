## Background
Many business and government entities use [Anaplan](https://www.anaplan.com/) for budgeting, planning, and other usecases. With the intense and far-reaching economic impacts of the COVID-19 pandemic, many businesses and municipalities want to know how the COVID-19 pandemic and associated economic crisis may affect their organization's financial outlook. This app allows such organizations to pull COVID-19 data and predictions directly into an Anaplan model, for analysis into the impact on their planning.

## Overview
At a high level, this app allows users to retrieve parameters and data from a specified Anaplan model, use those parameters and data to fit a COVID-19 epidemiological model, generate predictions from the COVID-19 model, and import the predictions back into the Anaplan model, for Anaplan users to then use in budgeting/forecasting/planning on the Anaplan platform.

### Assumptions
This app currently relies on the following assumptions:
- The user knows, or can obtain via an API service such as Postman, various ID strings associated with the Anaplan workspace, model, files, and processes.
- Historical data is available in an Anaplan model.
- Epidemiological model parameters are available in an Anaplan model.

## COVID-19 Epidemiological Model
This app uses [CurveFit](https://ihmeuw-msca.github.io/CurveFit/), a nonlinear mixed effects model-fitting package with applications in  epidemiology, and currently used by federal, state, and local governments and agencies, including the CDC. The CurveFit package is used to generate COVID-related predictions.

The package is developed and maintained by the [Institute for Health Metrics and Evaluation (IHME)](http://www.healthdata.org/), an independent global health research center at the University of Washington.
