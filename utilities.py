from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np
from sklearn import cluster, decomposition
from sklearn.metrics.cluster import normalized_mutual_info_score, adjusted_mutual_info_score
from sklearn.preprocessing import normalize
import inspect
import time


class Utilities:
    def __init__(self):
        self.data_botswana = loadmat('sets/Botswana.mat')
        self.data_salinas = loadmat('sets/Salinas.mat')
        self.data_pavia = loadmat('sets/Pavia.mat')
        self.data_pavia_u = loadmat('sets/PaviaU.mat')
        self.data_kennedy = loadmat('sets/KSC.mat')
        self.data_pines = loadmat('sets/Indian_pines.mat')
        self.data_salinas_a = loadmat('sets/SalinasA.mat')

        self.data_pines_corrected = loadmat('sets/Indian_pines_corrected.mat')
        self.data_salinas_a_corrected = loadmat('sets/SalinasA_corrected.mat')
        self.data_salinas_corrected = loadmat('sets/Salinas_corrected.mat')

        self.data_botswana_gt = loadmat('sets/Botswana_gt.mat')
        self.data_pavia_gt = loadmat('sets/Pavia_gt.mat')
        self.data_pavia_u_gt = loadmat('sets/PaviaU_gt.mat')
        self.data_kennedy_gt = loadmat('sets/KSC_gt.mat')
        self.data_pines_gt = loadmat('sets/Indian_pines_gt.mat')
        self.data_salinas_a_gt = loadmat('sets/SalinasA_gt.mat')
        self.data_salinas_gt = loadmat('sets/Salinas_gt.mat')
        self.mat_to_array()

        self.str_array = ["Botswana", "Salinas", "Pavia", "Pavia U", "Kennedy",
                          "Pines", "Salinas A", "Pines corrected", "Salinas A corrected", "Salinas corrected"]

        self.data_array = [self.data_botswana, self.data_salinas, self.data_pavia, self.data_pavia_u,
                           self.data_kennedy, self.data_pines, self.data_salinas_a, self.data_pines_corrected,
                           self.data_salinas_a_corrected, self.data_salinas_corrected]

        self.data_gt_array = [self.data_botswana_gt, self.data_salinas_gt, self.data_pavia_gt, self.data_pavia_u_gt,
                              self.data_kennedy_gt, self.data_pines_gt, self.data_salinas_a_gt, self.data_pines_gt,
                              self.data_salinas_a_gt, self.data_salinas_gt]

        self.k_array = [0, 6, 9, 9, 0, 16, 6, 16, 6, 6]

        self.percentage_array = [0.03, 0.05, 0.1, 0.15, 0.5, 0.75]

        # self.pca_then_kmean(self.data_pavia, self.data_pavia_gt, 16, True)
        # self.kmean_no_pca(self.data_pavia_u, self.data_pavia_u_gt, 9, True)

        # self.experiment_one()
        # self.experiment_two()

    def experiment_one(self):
        for i in range(len(self.data_array)):
            print(self.str_array[i])
            s, t = self.kmean_no_pca(self.data_array[i], self.data_gt_array[i], self.k_array[i], False)
            print("NMI: " + str(s))
            print("Time: " + str(t))

    def experiment_two(self):
        for i in range(len(self.data_array)):
            print(self.str_array[i])
            for j in range(len(self.percentage_array)):
                s, t1, t2 = self.pca_then_kmean(self.data_array[i], self.data_gt_array[i], self.k_array[i],
                                                self.percentage_array[j], False)
                print("Principal Components: " + str(self.percentage_array[j] * 100) + "%")
                print("NMI: " + str(s))
                print("Time PCA: " + str(t1))
                print("Time KMEAN: " + str(t2))

    def pca_then_kmean(self, data, data_gt, k, percentage, display):
        start = time.time()
        x, y, z = data.shape
        samples = x * y

        print("Calculating PCA")
        data_gt_transformed = data_gt.reshape(samples)
        vectors = data.reshape(samples, z)

        pca1 = decomposition.PCA(n_components=int(z * percentage))
        vec_pca1 = pca1.fit_transform(vectors)
        end = time.time()
        t1 = (end - start)

        start = time.time()
        print("Calculating Kmeans")
        data = self.kmeans(vec_pca1, x, y, k, display)
        end = time.time()
        t2 = (end - start)
        data = self.mask_background(data, data_gt_transformed, samples)
        # print(normalized_mutual_info_score(data, data_gt_transformed, average_method="arithmetic"))
        return normalized_mutual_info_score(data, data_gt_transformed, average_method="arithmetic"), t1, t2

    def kmean_no_pca(self, data, data_gt, k, display):
        x, y, z = data.shape
        samples = x * y

        data_gt_transformed = data_gt.reshape(samples)
        vectors = data.reshape(samples, z)

        # vectors = self.mask_background(vectors, data_gt_transformed, samples)

        # print("Calculating Kmeans")
        start = time.time()
        data = self.kmeans(vectors, x, y, k, display)
        end = time.time()
        data = self.mask_background(data, data_gt_transformed, samples)
        return normalized_mutual_info_score(data_gt_transformed, data, average_method="arithmetic"), (end - start)

    def kmeans(self, data, x, y, n_classes, display):
        if n_classes != 0:
            clf = cluster.KMeans(n_clusters=n_classes, max_iter=400)
        else:
            clf = cluster.KMeans(max_iter=400)
        img = clf.fit(data)
        if display:
            plt.figure(figsize=(7, 7))
            plt.imshow(img.labels_.reshape((x, y)))
            plt.show()
        return img.labels_

    def mask_background(self, data, data_gt, samples):
        for i in range(samples):
            if data_gt[i] == 0:
                data[i] = 0
        return data

    def mat_to_array(self):
        self.data_salinas_a_gt = self.data_salinas_a_gt['salinasA_gt'].astype(np.float32)
        self.data_botswana_gt = self.data_botswana_gt['Botswana_gt'].astype(np.float32)
        self.data_pines_gt = self.data_pines_gt['indian_pines_gt'].astype(np.float32)
        self.data_kennedy_gt = self.data_kennedy_gt['KSC_gt'].astype(np.float32)
        self.data_pavia_u_gt = self.data_pavia_u_gt['paviaU_gt'].astype(np.float32)
        self.data_pavia_gt = self.data_pavia_gt['pavia_gt'].astype(np.float32)
        self.data_salinas_gt = self.data_salinas_gt['salinas_gt'].astype(np.float32)

        self.data_botswana = self.data_botswana['Botswana'].astype(np.float32)
        self.data_pavia_u = self.data_pavia_u['paviaU'].astype(np.float32)
        self.data_kennedy = self.data_kennedy['KSC'].astype(np.float32)
        self.data_salinas = self.data_salinas['salinas'].astype(np.float32)
        self.data_salinas_a = self.data_salinas_a['salinasA'].astype(np.float32)
        self.data_pines = self.data_pines['indian_pines'].astype(np.float32)
        self.data_pavia = self.data_pavia['pavia'].astype(np.float32)

        self.data_pines_corrected = self.data_pines_corrected['indian_pines_corrected'].astype(np.float32)
        self.data_salinas_a_corrected = self.data_salinas_a_corrected['salinasA_corrected'].astype(np.float32)
        self.data_salinas_corrected = self.data_salinas_corrected['salinas_corrected'].astype(np.float32)

        self.data_salinas_a_corrected = self.processing_values(self.data_salinas_a_corrected)
        self.data_pines_corrected = self.processing_values(self.data_pines_corrected)

        self.data_pavia_u = self.processing_values(self.data_pavia_u)
        self.data_kennedy = self.processing_values(self.data_kennedy)
        self.data_salinas_a = self.processing_values(self.data_salinas_a)
        self.data_pines = self.processing_values(self.data_pines)
        self.data_botswana = self.processing_values(self.data_botswana)
        self.data_salinas = self.processing_values(self.data_salinas)
        self.data_salinas_a = self.processing_values(self.data_salinas_a)
        self.data_pavia = self.processing_values(self.data_pavia)

    def processing_values(self, data):
        for i in range(data.shape[-1]):
            data[:, :, i] = (data[:, :, i] - np.mean(data[:, :, i])) / np.std(data[:, :, i])
        return data
