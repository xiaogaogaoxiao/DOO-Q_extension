# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 12:54:09 2016
 MAQL implementation with optimizations of memory usage
@author: Felipe Leno
"""

import random
import math

from .agent import Agent
from common_features import Agent_Utilities

import copy
import actions

class MAQL(Agent):

    alpha = None
    gamma = None
    T = None
    qTable = None
    functions = None
    lastAction = None
    
    friends = None
    

    def __init__(self, seed=12345,numAg = 3,alpha = 0.1,gamma=0.9,T=0.4):
        self.sortFriends = True
        self.alpha = alpha
        self.gamma = gamma
        self.T = T
        self.functions = Agent_Utilities()
        self.qTable = {}
        self.friends = None
        self.lastAction = None
        super(MAQL, self).__init__(seed=seed,numAg = numAg)
        
        
    def initiate_agent_refs(self,numAg,seed):
        """ Create the references to be executed by experiment.py """
        agents = []
        for i in range(numAg):        
            agents.append(copy.deepcopy(self))
        #Prepares the other agents' references
        for i in range(numAg):
            agents[i].friends = agents

        
        
        return agents

        
        
    def get_proc_state(self,agentIndex):
        """ Returns a processed version of the current state """
        return self.environment.get_state(agentIndex,self.sortFriends)
            
        

            
    
    def select_action(self, state,agentIndex):
        """ When this method is called, the agent executes an action. """
        #Computes the best action for each agent        
        if self.exploring:
               action =  self.exp_strategy(state)
           #Else the best action is picked
        else:
            action = self.max_Q_action(state)
        self.lastAction = action
        return action
        
        
        
    def max_Q_action(self,state):
        """Returns the action that corresponds to the highest Q-value"""
        actions = self.getPossibleActions()
        v,a =  self.functions.get_max_Q_value_action(self.qTable,state,actions,self.exploring)
        return a[self.agentIndex]
    def get_max_Q_value(self,state):
        """Returns the maximum Q value for a state"""
        actions = self.getPossibleActions()
        v,a =  self.functions.get_max_Q_value_action(self.qTable,state,actions,self.exploring)
        return v
        
        
        
    def exp_strategy(self,state):
        """Returns the result of the exploration strategy"""
        useBoltz = False        
        allActions = self.getPossibleActions()
        if useBoltz:
            #Boltzmann exploration strategy
            valueActions = []
            sumActions = 0
            
            for action in allActions:
                qValue = self.qTable.get((state,action),0.0)
                vBoltz = math.pow(math.e,qValue/self.T)
                valueActions.append(vBoltz)
                sumActions += vBoltz
            
            probAct = []
            for index in range(len(allActions)):
                probAct.append(valueActions[index] / sumActions)
            
            rndVal = random.random()
            
            sumProbs = 0
            i=-1
            
            while sumProbs <= rndVal:
                i = i+1
                sumProbs += probAct[i]
            
            return allActions[i][self.agentIndex]
        else:
            prob = random.random()
            if prob <= 0.1:
                return random.choice(allActions)[self.agentIndex]
            return self.max_Q_action(state)
           

    
    def get_Q_size(self,agentIndex):
        """Returns the size of the QTable"""
        return len(self.qTable)
        
    
    def observe_reward(self,state,action,statePrime,reward,agentIndex):
        """Performs the standard Q-Learning Update"""
        if self.exploring:
            act = []
            for friend in self.friends:
                act.append(friend.lastAction)
            act = tuple(act)
            qValue= self.qTable.get((state,act),None)
            V = self.get_max_Q_value(statePrime)        
            if qValue is None:
                newQ = reward
            else:
                newQ = qValue + (self.alpha) * (reward + self.gamma * V - qValue)         
            self.qTable[(state,act)] = newQ
        self.lastAction = None
        
    
    def getPossibleActions(self):
        """Returns the possible actions"""
        #Cartesian product of all for all agents
        allActions = []  
        for ag in range(0,self.numAg):
            allActions.append(tuple(actions.all_agent_actions()))
        #Returns all possible combined actions
        listAct = self.cartesian(allActions).tolist()
        ret = []
        for ele in listAct:
            ret.append(tuple(ele))
        return ret

    def cartesian(self,arrays, out=None):
        """
        Generate a cartesian product of input arrays.
        http://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
        """
        import numpy as np
        arrays = [np.asarray(x) for x in arrays]
        dtype = arrays[0].dtype
    
        n = np.prod([x.size for x in arrays])
        if out is None:
            out = np.zeros([n, len(arrays)], dtype=dtype)
    
        m = n / arrays[0].size
        out[:,0] = np.repeat(arrays[0], m)
        if arrays[1:]:
            self.cartesian(arrays[1:], out=out[0:m,1:])
            for j in xrange(1, arrays[0].size):
                out[j*m:(j+1)*m,1:] = out[0:m,1:]
        return out
