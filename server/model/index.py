import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

cols = ['url', 'trustworthy']
phishtank_dataset = pd.read_csv('../datasets/verified_online.csv', usecols=cols)
phishtank_dataset['trustworthy'] = phishtank_dataset['trustworthy'].replace({'yes': True, 'no': False})

cols = ['url', 'label']

kaggle_dataset = pd.read_csv('../datasets/Webpages_Classification_train_data.csv', usecols=cols)
kaggle_dataset['label'] = kaggle_dataset['label'].replace({'good': True, 'bad': False})
kaggle_dataset = kaggle_dataset.rename(columns={'label': 'trustworthy'})

dataset = pd.concat([phishtank_dataset, kaggle_dataset], ignore_index=True)

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(analyzer='char', ngram_range=(2, 4))),
    ('clf', LogisticRegression(solver='liblinear'))
])

pipeline.fit(dataset['url'], dataset['trustworthy'])

with open('model_pipeline.pkl', 'wb') as f:
    pickle.dump(pipeline, f)