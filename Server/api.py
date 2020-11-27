import json
import pandas as pd
from sqlalchemy import create_engine
from flask import Flask
from flask import request
from sqlalchemy import create_engine


app = Flask(__name__)
engine = create_engine('mysql+mysqlconnector://user:u53r_mysql@db/article_clustering')
    

@app.route('/categories', methods=['GET'])
def get_categories():
      query =  """select cluster_id, group_concat(article_id) as article_ids, wordcloud
                  from cluster
                  join article_cluster on cluster.id = article_cluster.cluster_id
                  join article on article_cluster.article_id = article.id
                  join source on article.source_id = source.id
                  where source.url in (""" + request.args.get('source_urls')[1:-1] + ")" + \
               """group by cluster_id"""
      return pd.read_sql(query, engine).to_json(orient='split', index=False)
      

@app.route('/articles', methods=['GET'])
def get_articles():
      query =  """select top_image, title, date, url 
                  from article 
                  where id in (""" + request.args.get('article_ids')[1:-1] + ")"
      return pd.read_sql(query, engine).to_json(orient='split', index=False)


if __name__ == '__main__':
      app.run(debug=True, host='0.0.0.0')
