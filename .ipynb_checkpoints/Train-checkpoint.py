from Model import test_model
import torch.optim as optim
from Survival_CostFunc_CIndex import *
import torch
import numpy as np
from tqdm import tqdm
import copy

def train(X_train, t_train, e_train, X_val, t_val, e_val, X_test, t_test, e_test,
         learning_rate, epochs) :
    
    net = test_model(len(X_train[0]))
    if torch.cuda.is_available():
        net.cuda()
    opt = optim.Adam(net.parameters(), lr = learning_rate, weight_decay = 0.2)
    train_cost = []
    val_cost = []
    best_val_cost = np.inf
    
    for epoch in tqdm(range(epochs)) :
        net.train()
        train_pred = net(X_train)
        train_loss = neg_par_log_likelihood(train_pred, t_train, e_train)
        train_cost.append(train_loss)
        train_loss.backward()
        opt.zero_grad()
        opt.step()
            
        if (epochs % 20 == 0) :
            net.eval()
            val_pred = net(X_val)
            val_loss = neg_par_log_likelihood(val_pred, t_val, e_val)
            val_cost.append(val_loss)
        
            if (best_val_cost > val_loss) :
                best_val_cost = val_loss
                best_model = copy.deepcopy(net)  
                torch.save(net.state_dict(), './models/' + str(epoch))
        # print('train_loss = ', train_loss, 'val_loss = ', val_loss)
    
    best_model.eval()
    test_pred = best_model(X_test)
    test_cindex = c_index(test_pred, t_test, e_test)
    
    return train_cost, val_cost, test_cindex