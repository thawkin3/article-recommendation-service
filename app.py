from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
import json
import os
import pandas as pd
import pinecone
import re
import requests
from sentence_transformers import SentenceTransformer
import swifter

app = Flask(__name__)

PINECONE_INDEX_NAME = "article-recommendation-service"
DATA_FILE = "articles.csv"
NROWS = 1000

def initialize_pinecone():
    load_dotenv()
    PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
    pinecone.init(api_key=PINECONE_API_KEY)

def delete_existing_pinecone_index():
    if PINECONE_INDEX_NAME in pinecone.list_indexes():
        pinecone.delete_index(PINECONE_INDEX_NAME)

def create_pinecone_index():
    pinecone.create_index(name=PINECONE_INDEX_NAME, metric="cosine", shards=1)
    pinecone_index = pinecone.Index(name=PINECONE_INDEX_NAME)

    return pinecone_index

def create_model():
    model = SentenceTransformer('average_word_embeddings_komninos')

    return model

def prepare_data(data):
    # rename id column and remove unnecessary columns
    print("Preparing data...")
    data.rename(columns={"Unnamed: 0": "article_id"}, inplace = True)
    data.drop(columns=['date'], inplace = True)

    # extract only first few sentences of each article for quicker vector calculations
    data['content'] = data['content'].fillna('')
    data['content'] = data.content.swifter.apply(lambda x: ' '.join(re.split(r'(?<=[.:;])\s', x)[:4]))
    data['title_and_content'] = data['title'] + data['content']

    # create a vector embedding based on title and article columns
    print('Encoding articles...')
    encoded_articles = model.encode(data['title_and_content'], show_progress_bar=True)
    data['article_vector'] = pd.Series(encoded_articles.tolist())

    return data

def upload_items(data):
    print("Uploading items")

    # create a list of items for upload
    items_to_upload = [(row.id, row.article_vector) for i,row in data.iterrows()]

    # upsert
    pinecone_index.upsert(items=items_to_upload)

def process_file(filename):
    data = pd.read_csv(filename, nrows=NROWS)
    data = prepare_data(data)
    upload_items(data)
    pinecone_index.info()
    print(data.head())

    return data

initialize_pinecone()
delete_existing_pinecone_index()
pinecone_index = create_pinecone_index()
model = create_model()
uploaded_data = process_file(filename=DATA_FILE)

@app.route("/")
def index():
    return render_template("index.html")
