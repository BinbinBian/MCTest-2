import numpy as np

#for lstm input 
#the label is a 4 dim vector like for ans=B it is [0 1 0 0]
def mk_all(data):
	data_num = len(data)
	word_dim = len(data[0][0][0][0])
	print "This is make lstm with ans = 4 dim"
	print "Total data: %d\nWord dim:  %d\n" % (data_num, word_dim)

	label_size = len(data[0][1])
	#data[0][0] contains P,Q,A1,A2,A3,A4
	#data[0][1] contains label
	#data[0][0][0] contains P is a list of words
	#data[0][0][0][0] is word's np vector dim=300

	data_shuf = []
	label_shuf = np.zeros((data_num, label_size))
	for i in range(data_num):
		oneline=[]
		for j in range(len(data[i][0])):
			oneline=oneline+data[i][0][j]
		data_shuf.append(oneline)
		label_shuf[i, ] = data[i][1]
	return data_shuf, label_shuf

# for gru input
# the label is a 300 dim vector which is the average of all the words in the answer's sentence
# return each P and Q and Each Answer
def mk_newgru300(data):
	data_num = len(data)
	word_dim = len(data[0][0][0][0])
	print "This is make gru 300\n"
	print "Total data: %d\nWord dim:  %d\n" % (data_num, word_dim)

	label_size = len(data[0][1])
	#data[0][0] contains P,Q,A1,A2,A3,A4
	#data[0][1] contains label
	#data[0][0][0] contains P is a list of words
	#data[0][0][0][0] is word's np vector dim=300

	passage = []
	questions =[]
	A1 = []
	A2 = []
	A3 = []
	A4 = []
	true_ans = np.zeros((data_num, label_size),dtype='float32')
	for i in range(data_num):
		oneline=[]
		oneline = oneline +data[i][0][0]
		passage.append(oneline)
		onequestion=[]
		onequestion = onequestion +data[i][0][1]
		questions.append(onequestion)
		#print "Each len is "+ str(len(data_shuf[i]))
		index = np.nonzero(data[i][1])[0]+2
		index = int(index)
		#checkshape = 1
		#if index.ndim != checkshape:
		#	print "Data %d failed\n" % (i)
		# calculate the answer (average all its words)
		true_ans[i, ] = data[i][1]
		
		oneA1 = []
		oneA1 = oneA1 + data[i][0][2]
		A1.append(oneA1)
		oneA2 = []
		oneA2 = oneA2 + data[i][0][3]
		A2.append(oneA2)
		oneA3 = []
		oneA3 = oneA3 + data[i][0][4]
		A3.append(oneA3)
		oneA4 = []
		oneA4 = oneA4 + data[i][0][5]
		A4.append(oneA4)


	return passage, questions, A1, A2, A3, A4, true_ans

# for gru input
# the label is a 300 dim vector which is the average of all the words in the answer's sentence
# return each P and Q and Each Answer
def mk_gru300(data):
	data_num = len(data)
	word_dim = len(data[0][0][0][0])
	print "This is make gru 300\n"
	print "Total data: %d\nWord dim:  %d\n" % (data_num, word_dim)

	label_size = len(data[0][1])
	#data[0][0] contains P,Q,A1,A2,A3,A4
	#data[0][1] contains label
	#data[0][0][0] contains P is a list of words
	#data[0][0][0][0] is word's np vector dim=300

	passage = []
	questions =[]
	A1 = np.zeros((data_num, word_dim),dtype='float32')
	A2 = np.zeros((data_num, word_dim),dtype='float32')
	A3 = np.zeros((data_num, word_dim),dtype='float32')
	A4 = np.zeros((data_num, word_dim),dtype='float32')
	true_ans = np.zeros((data_num, label_size),dtype='float32')
	for i in range(data_num):
		oneline=[]
		oneline = oneline +data[i][0][0]
		passage.append(oneline)
		onequestion=[]
		onequestion = onequestion +data[i][0][1]
		questions.append(onequestion)
		#print "Each len is "+ str(len(data_shuf[i]))
		index = np.nonzero(data[i][1])[0]+2
		index = int(index)
		#checkshape = 1
		#if index.ndim != checkshape:
		#	print "Data %d failed\n" % (i)
		# calculate the answer (average all its words)
		true_ans[i, ] = data[i][1]
	
		a1_sum = np.zeros(word_dim,dtype='float32')
		for ans_word in data[i][0][2]:
			a1_sum = a1_sum + ans_word
		A1[i, ] = a1_sum/len(data[i][0][2])

		a2_sum = np.zeros(word_dim,dtype='float32')
		for ans_word in data[i][0][3]:
			a2_sum = a2_sum + ans_word
		A2[i, ] = a2_sum/len(data[i][0][3])

		a3_sum = np.zeros(word_dim,dtype='float32')
		for ans_word in data[i][0][4]:
			a3_sum = a3_sum + ans_word
		A3[i, ] = a3_sum/len(data[i][0][4])

		a4_sum = np.zeros(word_dim,dtype='float32')
		for ans_word in data[i][0][5]:
			a4_sum = a4_sum + ans_word
		A4[i, ] = a4_sum/len(data[i][0][5])

	print "Final len is "+str(len(passage))
	return passage, questions, A1, A2, A3, A4, true_ans

