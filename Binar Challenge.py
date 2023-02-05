#!/usr/bin/env python
# coding: utf-8

# # Library

# In[1]:


# Import library
import numpy as np
import re
import pandas as pd 
import matplotlib as plt

import sqlite3 

from flask import Flask, jsonify

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from


# # SQLite Connection

# In[2]:


# Connection to DB 
conn = sqlite3.connect('database/challenge.db')


# In[3]:


# Create Table polos

conn.execute('''
CREATE TABLE Tweet ( Id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Tweet varchar(255) not null
                        );
''')

conn.commit()


# Cleansing Data

# In[4]:


# Import Dataset
df = pd.read_csv('data.csv', encoding='latin-1')

# Import Kamus Alay
kamus = pd.read_csv('new_kamusalay.csv', encoding='latin-1',header=None)
kamus = kamus.rename(columns={0: 'original',1: 'replacement'})
kamus = dict(zip(kamus['original'], kamus['replacement']))

print(df)


# In[5]:


# Func Cleansing 

def lowercase(text):
    return text.lower()

def cleansing_text(text):
    text = text.strip() #hapus spasi awal dan akhir
    text = re.sub('\n',' ',text) #hapus enter
    text = re.sub('rt',' ',text) #hapus RT(retweet)
    text = re.sub('user',' ',text) #hapus kata user
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))',' ',text) #hapus link www/https/http
    text = re.sub(' +',' ',text) #hapus spasi ganda
    return text

def cleansing_simbol(text):
    text = re.sub('[^0-9a-zA-Z]+',' ',text)
    return text

def cleansing_alay(text):
    return ' '.join([kamus[word] if word in kamus else word for word in text.split(' ')])

def preprocessing(text):
    text = lowercase(text)
    text = cleansing_text(text)
    text = cleansing_simbol(text)
    text = cleansing_alay(text)
    return text




# In[6]:


# Apply Func
df['Tweet'] = df['Tweet'].apply(preprocessing)
print(df['Tweet'])


# # API

# In[ ]:


app = Flask(__name__)

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info ={
    'title' : LazyString(lambda: 'API Data Cleansing Challenge Binar' ),
    'version' : LazyString(lambda: '1.0.0' ),
    'description' : LazyString(lambda: 'Dokumentasi API untuk Data Cleansing Challenge Binar' )
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers":[],
    "specs": [
        {
            "endpoint" : 'docs',
            "route" : '/docs.json',
        }
    ],
    "static_url_path" : "/flasgger_static",
    "swagger_ui": True,
    "specs_route" : "/docs/"
}
swagger = Swagger(app=app, 
                    config=swagger_config,
                    template=swagger_template
)

@swag_from("docs/fungsi_dasar.yml", methods = ['GET'])
# route ke 1 
@app.route('/', methods=['GET'])
def fungsi_dasar():
    return "Selamat Datang di Fungsi Data Cleansing"

@swag_from("docs/fungsi_1.yml", methods = ['GET'])
# route ke 2 
@app.route('/fungsi_1', methods = ['GET'])
def fungsi_1():
    conn = sqlite3.connect('database/challenge.db')
    Tweets = df['Tweet']
    
    for i in Tweets:
        sql_string = (f'''
                        INSERT INTO Tweet (Tweet) VALUES ('{i}');

        ''')
        conn.execute(sql_string)

    conn.commit()
    return df['Tweet'].to_dict() 


@swag_from("docs/fungsi_2.yml", methods = ['GET'])
# route ke 3 
@app.route('/fungsi_2/<kalimat>', methods = ['GET'])
def fungsi_2(kalimat):
    conn = sqlite3.connect('database/challenge.db')
    kalimat = preprocessing(kalimat)
    
    sql_string = (f'''
                    INSERT INTO Tweet (Tweet) VALUES ('{kalimat}')

    ''')
    conn.execute(sql_string)
        
    conn.commit()
    return kalimat

if __name__ == "__main__":
    app.run()


# In[ ]:

# Analisis

# 1. Rata - rata char
print('==================================================================')
df['total_char'] = df['Tweet'].apply(len)
print ("rata rata huruf setiap tweet", df['total_char'].mean())

# 2. Rata - rata kata
print('==================================================================')
df['total_word'] = df['Tweet'].apply(lambda sent: len(sent.split()))
print ("rata rata kata setiap tweet", df['total_word'].mean())

# 3. Menghitung frekuensi kemunculan setiap kata
print('==================================================================')
df['splitted_tweet'] = [tweet.split(" ") for tweet in df['Tweet']] #mecah kata
count_of_words = {} #loop ngitung banyak kata
for splitted_tweet in df['splitted_tweet']:
    for word in splitted_tweet:
        try:
            count_of_words[word] += 1
        except KeyError:
            count_of_words[word] = 1

# 4. Top 5 dan bot 5
print('==================================================================')
print(sorted(count_of_words.items(), key = lambda x:x[1],reverse = True)[1:6]) #top 5 
print(sorted(count_of_words.items(), key = lambda x:x[1],reverse = False)[:5]) #bot 5 

# 5. Rata - rata kata hatespeech dan non - hatespeech
df.groupby('HS').total_word.mean().plot(kind='bar')


# In[ ]:


# In[ ]:

