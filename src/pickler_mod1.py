#import logging
#logging.basicConfig()
import pdb
import numpy as np
import cPickle as pickle
from gensim.models import Word2Vec
from cut1 import readTXT
from genans import parseAnsOneHot

wordvec_file = '../GloVe/glove.6B.300d.txt'
ansFilename='../Data/mc500.train.ans'
txtFilename='../Data/mc500.train.txt'
stopWordFile = '../Data/stopwords.txt'
#'../Data/mc160.train.txt'
#"../Data/mc500.test.txt"
#"../Data/mc160.test.txt"
#"../Data/mc500.val.txt"
#"../Data/mc160.val.txt"
dataPickle_name = "../Pickle/"+txtFilename.split('/')[-1].split('.')[0]+"."+txtFilename.split('/')[-1].split('.')[1]+".mod1.pickle"
print dataPickle_name
print "Loading word2vec..."
word_vec = Word2Vec.load_word2vec_format(wordvec_file, binary=False)
data = []

ans = parseAnsOneHot(ansFilename)

print "Loading",txtFilename.split('/')[-1],"..."
txtList = readTXT(txtFilename)
stopWord = []
f = open(stopWordFile, 'r')
for line in f:
    stopWord.append(line.split()[0])
pdb.set_trace()
idxCounter = 0
for one in txtList:
    #print 'The shape of one before is '+str(np.shape(one))
    oneQ = []
    for entry in one:
	count = 0.
	temp_vector = np.zeros(300,dtype='float32')
	for word in entry:
	    word = word.lower()
	    if word in stopWord:
		continue
	    if word not in word_vec:
		if '\'s' in word:
		    word = word.split('\'')[0]
		elif 'n\'t' in word:
		    temp_vector = np.add(temp_vector,np.asarray(word_vec[word.split('n')[0]]))
		    count += 1.
		    word = 'not'
		elif '\'d' in word:
		    temp_vector = np.add(temp_vector,np.asarray(word_vec[word.split('\'')[0]]))
		    count += 1.
		    word = 'would'
		elif 'i\'m' in word:
		    temp_vector = np.add(temp_vector,np.asarray(word_vec['i']))
		    count += 1.
		    word = 'am'
		elif '\'ll' in word:
		    temp_vector = np.add(temp_vector,np.asarray(word_vec[word.split('\'')[0]]))
		    count += 1.
		    word = 'will'
		elif '\'ve' in word:
		    temp_vector = np.add(temp_vector,np.asarray(word_vec[word.split('\'')[0]]))
		    count += 1.
		    word = 'have'
		elif '\'re' in word:
		    temp_vector = np.add(temp_vector,np.asarray(word_vec[word.split('\'')[0]]))
		    count += 1.
		    word = 'are'
		elif '(' in word:
		    word = word.split('(')[1]
		elif ')' in word:
		    word = word.split(')')[0]
		elif '.'  in word:
		    for oneword in word.split('.'):
			if oneword and oneword in word_vec:
			    temp_vector = np.add(temp_vector,np.asarray(word_vec[oneword]))
			    count+=1.
		    continue
		elif ';' in word:
		    for oneword in word.split(';'):
			if oneword and oneword in word_vec:
			    temp_vector = np.add(temp_vector,np.asarray(word_vec[oneword]))
			    count+=1.
		    continue
		elif ':' in word:
		    for oneword in word.split(':'):
			if oneword and oneword in word_vec:
			    temp_vector = np.add(temp_vector,np.asarray(word_vec[oneword]))
			    count+=1.
		    continue
		elif '\'' in word:
		    for oneword in word.split('\''):
			if oneword and oneword in word_vec:
			    temp_vector = np.add(temp_vector,np.asarray(word_vec[oneword]))
			    count+=1.
		    continue
		elif '-'  in word:
		    for oneword in word.split('-'):
			if oneword and oneword in word_vec:
			    temp_vector = np.add(temp_vector,np.asarray(word_vec[oneword]))
			    count+=1.
		    continue
	    try:
		temp_vector = np.add(temp_vector,np.asarray(word_vec[word]))
	        count += 1.
	    except:
		print word
	if count == 0:
	    oneQ.append(temp_vector)
	else:
	    oneQ.append(np.divide(temp_vector,count))
    #print 'The shape of Q is '+str(np.shape(oneQ))
    #print 'The shape of one after is '+str(np.shape(one))
    # === TODO:  Insert each LABLE here to retain the order ===
    # onoQ.append(label in numpy array)
    data.append([np.hstack(oneQ),ans[idxCounter]])
    #data.append(np.hstack(tuple(oneQ)))
    idxCounter +=1

pdb.set_trace()
print "Pickling..."
fh =open(dataPickle_name,'wb')
pickle.dump(data,fh,pickle.HIGHEST_PROTOCOL)
fh.close()
#print 'The shape of All Data is '+str(np.shape(data))
