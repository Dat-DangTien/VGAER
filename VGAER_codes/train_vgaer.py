from __future__ import division
from __future__ import print_function

import argparse
import time
import networkx as nx
import numpy as np
import scipy.sparse as sp
import torch
from matplotlib import pyplot as plt
from torch import optim
import pandas as pd
import dgl
from dgl.data import CoraGraphDataset, CiteseerGraphDataset , PubmedGraphDataset
import csv
# import scanpy

import model
from model import VGAERModel
import torch.nn.functional as F
from cluster import community
from NMI import load_label, NMI, label_change
from Qvalue import Q
from sklearn import manifold
from sklearn import metrics
#from tsne import get_data,tsne_show
#from Qwepoch import Q_with_epoch
from sklearn.manifold import TSNE

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='gcn_vae', help="models used")
parser.add_argument('--seed', type=int, default=42, help='Random seed.')
parser.add_argument('--epochs', type=int, default=10000, help='Number of epochs to train.')
parser.add_argument('--hidden1', type=int, default=8, help='Number of units in hidden layer 1.')
parser.add_argument('--hidden2', type=int, default=2, help='Number of units in hidden layer 2.')
parser.add_argument('--lr', type=float, default=0.05, help='Initial learning rate.')
parser.add_argument('--dropout', type=float, default=0., help='Dropout rate (1 - keep probability).')
parser.add_argument('--dataset', type=str, default='cora', help='type of dataset.')
parser.add_argument('--cluster', type=str, default=7, help='Number of community')
args = parser.parse_args()

#Check device
use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")

def vgaer():
    # Load form DGL dataset
    if args.dataset == 'cora':
        dataset = CoraGraphDataset(reverse_edge=False)
    elif args.dataset == 'citeseer':
        dataset = CiteseerGraphDataset(reverse_edge=False)
    elif args.dataset == 'pubmed':
        dataset = PubmedGraphDataset(reverse_edge=False)
    else:
        raise NotImplementedError
    graph = dataset[0]



    # data:power
    # G = nx.read_gml('data/netscience/netscience.gml', label='id')
    # A = torch.Tensor(nx.adjacency_matrix(G).todense())
    # A_orig = A.detach().numpy()
    # A_orig_ten = A
    # A_orig_ten = A_orig_ten.to(device)

    # columns = ['Source', 'Target']
    # data = pd.read_csv('data/lastfm_asia/lastfm_asia_edges.csv', names=columns, header=None)
    # G = nx.Graph()
    # data_len = len(data)
    # for i in range(data_len):
    #     G.add_edge(data.iloc[i]['Source'], data.iloc[i]['Target'])

    # A = torch.Tensor(nx.adjacency_matrix(G).todense())
    # A_orig = A.detach().numpy()
    # A_orig_ten = A.to(device)


    A = graph.adjacency_matrix().to_dense()
    A_orig = A.detach().numpy()
    A_orig_ten = A.to(device)
    label_orig = graph.ndata['label'].detach().numpy()

    #compute B matrix
    K = 1 / (A.sum().item()) * (A.sum(dim=1).reshape(A.shape[0], 1) @ A.sum(dim=1).reshape(1, A.shape[0]))
    B = A - K
    B = B.to(device)


    #compute A_hat matrix
    A = A + torch.eye(A.shape[0])
    D = torch.diag(torch.pow(A.sum(dim=1), -0.5))  # D = D^-1/2
    A_hat = D @ A @ D
    A_hat = A_hat.to(device)
    A = A.to(device)

    # graph=graph.to(device)


    #Extract node features
    #features = graph.ndata['feat']
    # feature_dim = A.shape[0]
    # features = torch.eye(feature_dim, feature_dim)
    #features = features.to(device)
    #feats = torch.cat((features,B),1)
    # in_dim = feats.shape[-1]
    feats = B
    # feats = features
    in_dim = feats.shape[-1]



    #create model
    vgaer_model = model.VGAERModel(in_dim,args.hidden1,args.hidden2,device)
    vgaer_model = vgaer_model.to(device)


    #create training component
    optimizer = torch.optim.Adam(vgaer_model.parameters(),lr=args.lr)
    print('Total Parameters:', sum([p.nelement() for p in vgaer_model.parameters()]))

    def compute_loss_para(adj):
        pos_weight = ((adj.shape[0] * adj.shape[0] - adj.sum()) / adj.sum())
        norm = adj.shape[0] * adj.shape[0] / float((adj.shape[0] * adj.shape[0] - adj.sum()) * 2)
        weight_mask = adj.view(-1) == 1
        weight_tensor = torch.ones(weight_mask.size(0)).to(device)
        weight_tensor[weight_mask] = pos_weight
        return weight_tensor,norm

    weight_tensor, norm = compute_loss_para(A)

        #create traing epoch
    for epoch in range(args.epochs):
        #x_num = []
        #y_num = []
        vgaer_model.train()
        recovered = vgaer_model.forward(A_hat,feats)
        logits = recovered[0]
        hidemb = recovered[1]
        loss = norm*F.binary_cross_entropy(logits.view(-1),A_orig_ten.view(-1),weight=weight_tensor)
        kl_divergence = 0.5 / logits.size(0) * (
                1 + 2 * vgaer_model.log_std - vgaer_model.mean ** 2 - torch.exp(vgaer_model.log_std) ** 2).sum(
            1).mean()
        loss -= kl_divergence
        print("Epoch:", '%04d' % (epoch + 1), "train_loss=", "{:.5f}".format(loss.item()))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if epoch == args.epochs-1:
            hidemb = hidemb.cpu()
            #torch.save(hidemb, './z.pt')
            # NMI_count=[]
            #commu_pred = community(hidemb, args.cluster)
            # label_orig = load_label(args.dataset)[0]
            #for i in range(18,args.cluster):
            #for i in range(5):
            commu_pred = community(hidemb, args.cluster)
            #print(i)
            #hidemb = hidemb.detach().numpy()
            #hidemb = hidemb.tolist()
            #showPicture(hidemb, commu_pred)
            #lable_truepred = label_change(commu_pred, label_orig)
            # feats = feats.cpu()
            # plt.scatter(feats[:, 0], feats[:, 1], c=commu_pred)
            # plt.show()
            #feats = feats.cpu()
            Q(A_orig, np.eye(args.cluster)[commu_pred])
            print(Q_NUMBER)
            nmi = NMI(commu_pred, label_orig)
            #x_num.append(epoch)
            #y_num.append(nmi * 100)
            # ts = manifold.TSNE(n_components=2, perplexity=35, early_exaggeration=500, n_iter=2000, learning_rate=500,
            #                    angle=0.5, init='random')
            # # ts = manifold.TSNE(n_components=2)
            # hidemb = hidemb.detach().numpy()
            # z = ts.fit_transform(hidemb)
            # # C_model = KMeans(n_clusters=clusters, verbose=0, max_iter=1000, tol=0.001, n_init=20, init='k-means++')
            # plt.figure(figsize=(8, 8), dpi=120)
            # plt.scatter(z[:, 0], z[:, 1], c=commu_pred, marker='o', s=5)  # 不同类别不同颜色
            # plt.title("k-means")
            # plt.show()
    # np.save('./{}_epoch_x.npy'.format(args.dataset), x_num)
    # np.save('./{}_epoch_y.npy'.format(args.dataset), y_num)
if __name__ == '__main__':
    vgaer()

















