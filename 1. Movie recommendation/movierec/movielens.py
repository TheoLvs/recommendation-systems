import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from tqdm import tqdm_notebook
from sklearn.neighbors import NearestNeighbors,KDTree

plt.style.use("seaborn")


DATAPATH = "../data/ml-latest-small"



class Movies(pd.DataFrame):


    def __init__(self,**kwargs):


        data_movies = pd.read_csv(os.path.join(DATAPATH,"movies.csv"))
        super().__init__(data_movies,**kwargs)


        self._clean_fields()
        self._merge_with_links()
        self._parse_year()
        self._create_genres_dummies()


    def _clean_fields(self):
        self["title"] = self["title"].map(lambda x : x.strip())
        self["genres"] = self["genres"].map(lambda x : x.strip())


    def _parse_year(self):

        def parse_year(x):
            year = x[-6:]
            if year[0] == "(" and year[-1] == ")":
                return int(year[1:-1])
            else:
                return np.NaN


        self["year"] = self["title"].map(parse_year)


    def _create_genres_dummies(self):
        
        genres = self["genres"].str.get_dummies(sep="|")
        genres.columns = ["genre_"+x for x in genres.columns]
        data = pd.concat([self.drop("genres",axis = 1),genres],axis = 1)
        data = data.drop(["genre_(no genres listed)"],axis = 1)
        super().__init__(data)



    def _merge_with_tags(self):
        tags = pd.read_csv(os.path.join(DATAPATH,"tags.csv"))
        tags.groupby("movieId",as_index = False).agg({"tag":lambda x : ", ".join(set(x))})
        data = self.merge(tags,on="movieId",how = "left")
        super().__init__(data)


    def _merge_with_links(self):
        links = pd.read_csv(os.path.join(DATAPATH,"links.csv"))[["movieId","imdbId"]]
        data = self.merge(links,on="movieId",how = "left")
        super().__init__(data)


    def show_movies_by_year(self):
        
        self["year"].value_counts().sort_index().plot(figsize = (15,4),title = "Movies by year")
        plt.show()


    def show_movies_by_genre(self):

        (self[[x for x in self.columns if x.startswith("genre")]].sum()
            .sort_values(ascending = True)
            .plot(kind = "barh",figsize = (8,8),title = "Movies by genre")
        )
        plt.show()



    def train_KNN(self):

        features = self._get_features()
        self.knn = KDTree(self[features], leaf_size=30, metric='euclidean')


    def _get_features(self):

        features = []
        features += [x for x in self.columns if x.startswith("genre")]
        return features


    def recommend(self,n = 5,movie_id = None,imdb_id = None,vector = None,genres = None,random = False):


        features = self._get_features()


        if movie_id is not None or imdb_id is not None:
            if movie_id is not None:
                data = self.query(f"movieId=='{movie_id}'")
            else:
                data = self.query(f"imdbId=='{imdb_id}'")


            _,indices = self.knn.query(data[features],k = n+1)


            recos = self.iloc[indices[0]]
            if data.index[0] in recos.index:
                recos = recos.drop(data.index[0])
            else:
                recos = recos.iloc[:-1]
            return recos.iloc[:,:3]

            

