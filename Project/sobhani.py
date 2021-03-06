!pip install keras
!pip install stopwords_guilannlp
!pip install nltk
!pip install hazm

import pandas as pd
import numpy as np
from scipy.stats import randint
import seaborn as sns # used for plot interactive graph. 
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2
from IPython.display import display
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn import metrics
from string import punctuation
#import warnings
#warnings.filterwarnings("ignore", category=FutureWarning)

import re
import hazm 
from stopwords_guilannlp import *
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
#--------------------------------

# loading data
df = pd.read_excel('/content/SobhaniComment.xlsx')
df.shape

df.head(2).T # Columns are shown in rows for easy reading

# Create a new dataframe with two columns
df1 = df[['comment', 'Label']].copy()

# Remove missing values (NaN)
df1 = df1[pd.notnull(df1['Label'])]

df1.shape

# Percentage of complaints with text
total = df1['Label'].notnull().sum()
round((total/len(df)*100),1)

pd.DataFrame(df.comment.unique()).values

# Because the computation is time consuming (in terms of CPU), the data was sampled
#df2 = df1.sample(10000, random_state=1).copy()

df2=df1.copy()

# Create a new column 'category_id' with encoded categories 
df2['category_id'] = df2['Label'].factorize()[0]
category_id_df = df2[['comment', 'category_id']].drop_duplicates()


# Dictionaries for future use
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['category_id', 'comment']].values)

# New dataframe
df2.head(10)

fig = plt.figure(figsize=(8,6))
colors = ['grey','grey','grey','grey','grey','grey','grey','grey','grey',
    'grey','darkblue','darkblue','darkblue']
df2.groupby('Label').comment.count().sort_values().plot.barh(
    ylim=0, color=colors, title= 'NUMBER OF Comment IN EACH PRODUCT CATEGORY\n')
plt.xlabel('Number of ocurrences', fontsize = 10);

normalizer =  hazm.Normalizer()
tokenizer = hazm.SentenceTokenizer()
tokens=hazm.word_tokenize

tfidf = TfidfVectorizer(lowercase=False, preprocessor=normalizer.normalize, tokenizer=tokens,ngram_range=(1, 2))

# We transform each complaint into a vector
dcom=df2.comment
features = tfidf.fit_transform(dcom).toarray()

labels = df2.category_id

print("Each of the %d complaints is represented by %d features (TF-IDF score of unigrams and bigrams)" %(features.shape))

# Finding the three most correlated terms with each of the product categories
#N = 3
#lis=liss=[]
#for Product, category_id in sorted(category_to_id.items()):
 # features_chi2 = chi2(features, labels == category_id)
 # indices = np.argsort(features_chi2[0])
 # feature_names = np.array(tfidf.get_feature_names())[indices]
#  unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
 # bigrams = [v for v in feature_names if len(v.split(' ')) == 2]
  #print("\n==> %s:" %(Product))
 # lis.append((unigrams[-N:]))
  #liss.append(bigrams[-N:])

X = df2['Label'] # Collection of documents
y = df2['comment'] # Target or the labels we want to predict (i.e., the 13 different complaints of products)

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.20,
                                                    random_state = 0)

models = [
    RandomForestClassifier(n_estimators=100, max_depth=5, random_state=0),
    LinearSVC(),
]

# 5 Cross-validation
CV = 5
cv_df = pd.DataFrame(index=range(CV * len(models)))

entries = []
for model in models:
  model_name = model.__class__.__name__
  accuracies = cross_val_score(model, features, labels, scoring='accuracy', cv=CV)
  for fold_idx, accuracy in enumerate(accuracies):
    entries.append((model_name, fold_idx, accuracy))
    
cv_df = pd.DataFrame(entries, columns=['model_name', 'fold_idx', 'accuracy'])

mean_accuracy = cv_df.groupby('model_name').accuracy.mean()
std_accuracy = cv_df.groupby('model_name').accuracy.std()

acc = pd.concat([mean_accuracy, std_accuracy], axis= 1, 
          ignore_index=True)
acc.columns = ['Mean Accuracy', 'Standard deviation']
acc

plt.figure(figsize=(8,5))
sns.boxplot(x='model_name', y='accuracy', 
            data=cv_df, 
            color='lightblue', 
            showmeans=True)
plt.title("MEAN ACCURACY (cv = 5)\n", size=14);

X_train, X_test, y_train, y_test,indices_train,indices_test = train_test_split(features, 
                                                               labels, 
                                                               df2.index, test_size=0.25, 
                                                               random_state=1)
model = LinearSVC()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Classification report
print('\t\t\t\tCLASSIFICATIION METRICS\n')
print(metrics.classification_report(y_test, y_pred, 
                                    target_names= df2['Label'].unique()))

conf_mat = confusion_matrix(y_test, y_pred)

#for predicted in category_id_df.category_id:
#  for actual in category_id_df.category_id:
#    if predicted != actual and conf_mat[actual, predicted] >= 20:
#      print("'{}' predicted as '{}' : {} examples.".format(id_to_category[actual], 
 #                                                          id_to_category[predicted], 
  #                                                         conf_mat[actual, predicted]))
 #   
 #     display(df2.loc[indices_test[(y_test == actual) & (y_pred == predicted)]][['Label', 
 #                                                               'comment']])
 #     print('')

model.fit(features, labels)

#N = 4
#for Product, category_id in sorted(category_to_id.items()):
 # indices = np.argsort(model.coef_[category_id])
 # feature_names = np.array(tfidf.get_feature_names())[indices]
#  unigrams = [v for v in reversed(feature_names) if len(v.split(' ')) == 1][:N]
#  bigrams = [v for v in reversed(feature_names) if len(v.split(' ')) == 2][:N]
#  print("\n==> '{}':".format(Product))
 # print("  * Top unigrams: %s" %(', '.join(unigrams)))
 # print("  * Top bigrams: %s" %(', '.join(bigrams)))

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.25,
                                                    random_state = 0)

tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5,
                        ngram_range=(1, 2), 
                        stop_words='english')

fitted_vectorizer = tfidf.fit(X_train)
tfidf_vectorizer_vectors = fitted_vectorizer.transform(X_train)

model = LinearSVC().fit(tfidf_vectorizer_vectors, y_train)

new_complaint = "عالیه بنظرم بخرید خوشتون میاد"
result=fitted_vectorizer.transform([new_complaint])
t=model.predict(result)
i=0
while i<len(df):
  if df['comment'][i]==t:
    emoj=df['Label'][i]
    break
  i+=1

!pip install emoji
import emoji

emo=pd.read_csv('/content/Emoji_Sobhani.csv')
dic=emo.Code

dic

if emoj == dic[0]:
   print(  "\U0001F600")
if emoj == dic[1]:
   print(   "\U0001F643")
if emoj == dic[2]:
   print(   "\U0001F970")

if emoj == dic[3]:
   print(   "\U0001F44E")

if emoj == dic[4]:
   print(   "\U0001F636")

if emoj == dic[5]:
   print(   "\U0001F614")

if emoj == dic[6]:
   print(   "\U0001F44D")

if emoj == dic[7]:
  print(    "\U0001F33A")

if emoj == dic[8]:
  print(    "\U0001F62F")

if emoj == dic[9]:
   print(   "\U0001F64F")
