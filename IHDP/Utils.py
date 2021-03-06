"""
MIT License

Copyright (c) 2020 Shantanu Ghosh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import math

import numpy as np
import sklearn.model_selection as sklearn
import torch
import torch.nn.functional as F
from torch.distributions import Bernoulli
from collections import namedtuple
from itertools import product
import pandas as pd

class Utils:
    @staticmethod
    def convert_df_to_np_arr(data):
        return data.to_numpy()

    @staticmethod
    def test_train_split(covariates_X, treatment_Y, split_size=0.8):
        return sklearn.train_test_split(covariates_X, treatment_Y, train_size=split_size)

    @staticmethod
    def convert_to_tensor(X, Y):
        tensor_x = torch.stack([torch.Tensor(i) for i in X])
        tensor_y = torch.from_numpy(Y)
        processed_dataset = torch.utils.data.TensorDataset(tensor_x, tensor_y)
        return processed_dataset

    @staticmethod
    def convert_to_tensor_DCN(X, ps_score, Y_f, Y_cf):
        tensor_x = torch.stack([torch.Tensor(i) for i in X])
        tensor_ps_score = torch.from_numpy(ps_score)
        tensor_y_f = torch.from_numpy(Y_f)
        tensor_y_cf = torch.from_numpy(Y_cf)
        processed_dataset = torch.utils.data.TensorDataset(tensor_x, tensor_ps_score,
                                                           tensor_y_f, tensor_y_cf)
        return processed_dataset

    @staticmethod
    def concat_np_arr(X, Y, axis=1):
        return np.concatenate((X, Y), axis)

    @staticmethod
    def get_device():
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    @staticmethod
    def get_num_correct(preds, labels):
        return preds.argmax(dim=1).eq(labels).sum().item()

    @staticmethod
    def get_shanon_entropy(prob):
        if prob < 0:
            return
        if prob == 1:
            return -(prob * math.log(prob))
        elif prob == 0:
            return -((1 - prob) * math.log(1 - prob))
        else:
            return -(prob * math.log(prob)) - ((1 - prob) * math.log(1 - prob))

    @staticmethod
    def get_dropout_probability(entropy, gama=1):
        return 1 - (gama * 0.5) - (entropy * 0.5)

    @staticmethod
    def get_dropout_mask(prob, x):
        return Bernoulli(torch.full_like(x, 1 - prob)).sample() / (1 - prob)

    @staticmethod
    def KL_divergence(rho, rho_hat, device):
        # sigmoid because we need the probability distributions
        rho_hat = torch.mean(torch.sigmoid(rho_hat), 1)
        rho = torch.tensor([rho] * len(rho_hat)).to(device)
        return torch.sum(rho * torch.log(rho / rho_hat) + (1 - rho) * torch.log((1 - rho) / (1 - rho_hat)))

    @staticmethod
    def get_runs(params):
        """
        Gets the run parameters using cartesian products of the different parameters.
        :param params: different parameters like batch size, learning rates
        :return: iterable run set
        """
        Run = namedtuple("Run", params.keys())

        runs = []
        for v in product(*params.values()):
            runs.append(Run(*v))

        return runs

    @staticmethod
    def write_to_csv(file_name, list_to_write):
        pd.DataFrame.from_dict(
            list_to_write,
            orient='columns'
        ).to_csv(file_name)
