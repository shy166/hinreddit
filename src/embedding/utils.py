import os
import os.path as osp
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import torch
from torch_geometric.data import Data as dt
from torch_geometric.data import InMemoryDataset
from torch_geometric.utils import from_scipy_sparse_matrix
from scipy import io
import shutil
class RedditData(InMemoryDataset):
    def __init__(self, root, transform=None, pre_transform=None):
        super(RedditData, self).__init__(root, transform, pre_transform)
        self.root = root
        self.data, self.slices = torch.load(self.processed_paths[0])

    @property
    def raw_file_names(self):
        return ['graph.mat']

    @property
    def processed_file_names(self):
        return ['graph.pt']

    def download(self):
        # Download to `self.raw_dir`.
        pass
    def process(self):
        # Read data into huge `Data` list.
        data_list = []
        if self.pre_filter is not None:
            data_list = [data for data in data_list if self.pre_filter(data)]

        if self.pre_transform is not None:
            data_list = [self.pre_transform(data) for data in data_list]
        g = io.loadmat(osp.join(self.root, 'interim', 'graph', 'graph.mat'))
        N = g['N']
        edge_idx, x =from_scipy_sparse_matrix(N)
        data_list.append(
            dt(
                x = x,
                edge_index = edge_idx
            )
        )
        data, slices = self.collate(data_list)
        torch.save((data, slices), self.processed_paths[0])

def create_dataset(fp):
    shutil.rmtree(osp.join(fp, 'interim', 'graph', 'processed'), ignore_errors = True)
    shutil.rmtree(osp.join(fp, 'interim', 'graph', 'raw'), ignore_errors = True)
    data = RedditData(root = os.path.join(fp, 'interim', 'graph'))
    return data
