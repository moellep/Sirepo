# -*- coding: utf-8 -*-
u"""Machine learning tools

:copyright: Copyright (c) 2018-2019 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""

import numpy
import sklearn.cluster
import sklearn.metrics.pairwise
import sklearn.mixture
import sklearn.preprocessing
from pykern.pkcollections import PKDict


def agglomerative(scale, count):
    return sklearn.cluster.AgglomerativeClustering(
        n_clusters=count,
        linkage='complete',
        affinity='euclidean'
    ).fit(scale).labels_


def dbscan(scale, dbscan_eps):
    return sklearn.cluster.DBSCAN(
        eps=dbscan_eps,
        min_samples=3
    ).fit(scale).fit_predict(scale) + 1.


def gmix(scale, count, seed):
    return sklearn.mixture.GaussianMixture(
        n_components=count,
        random_state=seed
    ).fit(scale).predict(scale)


def kmeans(scale, count, seed, kmeans_init):
    return sklearn.metrics.pairwise.pairwise_distances_argmin(
            scale,
            numpy.sort(
                sklearn.cluster.KMeans(
                    init='k-means++',
                    n_clusters=count,
                    n_init=kmeans_init,
                    random_state=seed
                ).fit(scale).cluster_centers_,
                axis = 0
            )
        )


def scale_data(data, scale_range):
    return sklearn.preprocessing.MinMaxScaler(
        feature_range=scale_range
    ).fit_transform(data)