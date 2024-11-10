#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import shutil
import tempfile
import zipfile
from pathlib import Path

import requests

source = "https://www.kaggle.com/api/v1/datasets/download/basilb2s/language-detection"
source_filename = "Language Detection.csv"
filename = source_filename.lower()
dirpath = Path(".")
filepath = dirpath / filename


response = requests.get(source, stream=True, timeout=180)
if response.status_code == 200:
    with tempfile.NamedTemporaryFile() as temp_file:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:  # filter out keep-alive new chunks
                temp_file.write(chunk)
        temp_file.flush()
        temp_file.seek(0)

        with zipfile.ZipFile(temp_file, "r") as zip_ref:
            zip_ref.extractall(dirpath)
    shutil.move(dirpath / source_filename, filepath)
    print(f"Download complete! Saved and extracted: {dirpath}")
else:
    print(f"Download failed with status code: {response.status_code}")



# In[143]:


source_filename: str = "Language Detection.csv"
Path(source_filename).suffix


# In[60]:


import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


# In[147]:


df = pd.read_csv(filepath)
df["is_italian"] = (df["Language"] == "Italian")
print(df["is_italian"].sum(), df["is_italian"].count())

# Create a pipeline
text_clf = Pipeline([
    ("vect", CountVectorizer(strip_accents="unicode")),
    ("clf", MultinomialNB()),
])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    df["Text"], df["Language"], test_size=0.3, random_state=42,
)

# Fit the pipeline to the training data
text_clf.fit(X_train, y_train)

# Make predictions on the test data
predicted = text_clf.predict(X_test)


# In[130]:


text_clf.fit(X_train, y_train)


# In[131]:


text_clf.score(X_test, y_test)


# In[146]:


text_clf.predict(["meglio niente"])


# In[ ]:




