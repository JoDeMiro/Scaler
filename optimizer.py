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

# --------------------------------------------


class Optimizer():
    
    def __init__(self, model_path):
        self.model_path = model_path
        pass
    
    def load_data(self):
        
        metric_file_name = './Train/metric_train_by_none.log'
        df = pd.read_csv(metric_file_name, sep=',', header=0)
        
        print('_________________________ DF _________________________')
        
        print(df.tail())

        
        # new
        mf = df.copy()

        mf['actual_vm_number_is'] = mf['worker_number']
        mf['actual_vm_number_was'] = mf['worker_number'].shift(1)
        mf['actual_vm_number_will'] = mf['worker_number'].shift(-1)

        mf['delta_vm'] = mf['actual_vm_number_will'] - mf['actual_vm_number_is']
        
        self.mf = mf
        
        print('_________________________ MF _________________________')

        print(mf.tail())


        
    def set_input_variables(self):

        # Set input variables
        input_variables = ['request_rate',
                           'CPU0User%',
                           '[DSK:sda]Reads',
                           '[NUMA:0]Anon',
                           '[NUMA:0]AnonH']
        
        input_variables = ['request_rate',
                           'CPU0User%',
                           'CPU1Total%',
                           '[DSK:sda]Reads',
                           '[NUMA:0]Anon',
                           '[NUMA:0]AnonH']

        self.train_features = self.mf[input_variables]
        # self.train_labels = self.mf[['response_time_p95']]
        self.train_labels = self.mf[['response_time']]
        
        self.input_variables = input_variables



    def load_neural_net(self):

        # Neural Net part
        normalizer = tf.keras.layers.Normalization(axis=-1)
        normalizer.adapt(np.array(self.train_features))

        first_model = tf.keras.Sequential([
            normalizer,
            tf.keras.layers.Dense(5, activation='ReLU'),
            tf.keras.layers.Dense(3, activation='ReLU'),
            layers.Dense(units=1)
        ])
        
        # first_model.summary()

        first_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.1),
            loss='mean_absolute_error', run_eagerly=True)

        # Tulikép csak ez kell
        # first_model = keras.models.load_model('./Models/nn')
        first_model = keras.models.load_model(self.model_path)
        

        # predicted_labels = first_model.predict(self.train_features)
        
        self.first_model = first_model



    def calculate_rt(self, n = None, min_a = None, max_a = None):
        
        input_variables = self.input_variables

        # -1. kiválasztani, hogy milyen értéket mérek aktuális metrikákként
        # ideiglenesen az mf utolsó értékei lesznek a bemenők
        
        __N   = -30 if n is None else n
        min_a = -7 if min_a is None else min_a
        max_a = +8 if max_a is None else max_a
        
        print('n =', __N, 'min_a =', min_a, 'max_a =', max_a)
        
        # Linreg -> Action part
        A = [i for i in range(min_a, max_a, 1)]
        
        # Create embty retun list
        results = []

        print(A)

        # -2. inicalizálni egy üres dictianary-t a dict(action, predicted_response_time) pároknak
        r = []; al = []; rl = []
        
        __current_response_time = self.mf['response_time_p95'].values[__N]
        __last_metrics = self.mf[input_variables].values[__N]
        __w = self.mf['worker_number'].values[__N]

        print('-----------------------------------------')
        print('__last_metrics -> vagyis a current values')
        print(__last_metrics)
        print('__current_rt ->')
        print(__current_response_time)
        print('__w -> worker_number')
        print(__w)
        print('-----------------------------------------')
        

        for a in A:

            # Ez kell, hogy a VM szám (w) ne legyen 0
            if __w + a != 0:

                # 0.
                # inicializálni egy üres tömböt az input_variable változónak
                _new_train_features = np.zeros((1, self.mf[input_variables].shape[1]))
                
                # 1.
                # minden metrikára kiszámolni
                for i, metric in enumerate(input_variables):
                    # print(i, metric)
                    if metric != 'worker_number':

                        # 2.
                        # megcsinálni a linreg modelt az adott metrikára (tanítás)
                        __metric_term, __metric_next = self.create_term_for_metric(metric)
                        __lr_model = self.calc_pred_for_metric(__metric_term.values, __metric_next.values)
                        
                        # 3.
                        # elmenetni az adott modelt
                        # _ = joblib.dump(__lr_model, './Models/lr/lr_' + metric + '.joblib', compress=9)

                        # 3.
                        # az előbbi model alapján egy becslés egy konkrét értékre (value, w, k)
                        __metric_term = self.create_term_for_prediction(__last_metrics[i], __w, a)
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

                # 6.
                # a neurális háló model segítségével megbecsülöm a válaszidőt

                __predicted_response_time = self.first_model.predict(_new_train_features, verbose = 0)
                
                print('action = ', a, ' --> rt --> ', __predicted_response_time, '\n')
                
                result = {'action': a, 'prt': __predicted_response_time.flatten()[0]}
                
                results.append(result)
        
        # dobjon vissza egy olyan listát amiben dictionary-t amiben {action: ., prt: .}
        
        return results


    def create_term_for_metric(self, columnname: str):

        f1 = self.mf.copy()
        __next_name = columnname + 'Next'
        __prev_name = columnname + 'Prev'

        f1[__next_name] = f1[columnname].shift(-1)
        f1[__prev_name] = f1[columnname].shift(+1)

        f1 = f1.dropna()

        # Az lenne a korrekt ha kidobnám azokat ahol nem volt skálázás (delta_vm == 0)

        indexAge = f1[ (f1['delta_vm'] == 0) ].index
        f1.drop(indexAge , inplace=True)

        __metric_term1 = columnname + '_term1'
        __metric_term2 = columnname + '_term2'
        f1[__metric_term1] = f1[columnname] * f1['worker_number']/(f1['worker_number'] + f1['delta_vm'])
        f1[__metric_term2] = f1[columnname] * f1['delta_vm']/(f1['worker_number'] + f1['delta_vm'])

        __metric_term = f1[[__metric_term1, __metric_term2]]
        __metric_next = f1[__next_name]

        return __metric_term, __metric_next

    
    # meg kéne csinálni, hogy ne kiszámolja, hanem olvassa be a modelt
    def calc_pred_for_metric_learned(self, __metric, __metric_term, __metrix_next):
        pass
    
    
    def calc_pred_for_metric(self, __metric_term, __metric_next):

        lr = LinearRegression(fit_intercept=True)

        rr = lr.fit(__metric_term, __metric_next)

        __fit_score = rr.score(__metric_term, __metric_next)
        __fit_coef_ = rr.coef_
        __fit_intercept_ = rr.intercept_

        __pred_metric = rr.predict(__metric_term)

        return rr

    
    def create_term_for_prediction(self, value: float, w: int, k: int):
    
        __metric_term1 = value * w/(w+k)
        __metric_term2 = value * k/(w+k)

        __metric_term = np.array([[__metric_term1, __metric_term2]])

        return __metric_term


