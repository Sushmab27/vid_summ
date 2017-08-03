# Basic libraries
import numpy as np
import tensorflow as tf
import os
import math
import random
import sys
import scipy.io as sio
tf.set_random_seed(2016)
np.random.seed(2016)

# LSTM-autoencoder
from LSTMAutoencoder import *

# Constants
batch_num = 1
hidden_num = 2048
step_num = 3
elem_num = 8192


# placeholder list
p_input = tf.placeholder(tf.float32, [batch_num, step_num, elem_num])
p_inputs = [tf.squeeze(t, [1]) for t in tf.split(1, step_num, p_input)]

cell = tf.nn.rnn_cell.LSTMCell(hidden_num, use_peepholes=True)
ae = LSTMAutoencoder(hidden_num, p_inputs, cell=cell, decode_without_input=True)

model_path = sys.path[0] + '/obj_cont_1_layer.ckpt'
saver = tf.train.Saver()

with tf.Session() as sess:
    saver.restore(sess, model_path)
    path = '/home/dingwen/meanMask/obj_cont/find_iter/first_layer/'
    path_ = path + 'feat_validation_mean.mat'
    path__ = sys.path[0] + '/feat_validation_2048.txt'


    if os.path.exists(path):
        clip_num = 200

	input_ = sio.loadmat(path_)
	input_ = input_['feat']
        input_ = input_[0:clip_num*step_num,:]
        input_ = np.reshape(input_,(-1,step_num,elem_num))

        train_cnt = clip_num/batch_num
        for train_iter in range(0,train_cnt):
            train_input = input_[train_iter:train_iter+batch_num]
            train_iter = train_iter+batch_num

            concate = False
            for out_tensor in ae.z_codes:
                loss, result = sess.run([ae.loss, out_tensor], {p_input:train_input})
                result = np.reshape(result,(batch_num,1,hidden_num))
                if concate == False:
                    res = result
                    concate = True
                    loss0 = loss
                else:
                    res = np.concatenate((res,result),axis=1)
                    loss0 = loss0+loss
            loss_final = loss0/step_num
            print loss_final
            res_ = np.reshape(res,(batch_num*step_num,-1))
            f = open(path__,'a')
            np.savetxt(f, res_)