# for lstm input
# the label is a 300 dim vector which is the average of all the words in the answer's sentence
# the data contain P and Q words
def mk_all300(data):
	data_num = len(data)
	word_dim = len(data[0][0][0][0])
	print "This is make lstm 300\n"
	print "Total data: %d\nWord dim:  %d\n" % (data_num, word_dim)

	label_size = len(data[0][1])
	#data[0][0] contains P,Q,A1,A2,A3,A4
	#data[0][1] contains label
	#data[0][0][0] contains P is a list of words
	#data[0][0][0][0] is word's np vector dim=300

	data_shuf = []
	label_shuf = np.zeros((data_num, word_dim),dtype='float32')
	for i in range(data_num):
		oneline=[]
		for j in range(2):
			oneline = oneline +data[i][0][j]
		data_shuf.append(oneline)
		index = np.nonzero(data[i][1])[0]+2
		checkshape = 1
		if index.ndim != checkshape:
			print "Data %d failed\n" % (i)
		ans_sum = np.zeros(word_dim,dtype='float32')
		for ans_word in data[i][0][index]:
			ans_sum = ans_sum + ans_word
		label_shuf[i, ] = ans_sum/len(data[i][0][index])
	return data_shuf, label_shuf

def mk_batch(data, batch_size, shuffle=True):
	data_num = len(data)
	data_size = len(data[0][0])
	print "Total data: %d\nData size:  %d\n" % (data_num, data_size)
	n_batch = data_num/batch_size
	n_left_data = data_num % batch_size
	if(n_left_data != 0):
		n_batch += 1
	batch_data = np.zeros((n_batch, batch_size, data_size))

	label_size = len(data[0][1])
	batch_label = np.zeros((n_batch, batch_size, label_size))

	data_shuf = np.zeros((data_num, data_size))
	label_shuf = np.zeros((data_num, label_size))
	for i in range(data_num):
		data_shuf[i, ] = data[i][0] 
		label_shuf[i, ] = data[i][1]
	if(shuffle):
		idx_shuffle = np.arange(data_num)
		np.random.shuffle(idx_shuffle)
		i=0
		for i_shuf in idx_shuffle:
			data_shuf[i, :] = data[i_shuf][0]
			label_shuf[i] = data[i_shuf][1]
			i+=1

	# bad implementation, need modification...
	if(n_left_data != 0):
		for i in range(batch_size - n_left_data):
			data_shuf = np.concatenate((data_shuf, np.asarray([data_shuf[i]])))
			label_shuf = np.concatenate((label_shuf, np.asarray([label_shuf[i]])))

	for i in range(n_batch):
		batch_data_matrix = np.zeros((batch_size, data_size))
		batch_label_matrix = np.zeros((batch_size, label_size))
		for j in range(batch_size):
			idx = j + i * batch_size
			batch_data_matrix[j, :] = data_shuf[idx]
			batch_label_matrix[j, :] = label_shuf[idx]
		batch_data[i, :] = batch_data_matrix
		batch_label[i, :] = batch_label_matrix
		del batch_data_matrix
		del batch_label_matrix
	return batch_data, batch_label


if __name__ == "__main_":
	pass
