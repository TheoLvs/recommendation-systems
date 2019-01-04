import bs4 as bs
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm_notebook
import time
import os

def scrapping(url,timeout = 15,session = None,verify = True):
    """Scrapping function that takes an URL to get a beautiful soup object of the source code of the URL
    A timeout is set by default at 15 seconds

    Returns : a beautiful soup object
    """
    if session is not None:
        html = session.get(url,timeout = timeout,verify = verify).content
    else:     
        html = requests.get(url,timeout = timeout,verify = verify).content
    return parsing(html)



def parsing(html):
    return bs.BeautifulSoup(html,'lxml')




class IMDBScrapper(object):
    def __init__(self):
        pass


    def get_movie_url(self,imdb_id):
        return f"https://www.imdb.com/title/tt0{imdb_id}"

    def get_movie_page(self,imdb_id):
        return scrapping(self.get_movie_url(imdb_id))

    def set_page(self,page = None,imdb_id = None):
        if page is not None:
            self.page = page

        elif imdb_id is not None:
            self.page = self.get_movie_page(imdb_id)


    def get_movie_poster(self,imdb_id,save_to = None):

        # Parse and set page from movie
        page = self.get_movie_page(imdb_id = imdb_id)

        # Find img url
        img_url = page.find("div",class_ = "poster").find("img").attrs["src"]

        # Get image
        img = self._fetch_img_from_url(img_url)

        if save_to is not None:
            name = f"poster_{imdb_id}.png"
            img.save(os.path.join(save_to,name))

        return img


    def get_movie_posters(self,imdb_ids,save_to = None,wait = 0.5):

        skipped = []

        for imdb_id in tqdm_notebook(imdb_ids):

            try:
                self.get_movie_poster(imdb_id,save_to = save_to)
                time.sleep(wait)
            except:
                skipped.append(imdb_id)

        return skipped


    @staticmethod
    def _fetch_img_from_url(url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img


