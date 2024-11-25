# -*- coding: utf-8 -*-
"""TwitterSentimentAnalysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1s5oYgnIw644UaWyyX1fHHl08QUHlA8Ir
"""

from google.colab import drive
drive.mount('/content/drive')
! pip install -q kaggle
from google.colab import files
files.upload()
#configuring the path of kaggle.jason file
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json
#API to fetch the data set from the kaggle
!kaggle datasets download -d kazanova/sentiment140

#extracting the compressed dataset
from zipfile import ZipFile
dataset = '/content/sentiment140.zip'
with ZipFile(dataset,'r') as zip:
  zip.extractall()
  print("the data set is extracted")

import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import nltk
nltk.download('stopwords')
#print the stopwords in English
print(stopwords.words('english'))
#loading the csv file data into pandas dataframe
twitter_data = pd.read_csv('/content/training.1600000.processed.noemoticon.csv',encoding='ISO-8859-1')
#checking the number of rows and colomns
twitter_data.shape
#printing the first 5rows of the dataferame
twitter_data.head()

#naming the colomns and reading the dataset again
colomn_names=['Target','id','data','flag','user','text']
twitter_data = pd.read_csv('/content/training.1600000.processed.noemoticon.csv',names=colomn_names,encoding='ISO-8859-1')
#checking the number of rows and colomns
twitter_data.shape
#printing the first 5rows of the dataferame
twitter_data.head()

#verfifing the null values or missing values in the data set
twitter_data.isnull().sum()

#checking the Distribution of Target Colomn
twitter_data['Target'].value_counts()

#Convert the target value 4 to 1
twitter_data.replace({'Target':{4:1}},inplace=True)
#checking the Distribution of Target Colomn
twitter_data['Target'].value_counts()

"""**0 --> Negative 1 --> Positive**

# **Stemming=Stemming is the process of reducing a word to its Rootword**
"""

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Initialize stopwords
stop_words = set(stopwords.words('english'))
def stemming(content):
    try:
        port_stem = PorterStemmer()  # Instantiate inside the function
        stemmed_content = re.sub('[^a-zA-Z]', ' ', content).lower()
        return ' '.join(port_stem.stem(word) for word in stemmed_content.split() if word not in stop_words)
    except Exception as e:
        print(f"Error processing content: {content}. Error: {e}")
        return ""  # Return an empty string on error

def process_data(df):
    with ThreadPoolExecutor() as executor:
        return list(tqdm(executor.map(stemming, df['text']), total=len(df)))

# Process the DataFrame in chunks
chunk_size = 50000  # Adjust based on your memory capacity
num_chunks = len(twitter_data) // chunk_size + 1
stemmed_contents = []
for i in tqdm(range(num_chunks)):
    start = i * chunk_size
    end = min((i + 1) * chunk_size, len(twitter_data))
    chunk = twitter_data.iloc[start:end]
    stemmed_chunk = process_data(chunk)
    stemmed_contents.extend(stemmed_chunk)

# Add the stemmed content back to the DataFrame
twitter_data['stemmed_content'] = stemmed_contents

port_stem = PorterStemmer()

def stemming(content):
  stemmed_content =re.sub('[^a-zA-Z]',' ',content)
  stemmed_content=stemmed_content.lower()
  stemmed_content=stemmed_content.split()
  stemmed_content=[port_stem.stem(word) for word in stemmed_content if not word in stopwords.words('english')]
  stemmed_content=' '.join(stemmed_content)


  return stemmed_content

#Adding the colomn to the twitter data table
twitter_data['stemmed_content']=twitter_data['text'].apply(stemming)
#it took nearly 50min to execute

twitter_data.head()

#seperating the data and label
x=twitter_data['stemmed_content'].values
y=twitter_data['Target'].values

print(x)

from google.colab import drive
drive.mount('/content/drive')

"""**Spliting the data into training data and testing data**"""

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,stratify=y,random_state=2)

#converting the texual data to numerical value
vectorizer = TfidfVectorizer()
vectorizer.fit(x_train)
x_train=vectorizer.transform(x_train)
x_test=vectorizer.transform(x_test)

"""**Training the Machine Learning model**
# **Logistic Regression**
"""

model=LogisticRegression(max_iter=1000)

model.fit(x_train,y_train)

"""**Model Evaluation**

Accuracy Score
"""

x_train_prediction=model.predict(x_train)
training_data_accuracy=accuracy_score(y_train,x_train_prediction)

print('Accuracy on training data:',training_data_accuracy)

x_test_prediction=model.predict(x_test)
testing_data_accuracy=accuracy_score(y_test,x_test_prediction)

print('Accuracy on testing data:',testing_data_accuracy)

"""**Model Accurancy=77%**

**Saving the training Model**
"""

import pickle

filename='trained_model.sav'
pickle.dump(model,open(filename,'wb'))

"""**Using the saving Model for preditions**"""

loaded_model=pickle.load(open('trained_model.sav','rb'))

x_new = x_test[200]
print(y_test[200])
prediction = loaded_model.predict(x_new)
print(prediction)
if(prediction[0]==0):
  print("Negative Tweet")
else:
  print("Positive Tweet")