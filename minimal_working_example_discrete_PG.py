
"""
A Discrete Control Implementation for TensorFlow 2.0
Author: W.J.A. van Heeswijk
Date: 11-8-2020
This code is supplemental to the following note:
'Implementing  Actor Networks for  Discrete Control in TensorFlow 2.0'
https://www.researchgate.net/publication/344102641_Implementing_Actor_Networks_for_Discrete_Control_in_TensorFlow_20
Corresponding blog post:
https://towardsdatascience.com/a-minimal-working-example-for-discrete-policy-gradients-in-tensorflow-2-0-d6a0d6b1a6d7
Python 3.8 and TensorFlow 2.3 were used to write the algorithm
This code has been published under the GNU GPLv3 license
"""


# Needed for training the network
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.layers as layers
import tensorflow.keras.initializers as initializers

# Needed for animation
import matplotlib.pyplot as plt

def get_reward(bandit):
    """Generate reward for selected bandit"""
    reward = tf.random.normal \
        ([1], mean=bandit, stddev=1, dtype=tf.dtypes.float32)

    return reward

def plot():
    """Plot bar chart with selection probability per bandit"""
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        bandits = ['1', '2', '3', '4']
        probabilities = [action_probabilities[0,0],\
                    action_probabilities[0,1],\
                    action_probabilities[0,2],\
                    action_probabilities[0,3]]
        ax.bar(bandits,probabilities)

        # Add labels and legend
        plt.xlabel('Episode')
        plt.ylabel('Probability action')
        plt.legend(loc='best')
        
        plt.show()


def construct_actor_network(bandits):
    """Construct the actor network with mu and sigma as output"""
    inputs = layers.Input(shape=(1,)) #input dimension
    hidden1 = layers.Dense(5, activation="relu",kernel_initializer=initializers.he_normal())(inputs)
    hidden2 = layers.Dense(5, activation="relu",kernel_initializer=initializers.he_normal())(hidden1)
    probabilities = layers.Dense(len(bandits), kernel_initializer=initializers.Ones(),activation="softmax")(hidden2)

    actor_network = keras.Model(inputs=inputs, outputs=[probabilities]) 
    
    return actor_network

def cross_entropy_loss(probability_action, state, reward):   
    """Comput cross entropy loss"""
    log_probability = tf.math.log(probability_action + 1e-5)
    loss_actor = - reward * log_probability
    
    return loss_actor


"""Main code: train actor network with discrete policy gradient method"""
# Fixed state
state = tf.constant([[1]],dtype=np.float32)
bandits = np.array([1.0,0.9,0.9,1.0])

# Construct actor network
actor_network = construct_actor_network(bandits)

# Define optimizer
opt = keras.optimizers.Adam(learning_rate=0.001)

for i in range(10000 + 1):    
    with tf.GradientTape() as tape:  
         # Obtain action probabilities from network
        action_probabilities = actor_network(state)
        
        # Select random action based on probabilities
        action = np.random.choice(len(bandits), p=np.squeeze(action_probabilities))
        
        # Obtain reward from bandit
        reward = get_reward(bandits[action])  

        # Store probability of selected action
        probability_action = action_probabilities[0, action]
        
        # Compute cross-entropy loss
        loss_value = cross_entropy_loss(probability_action, state, reward)

        # Compute gradients
        grads = tape.gradient(loss_value[0], actor_network.trainable_variables)
        
        #Apply gradients to update network weights
        opt.apply_gradients(zip(grads, actor_network.trainable_variables))
        
    # Animation
    if np.mod(i, 100) == 0:       
        print('\n======episode',i, '======')
        print('probability',float(probability_action))
        print('action',int(action))
        print('reward',float(reward))
        print('loss',float(loss_value))
        
        plot() 
