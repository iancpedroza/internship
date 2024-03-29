# -*- coding: utf-8 -*-
"""MultivariateTimeSeries.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19t2_1D6fBnZ391fUNNGCzACyIik4Fgg_

# **READ ME:**

---

To run this, you will need to upload the "interview_dataset.csv" file onto your workspace. For my implementation, I used Google Colaboratory so that may be simplest.
Other than that, everything else should run on its own.

---

To summarize my work, I shifted through multiple algorithms, before settling on this one. At first, I tried working with an ANN trained to use prior values to predict future ones, however, this proved to be ineffective beyond a couple of points. I then experimented with univariate data models like ARIMA, but realized that a univariate model was not the correct model. Since the data contained multiple features affecting usage, I decided a multivariate time series model would be best. I ended up using a VAR (Vector Auto Regression) model, and was able to implement and fit it onto the data. I think the overall structure fits the problem well, and would work well for predicting into the future, as it is meant to excel at using each feature to help predict eachother. Unfortunately, in implementation, the model generalized greatly, as when graphed it largely rose to one value and stayed there. I predict that this is an error relating to stationarity, as this is something I've read is critical in confirming within time series. I don't have much experience with it, but there are plentiful resources online, and my first step would be to fix any stationarity issues to create better predictions.
"""

#import initial packages
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline

#read in data
df = pd.read_csv("interview_dataset.csv")
df.dtypes

#make the datetimes the index
df['datetime'] = pd.to_datetime(df.datetime)
data = df.drop(['datetime'], axis=1)
data.index = df.datetime

#new dataframe
data.head()

#drop reduntant time-based columns because the date-time object already covers it
newdata = data.drop(['DAY_OF_WEEK'], axis = 1)
newdata = newdata.drop(['HOUR_OF_DAY'], axis = 1)
newdata.head()

#remove null values
newdata.dropna(inplace=True)

#conduct test for stationarity - I didn't make any changes off this, and I feel that the dataset not being stationary may have been a cause of problems
from statsmodels.tsa.vector_ar.vecm import coint_johansen
johan_test_temp = newdata
coint_johansen(johan_test_temp,-1,1).eig

#create train and test sets - these have to be in order with time
train = newdata[:int(0.8*(len(newdata)))]
valid = newdata[int(0.8*(len(newdata))):]

#import the Vector Auto Regression model
from statsmodels.tsa.vector_ar.var_model import VAR

#Fit the model to the training data
model = VAR(endog=train)
model_fit = model.fit()

#make a forecasted prediction on the length of the validation set
prediction = model_fit.forecast(model_fit.y, steps=len(valid))

#the predicted values
prediction

#convert the array to a data frame
from sklearn.metrics import mean_squared_error
from math import sqrt
pred = pd.DataFrame(index=range(0,len(prediction)),columns=[newdata.columns])
for j in range(0,5):
    for i in range(0, len(prediction)):
       pred.iloc[i][j] = prediction[i][j]

#check root mean squared error for numerical accuracy checking
for i in newdata.columns:
    print('rmse value for', i, 'is : ', sqrt(mean_squared_error(pred[i], valid[i])))

#create copy of the validation set to use for the predictions
testgraph = valid.copy()
testgraph.head()

#make an array of only the predicted values for usage_kwh
filtered_prediction = []
for pred in prediction:
  filtered_prediction.append(pred[0])
filtered_prediction

#replace the testgraph's usage_kwh values with the predictions
testgraph['USAGE_KWH'] = filtered_prediction

#check the change is complete
testgraph.head()

#compare the validation set to the predictions
#The graph shows that the model generalized heavily, and work will need to be done to improve it.
#I believe it was an issue with stationarity, which I will have to work more with to improve upon
plt.plot(valid['USAGE_KWH'])
plt.plot(testgraph['USAGE_KWH'])

#fitting the model on the full dataset, and predicting 96 datapoints into the future
model = VAR(endog=newdata)
model_fit = model.fit()
yhat = model_fit.forecast(model_fit.y, steps=96)

#making the predictions into a dataframe
predyhat = pd.DataFrame(index=range(0,len(yhat)),columns=[newdata.columns])
for j in range(0,5):
    for i in range(0, len(yhat)):
       predyhat.iloc[i][j] = yhat[i][j]

#checking it is indeed a dataframe
predyhat.head()

#plotting the predictions to see the results
#Again, the model clearly generalized greatly, and changes will need to be made to improve stationarity, and take into account seasonality
plt.plot(predyhat['USAGE_KWH'])

