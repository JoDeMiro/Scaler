


import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import os
import pickle
import joblib

import warnings 
warnings.filterwarnings("ignore")
tf.get_logger().setLevel('INFO')

from datetime import datetime, date, time

from tensorflow import keras
from tensorflow.keras import layers

from sklearn.linear_model import LinearRegression

print(tf.__version__)

import time
ost = time.time()

ost = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print(ost)

ost = time.strftime("%H:%M:%S", time.gmtime())
print(ost)

# --------------------------------------------

# sets seeds for base-python, numpy and tf
tf.keras.utils.set_random_seed(42)
tf.config.experimental.enable_op_determinism()

#
metric_file_name = './Train/metric_train_by_none.log'
df = pd.read_csv(metric_file_name, sep=',', header=0)

train_log_file_name  = './Train/scaled_train_by_none.log'
cf = pd.read_csv(train_log_file_name, sep=',', header=0)

cf['otime'] = cf['time']
cf['time'] = cf['otime'].str[:-1]

mf = df.merge(cf, on='time', how='left')
mf['delta_vm'] = mf['actual_vm_number_is'] - mf['actual_vm_number_was']

assert mf['worker_number'].isnull().values.any() == False



def create_term_for_metric(columnname: str):
    
    f1 = mf.copy()
    __next_name = columnname + 'Next'
    __prev_name = columnname + 'Prev'

    f1[__next_name] = f1[columnname].shift(-1)
    f1[__prev_name] = f1[columnname].shift(+1)
    
    f1 = f1.dropna()
    
    __metric_term1 = columnname + '_term1'
    __metric_term2 = columnname + '_term2'
    f1[__metric_term1] = f1[columnname] * f1['worker_number']/(f1['worker_number'] + f1['delta_vm'])
    f1[__metric_term2] = f1[columnname] * f1['delta_vm']/(f1['worker_number'] + f1['delta_vm'])
    
    __metric_term = f1[[__metric_term1, __metric_term2]]
    __metric_next = f1[__next_name]
    
    return __metric_term, __metric_next

def create_term_for_prediction(value: float, w: int, k: int):
    
    __metric_term1 = value * w/(w+k)
    __metric_term2 = value * k/(w+k)
    
    __metric_term = np.array([[__metric_term1, __metric_term2]])
    
    return __metric_term

def calc_pred_for_metric(__metric_term, __metric_next):

    lr = LinearRegression(fit_intercept=True)

    rr = lr.fit(__metric_term, __metric_next)

    __fit_score = rr.score(__metric_term, __metric_next)
    __fit_coef_ = rr.coef_
    __fit_intercept_ = rr.intercept_
    
    __pred_metric = rr.predict(__metric_term)
    
    return rr
    
    


# Set input variables
input_variables = ['request_rate', 'CPU0User%', '[DSK:sda]Reads', '[NUMA:0]Anon', '[NUMA:0]AnonH']

train_features = mf[input_variables]
train_labels = mf[['response_time_p95']]
# train_labels = mf[['response_time']]







# Neural Net part
normalizer = tf.keras.layers.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))

first_model = tf.keras.Sequential([
    normalizer,
    tf.keras.layers.Dense(5, activation='tanh'),
    tf.keras.layers.Dense(3, activation='ReLU'),
    layers.Dense(units=1)
])

# first_model.summary()

first_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.1),
    loss='mean_absolute_error')

predicted_labels = first_model.predict(train_features)

# Tulikép csak ez kell
first_model = keras.models.load_model('./Models/nn')
# first_model = keras.models.load_model(os.getcwd() + '/Models/nn')







# Linreg -> Action part
A = [i for i in range(-7, 8, 1)]

print(A)

# -2. inicalizálni egy üres dictianary-t a dict(action, predicted_response_time) pároknak
r = []; al = []; rl = []

# -1. kiválasztani, hogy milyen értéket mérek aktuális metrikákként
# ideiglenesen az mf utolsó értékei lesznek a bemenők
__N = -30

__current_response_time = mf['response_time_p95'].values[__N]
__last_metrics = mf[input_variables].values[__N]
__w = __last_metrics[-1]

print('-----------------------------------------')
print('__last_metrics -> vagyis a current values')
print(__last_metrics)
print('__current_rt ->')
print(__current_response_time)
print('-----------------------------------------')

for a in A:
    
    # Ez kell, hogy a VM szám (w) ne legyen 0
    # if __w + a != 0:
    
        # 0.
        # inicializálni egy üres tömböt az input_variable változónak
        _new_train_features = np.zeros((1, mf[input_variables].shape[1]))
        
        # 0.
        # az új tömb utolsó értéke (worker_number) legyen beállítva az aktuális worker_number értékével
        _new_train_features[0, -1] = __w
        # helyett
        _new_train_features[0, -1] = __w + a
        

        # 1.
        # minden metrikára kiszámolni
        for i, metric in enumerate(input_variables):            # A worker_number az kivétle azt majd kiszámolom
            # print(i, metric)
            if metric != 'worker_number':

                # 2.
                # megcsinálni a linreg modelt az adott metrikára (tanítás)
                __metric_term, __metric_next = create_term_for_metric(metric)
                __lr_model = calc_pred_for_metric(__metric_term, __metric_next)
                
                # 3.
                # elmenetni az adott modelt
                _ = joblib.dump(__lr_model, './Models/lr/lr_' + metric + '.joblib', compress=9)

                # 3.
                # az előbbi model alapján egy becslés egy konkrét értékre (value, w, k)
                __metric_term = create_term_for_prediction(__last_metrics[i], __w, a)
                # print('---a metrica értékének becsése (value, w, k alapján ---')
                # print(__metric_term)
                # print(metric)
                # print(a)
                # print('------------------')
                __pred_metric = __lr_model.predict(__metric_term)
                
                # 4.
                # adott becsült metrikát bele kell helyezni a neurális háló bemeneti változójához
                _new_train_features[0, i] = __pred_metric
                # print(_new_train_features)

        # 5.
        # megvan az új a-hoz tartozó metika tömb, ez alapján becsüjük meg a válaszidőt
        print(_new_train_features)
        
        # 6. NN -> RT
        
        __predicted_response_time = first_model.predict(_new_train_features, verbose = 0)
        
        print(__predicted_response_time)
        
        print(a)


