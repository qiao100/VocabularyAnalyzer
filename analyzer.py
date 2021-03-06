# -*- coding: utf-8 -*-

import sys
sys.path.append("utils")
from flask import request, render_template, Blueprint
import nlp
import requests, json
import collections, time
from collections import OrderedDict
import userlog


'''
Vocabulary Analyzer
'''
# 创建 Blueprint
bp_va = Blueprint("Vocabulary Analyzer", __name__)

# 提交文本的页面
@bp_va.route('/vocabulary_analyzer', methods=['GET'])
def submit():
	return render_template('va_submit.html')

# 处理数据并返回结果页面
@bp_va.route('/vocabulary_analyzer', methods=['POST'])
def processing():
	start_time = time.time()  # 计时起点
	# 读取词频表，注意要用list，保证次序（排名）
	with open("data/coca-20000.txt", 'r', encoding='utf-8') as fd:
		coca_word_list = fd.read().split()
	# 读取难词表
	with open("data/difficult-words.txt", 'r', encoding='utf-8') as fd:
		difficult_word_set = set(fd.read().split()) # 转换为 set 查找效率更高

	'''
	# 获取用户 IP 地址
	user_ip = request.remote_addr
	try:
		real_ip = request.headers["X-Real-IP"]
		if real_ip is not None:
			user_ip = real_ip
	except Exception as e:
		pass
	'''

	# 获取用户输入的文本
	text = request.form["text"]
	text = text[0:50000]

	'''
	# 保存日志
	userlog.save_log(user_ip, text)
	'''

	wordlist = nlp.nltk_word_tokenizer(text)
	lemmalist = nlp.nltk_word_lemmatizer(wordlist)
	result = collections.OrderedDict()
	for word in lemmalist:  # 对每一个待查词汇
		word = word.lower() # 防止大写影响查询
		if word in difficult_word_set:  # 如果它在高阶词典里
			try:
				index = coca_word_list.index(word)  # 查找coca排名
			except ValueError:  # coca不包含此单词
				index = 99999
			ranking = index + 1  # 下标加1为排名
			result[word] = ranking
	# 按照 value 排序
	result = OrderedDict(sorted(result.items(), key=lambda t: t[1]))
	# 组装 HTML Block
	content_block = ""
	for word, ranking in result.items():
		ranking = ranking if ranking != 100000 else "比较生僻"
		content_block += ("<tr><td>%s</td><td>%s</td></tr>" %(word, ranking))
	content_block = "<table border=\"1\">" + content_block + "</table>"

	text_wc = len(wordlist)
	result_wc = len(result)
	end_time = time.time()  # 计时终点
	elapsed_time = end_time-start_time
	content_block = ("<h5>输入词汇数: %d 个</h5>" %text_wc) \
	        + ("<h5>高阶词汇数: %d 个</h5>" %result_wc) \
	        + ("<h5>执行时间: %f 秒</h5>" %elapsed_time) \
	        + content_block
	return render_template('va_result.html',
	                       content_block=content_block)
