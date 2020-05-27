import os
import os.path as osp
import sys
import torch
import numpy as np
import scipy.sparse as sp
from torch.utils.data import DataLoader
from torch_geometric.utils import from_scipy_sparse_matrix
from torch_geometric.data import Data
from scipy import io
from torch_geometric.nn import GCNConv, DeepGraphInfomax
from tqdm import tqdm
import json
from torch import nn
import shutil
class Encoder(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super(Encoder, self).__init__()
        self.conv = GCNConv(in_channels, hidden_channels, cached=True)
        self.prelu = nn.PReLU(hidden_channels)

    def forward(self, x, edge_index):
        x = self.conv(x, edge_index)
        x = self.prelu(x)
        return x
def corruption(x, edge_index):
    return x[torch.randperm(x.size(0))], edge_index

def infomax(fp, PARAMS):
    g = io.loadmat(osp.join(fp, 'interim', 'graph', PARAMS['GRAPH_NAME']))
    N = g['N']
    p_cate = g['post_cate']
    post_indx = g['post_indx']
    edge_idx, x =from_scipy_sparse_matrix(N)
    x = x.view(-1, 1).float()
    feature = np.zeros((x.shape[0], p_cate.shape[1]))
    feature[post_indx, :] = p_cate
    x = torch.cat([x, torch.FloatTensor(feature)], 1)
    data = Data(
                x = x,
                edge_index = edge_idx
            )
    if PARAMS['CUDA']:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = 'cpu'
    shutil.rmtree(osp.join(fp, 'processed', 'infomax'), ignore_errors = True)
    data = data.to(device)
    model = DeepGraphInfomax(
        hidden_channels=PARAMS['HIDDEN_CHANNELS'], encoder=Encoder(data.x.shape[1], PARAMS['SUMMARY']),
        summary=lambda z, *args, **kwargs: torch.sigmoid(z.mean(dim=0)),
        corruption=corruption).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=PARAMS['LEARNING_RATE'])
    def train():
        model.train()
        optimizer.zero_grad()
        pos_z, neg_z, summary = model(data.x, data.edge_index)
        loss = model.loss(pos_z, neg_z, summary)
        loss.backward()
        optimizer.step()
        return loss.item()
    losses = []
    for epoch in range(1, PARAMS['NUM_EPOCH']+ 1) :
        loss = train()
        losses.append(loss)
        print('Epoch: {:03d}, Loss: {:.4f}'.format(epoch, loss))
    model.eval()
    with torch.no_grad():
        z, _, _ =model(data.x, data.edge_index)
    if not os.path.exists(os.path.join(fp, 'processed', 'infomax')):
        os.mkdir(os.path.join(fp, 'processed', 'infomax'))
    with open(osp.join(fp, 'processed', 'infomax', PARAMS['EMBEDDING_NAME'] + 'log.json'), 'w') as f:
        json.dump({'loss': losses}, f)
    z = z.detach().cpu().numpy()[post_indx.reshape(-1,), :]
    np.save(osp.join(fp, 'processed', 'infomax', PARAMS['EMBEDDING_NAME']), z)
    return 'embedding infomax created'