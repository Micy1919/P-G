# -*- coding:utf-8 -*-
"""
模型训练
"""
import argparse
import random
import time
import sys
import numpy as np
import tensorflow as tf
from tqdm import tqdm
from datautil import TrainingData

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, help="input model file", default=None)
parser.add_argument('--dir', type=str, help="input model file", default=None)
args = parser.parse_args()
if args.model is None:
    raise ValueError
model_path = args.model
path = args.dir
# load training data for now
start = time.time()
print 'Start to loading test data '
test_data = TrainingData()
test_data.load_data(path + '/query.test', path + '/docvec.test')


end = time.time()
print("Loading data from HDD to memory: %.2fs" % (end - start))

# ---------------------config--------------------
TRIGRAM_D = 8710
NEG = 50
BS = 512

L1_N = 256
L2_N = 128
batch_num = test_data.size()/BS
querynum = 10
# ---------------------config--------------------


checkpoint_file = tf.train.latest_checkpoint(model_path)
graph = tf.Graph()
with graph.as_default():
    sess = tf.Session()
    with sess.as_default():
        #sess.run(tf.initialize_all_variables())
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)
        doc_batch_shape = graph.get_operation_by_name("input/DocBatch/shape").outputs[0]
        doc_batch_values = graph.get_operation_by_name("input/DocBatch/values").outputs[0]
        doc_batch_indices = graph.get_operation_by_name("input/DocBatch/indices").outputs[0]

        query_batch_shape = graph.get_operation_by_name("input/QueryBatch/shape").outputs[0]
        query_batch_values = graph.get_operation_by_name("input/QueryBatch/values").outputs[0]
        query_batch_indices = graph.get_operation_by_name("input/QueryBatch/indices").outputs[0]

        acc = graph.get_operation_by_name("Accuracy/Mean").outputs[0]
        query_in = test_data.get_query_batch(BS * querynum, 1, TRIGRAM_D)
        doc_in = test_data.get_doc_batch(BS, 1, TRIGRAM_D)

        predict_rest = sess.run([acc], feed_dict={
            doc_batch_shape: doc_in.dense_shape,
            doc_batch_values: doc_in.values,
            doc_batch_indices: doc_in.indices,

            query_batch_shape: query_in.dense_shape,
            query_batch_values: query_in.values,
            query_batch_indices: query_in.indices
        })

        print predict_rest
