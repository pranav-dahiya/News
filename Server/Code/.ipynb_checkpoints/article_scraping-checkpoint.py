import json
import datetime
import tqdm
import newspaper
import multiprocess as mp
import pandas as pd
from sqlalchemy import create_engine
from gensim.models.doc2vec import Doc2Vec
from nltk import word_tokenize

engine = create_engine('mysql+mysqlconnector://user:u53r_mysql@db/article_clustering')


def get_sources():
    try:
        sources = pd.read_sql('source', engine, columns=['id', 'url'], index_col='id')['url']
    except:
        return pd.Series()
    return sources


def get_articles(source_id, source_url):
    url_set = set(pd.read_sql('SELECT url FROM article WHERE source_id = ' + str(source_id), engine)['url'])
    source = newspaper.build(source_url, memoize_articles=False)
    source.articles = [article for article in source.articles if article.url not in url_set]
    newspaper.news_pool.set([source], threads_per_source=10)
    newspaper.news_pool.join()
    article_frame = list()
    model = Doc2Vec.load('doc2vec')
    for article in source.articles:
        article.parse()
        if article.publish_date and article.text:
            vector = [float(val) for val in model.infer_vector(word_tokenize(article.text))]
            article_frame.append({'title': article.title, 
                                  'date': article.publish_date, 
                                  'top_image': article.top_image, 
                                  'url': article.url, 
                                  'text': article.text, 
                                  'vector': json.dumps(vector)})
    article_frame = pd.DataFrame(article_frame)
    article_frame['source_id'] = source_id
    try:
        article_frame.to_sql('article', engine, if_exists='append', index=False)
    except:
        print(article_frame)

    
if __name__ == '__main__':
    while(True):
        print(datetime.datetime.now())
        pool = mp.Pool()
        for source_id, source_url in get_sources().iteritems():
            pool.apply_async(get_articles, (source_id, source_url))
        pool.close()
        pool.join()