from ast import literal_eval

import tensorflow as tf
import pandas as pd
import numpy as np


def prepare_data_from_csv(data_file):
    training_output = data_file['sentiment']
    training_input = data_file['review'].map(literal_eval).tolist()

    max_length = get_max_length(training_input)
    training_input = map(lambda l: np.append(l, np.repeat(-1, max_length - len(l))).tolist(),
                         training_input)

    return training_input, training_output


def get_max_length(collection):
    """
    Returns length of the longest collection item in given collection.
    If collection is empty returns 0.
    """
    try:
        max_length = max(map(len, collection))
        return max_length
    except:
        raise ValueError('Empty collection has no collection items.')


def main():
    num_neurons = 24
    batch_size = 50

    data_file = pd.read_csv('output.csv')
    training_input, training_output = prepare_data_from_csv(data_file)
    max_length = get_max_length(training_input)
    training_input = np.reshape(training_input, (len(training_input), max_length, 1))
    training_output = np.reshape(training_output, (len(training_output), 1))

    x = tf.placeholder(tf.float32, shape=[None, max_length, 1])
    y = tf.placeholder(tf.float32, shape=[None, 1])

    cell = tf.nn.rnn_cell.LSTMCell(num_neurons, state_is_tuple=True)
    output, state = tf.nn.dynamic_rnn(cell, x, dtype=tf.float32)
    output = tf.transpose(output, [1, 0, 2])
    last = tf.gather(output, int(output.get_shape()[0]) - 1)
    weight = tf.Variable(tf.truncated_normal([num_neurons, int(y.get_shape()[1])]))
    bias = tf.Variable(tf.constant(0.1, shape=[y.get_shape()[1]]))
    prediction = tf.nn.softmax(tf.matmul(last, weight) + bias)
    cross_entropy = -tf.reduce_sum(y * tf.log(prediction))
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    mistakes = tf.not_equal(tf.argmax(y, 1), tf.argmax(prediction, 1))
    error = tf.reduce_mean(tf.cast(mistakes, tf.float32))

    init_op = tf.initialize_all_variables()
    with tf.Session() as sess:
        sess.run(init_op)
        counter = 0
        for i in range(len(training_input)/batch_size):
            inp = training_input[counter:(counter + batch_size)]
            out = training_output[counter:(counter + batch_size)]
            counter += batch_size
            sess.run(train_step, feed_dict={x: inp, y: out})
        train_accuracy = error.eval(feed_dict={x: inp, y: out})
        print("training accuracy %g" % train_accuracy)
        print(sess.run(prediction, {x:np.reshape(training_input[1], (1, 291, 1))}))

if __name__ == '__main__':
    main()
