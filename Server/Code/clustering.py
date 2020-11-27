import datetime
import time
import json
import pandas as pd
import multiprocess as mp
from collections import Counter
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.clustering import BisectingKMeans
from pyspark.sql.types import ArrayType, DoubleType
from pyspark.sql import functions as F
from sqlalchemy import create_engine
from nltk import word_tokenize
from nltk.corpus import stopwords

sc = SparkContext()
spark = SparkSession(sc)
engine = create_engine('mysql+mysqlconnector://user:u53r_mysql@db/article_clustering')
stopwords_set = set(stopwords.words('english'))


def vocab_gen(text):
    try:
        return Counter([token for token in word_tokenize(text.lower()) if token not in stopwords_set and token.isalnum()])
    except:
        print(text)
        exit(0)

def wordcloud(cluster_id, article_frame):
    #vocab_gen = lambda text: 
    vocab = Counter()
    article_text = article_frame[article_frame['cluster_id'] == cluster_id]['text'].to_list()
    vocab_list = mp.Pool().map(vocab_gen, article_text)
    for text_vocab in vocab_list:
        vocab += text_vocab
    return json.dumps(vocab.most_common(50))


def cluster():
    article_frame = pd.read_sql('article', engine, columns=['vector', 'text', 'id'])
    article = spark.createDataFrame(article_frame[['vector', 'id']])
    
    new_schema = ArrayType(DoubleType(), containsNull=False)
    udf_foo = F.udf(lambda x: x, new_schema)
    article = article.withColumn("vector", udf_foo("vector"))
    
    bkm = BisectingKMeans(k=100, featuresCol='vector')
    model = bkm.fit(article)
    model.setPredictionCol("cluster_id")
    article = model.transform(article)
    
    article_frame = pd.merge(article_frame, article.toPandas(), on='id')
    # article_frame = article_frame.join(pd.read_sql('article', engine, columns=['text', 'id']), on='id', rsuffix='_article')
    article_frame['article_id'] = article_frame['id']
    print(article_frame)
    cluster_frame = pd.DataFrame(article_frame['cluster_id'].unique(), columns=['id'])
    
    print(cluster_frame)
    
    cluster_frame['wordcloud'] = cluster_frame['id'].apply(wordcloud, args=(article_frame, ))
    
    print(cluster_frame)
    
    article_frame = article_frame[['article_id', 'cluster_id']]
    engine.execute('DELETE FROM cluster')
    cluster_frame.to_sql('cluster', engine, if_exists='append', index=False)
    article_frame.to_sql('article_cluster', engine, if_exists='append', index=False)
    
    
if __name__ == '__main__':
    print(datetime.datetime.now())
    cluster()
    time.sleep(60)