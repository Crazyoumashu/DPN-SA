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

import os

import numpy as np
import pandas as pd

from Utils import Utils


class DataLoader:
    def preprocess_for_graphs(self, csv_path):
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), csv_path), header=None)
        return self.__convert_to_numpy(df)

    def prep_process_all_data(self, csv_path):
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), csv_path), header=None)
        np_covariates_X, np_treatment_Y = self.__convert_to_numpy(df)
        return np_covariates_X, np_treatment_Y

    def preprocess_data_from_csv(self, csv_path, split_size):
        # print(".. Data Loading ..")
        # data load
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), csv_path), header=None)
        np_covariates_X, np_treatment_Y = self.__convert_to_numpy(df)
        print("ps_np_covariates_X: {0}".format(np_covariates_X.shape))
        print("ps_np_treatment_Y: {0}".format(np_treatment_Y.shape))

        np_covariates_X_train, np_covariates_X_test, np_covariates_Y_train, np_covariates_Y_test = \
            Utils.test_train_split(np_covariates_X, np_treatment_Y, split_size)

        print("np_covariates_X_train: {0}".format(np_covariates_X_train.shape))
        print("np_covariates_Y_train: {0}".format(np_covariates_Y_train.shape))
        print("---" * 20)
        print("np_covariates_X_test: {0}".format(np_covariates_X_test.shape))
        print("np_covariates_Y_test: {0}".format(np_covariates_Y_test.shape))
        print("---" * 20)

        return np_covariates_X_train, np_covariates_X_test, np_covariates_Y_train, np_covariates_Y_test

    def preprocess_data_from_csv_augmented(self, csv_path, split_size):
        # print(".. Data Loading synthetic..")
        # data load
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), csv_path), header=None)
        np_covariates_X, np_treatment_Y = self.__convert_to_numpy_augmented(df)
        print("ps_np_covariates_X: {0}".format(np_covariates_X.shape))
        print("ps_np_treatment_Y: {0}".format(np_treatment_Y.shape))

        np_covariates_X_train, np_covariates_X_test, np_covariates_Y_train, np_covariates_Y_test = \
            Utils.test_train_split(np_covariates_X, np_treatment_Y, split_size)
        print("np_covariates_X_train: {0}".format(np_covariates_X_train.shape))
        print("np_covariates_Y_train: {0}".format(np_covariates_Y_train.shape))
        print("---" * 20)
        print("np_covariates_X_test: {0}".format(np_covariates_X_test.shape))
        print("np_covariates_Y_test: {0}".format(np_covariates_Y_test.shape))
        return np_covariates_X_train, np_covariates_X_test, np_covariates_Y_train, np_covariates_Y_test

    @staticmethod
    def convert_to_tensor(ps_np_covariates_X, ps_np_treatment_Y):
        return Utils.convert_to_tensor(ps_np_covariates_X, ps_np_treatment_Y)

    def prepare_tensor_for_DCN(self, ps_np_covariates_X, ps_np_treatment_Y, ps_list,
                               is_synthetic):
        # print("ps_np_covariates_X: {0}".format(ps_np_covariates_X.shape))
        # print("ps_np_treatment_Y: {0}".format(ps_np_treatment_Y.shape))
        X = Utils.concat_np_arr(ps_np_covariates_X, ps_np_treatment_Y, axis=1)

        # col of X -> x1 .. x25, Y_f, Y_cf, T, Ps
        X = Utils.concat_np_arr(X, np.array([ps_list]).T, axis=1)
        # print("Big X: {0}".format(X.shape))
        df_X = pd.DataFrame(X)
        treated_df_X, treated_ps_score, treated_df_Y_f, treated_df_Y_cf = \
            self.__preprocess_data_for_DCN(df_X, treatment_index=1,
                                           is_synthetic=is_synthetic)

        control_df_X, control_ps_score, control_df_Y_f, control_df_Y_cf = \
            self.__preprocess_data_for_DCN(df_X, treatment_index=0,
                                           is_synthetic=is_synthetic)

        np_treated_df_X, np_treated_ps_score, np_treated_df_Y_f, np_treated_df_Y_cf = \
            self.__convert_to_numpy_DCN(treated_df_X, treated_ps_score, treated_df_Y_f,
                                        treated_df_Y_cf)

        np_control_df_X, np_control_ps_score, np_control_df_Y_f, np_control_df_Y_cf = \
            self.__convert_to_numpy_DCN(control_df_X, control_ps_score, control_df_Y_f,
                                        control_df_Y_cf)

        # print(".. Treated Statistics ..")
        # print(np_treated_df_X.shape)

        # print(".. Control Statistics ..")
        # print(np_control_df_X.shape)

        return {
            "treated_data": (np_treated_df_X, np_treated_ps_score,
                             np_treated_df_Y_f, np_treated_df_Y_cf),
            "control_data": (np_control_df_X, np_control_ps_score,
                             np_control_df_Y_f, np_control_df_Y_cf)
        }

    @staticmethod
    def convert_to_tensor_DCN(np_df_X,
                              np_ps_score,
                              np_df_Y_f,
                              np_df_Y_cf):
        return Utils.convert_to_tensor_DCN(np_df_X,
                                           np_ps_score,
                                           np_df_Y_f,
                                           np_df_Y_cf)

    @staticmethod
    def __convert_to_numpy(df):
        covariates_X = df.iloc[:, 5:]
        treatment_Y = df.iloc[:, 0:1]
        outcomes_Y = df.iloc[:, 1:3]

        np_covariates_X = Utils.convert_df_to_np_arr(covariates_X)
        np_outcomes_Y = Utils.convert_df_to_np_arr(outcomes_Y)
        np_X = Utils.concat_np_arr(np_covariates_X, np_outcomes_Y, axis=1)

        np_treatment_Y = Utils.convert_df_to_np_arr(treatment_Y)

        return np_X, np_treatment_Y

    def __convert_to_numpy_augmented(self, df):
        covariates_X = df.iloc[:, 5:]
        treatment_Y = df.iloc[:, 0:1]
        outcomes_Y = df.iloc[:, 1:3]

        np_covariates_X = Utils.convert_df_to_np_arr(covariates_X)
        np_std = np.std(np_covariates_X, axis=0)
        np_outcomes_Y = Utils.convert_df_to_np_arr(outcomes_Y)

        noise1 = self.get_noise(np_std, error=1.96)
        noise2 = self.get_noise(np_std, error=2.00)
        # noise3 = self.get_noise(np_std, error=2.45)

        random_correlated1 = np_covariates_X + noise1
        random_correlated2 = np_covariates_X + noise2
        # random_correlated3 = np_covariates_X + noise3

        random_X = np.random.permutation(np.random.random((747, 25)) * 10)
        np_covariates_X = np.concatenate((np_covariates_X, random_X), axis=1)
        np_covariates_X = np.concatenate((np_covariates_X, random_correlated1), axis=1)
        np_covariates_X = np.concatenate((np_covariates_X, random_correlated2), axis=1)
        # np_covariates_X = np.concatenate((np_covariates_X, random_correlated3), axis=1)

        np_X = Utils.concat_np_arr(np_covariates_X, np_outcomes_Y, axis=1)

        np_treatment_Y = Utils.convert_df_to_np_arr(treatment_Y)

        return np_X, np_treatment_Y

    @staticmethod
    def get_noise(np_std, error):
        noise = np.empty([747, 25])
        id = -1
        for std in np_std:
            id += 1
            noise[:, id] = np.random.normal(0, error * std)

        return noise

    @staticmethod
    def __preprocess_data_for_DCN(df_X, treatment_index, is_synthetic):
        df = df_X[df_X.iloc[:, -2] == treatment_index]

        if is_synthetic:
            # for synthetic dataset #covariates: 225
            df_X = df.iloc[:, 0:100]
        else:
            # for original dataset #covariates: 25
            df_X = df.iloc[:, 0:25]

        ps_score = df.iloc[:, -1]
        df_Y_f = df.iloc[:, -4:-3]
        df_Y_cf = df.iloc[:, -3:-2]

        return df_X, ps_score, df_Y_f, df_Y_cf

    @staticmethod
    def __convert_to_numpy_DCN(df_X, ps_score, df_Y_f, df_Y_cf):
        np_df_X = Utils.convert_df_to_np_arr(df_X)
        np_ps_score = Utils.convert_df_to_np_arr(ps_score)
        np_df_Y_f = Utils.convert_df_to_np_arr(df_Y_f)
        np_df_Y_cf = Utils.convert_df_to_np_arr(df_Y_cf)

        # print("np_df_X: {0}".format(np_df_X.shape))
        # print("np_ps_score: {0}".format(np_ps_score.shape))
        # print("np_df_Y_f: {0}".format(np_df_Y_f.shape))
        # print("np_df_Y_cf: {0}".format(np_df_Y_cf.shape))

        return np_df_X, np_ps_score, np_df_Y_f, np_df_Y_cf
