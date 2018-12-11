from flask import Flask,jsonify,request
from flask import render_template
import ast
import json

app = Flask(__name__)
hashtag_labels = []
hashtag_values = []
word_labels = []
word_values = []
user_labels = []
user_values = []
keyword_labels = []
keyword_values = []


@app.route("/")
def get_chart_page():
	global labels, values
	labels = []
	values = []
	return render_template('chart.html', hashtag_values=hashtag_values, hashtag_labels=hashtag_labels, word_values=word_values, word_labels=word_labels, user_values=user_values, user_labels=user_labels, keyword_labels=keyword_labels, keyword_values=keyword_values)


@app.route('/refreshHashtagData')
def refresh_hashtag_graph_data():
	global hashtag_labels, hashtag_values
	if hashtag_labels == [] or hashtag_values == []:
		with open('graph_values/hashtag_data.json', "r") as f:
			data = json.load(f)
		hashtag_labels = ast.literal_eval(data['label'])
		hashtag_values = ast.literal_eval(data['data'])
	return jsonify(hLabel=hashtag_labels, hData=hashtag_values)


@app.route('/refreshWordData')
def refresh_word_graph_data():
	global word_labels, word_values
	if word_labels == [] or word_values == []:
		with open('graph_values/word_data.json', "r") as f:
			data = json.load(f)
		word_labels = ast.literal_eval(data['label'])
		word_values = ast.literal_eval(data['data'])
	return jsonify(wLabel=word_labels, wData=word_values)


@app.route('/refreshUserData')
def refresh_user_graph_data():
	global user_labels, user_values
	if user_labels == [] or user_values == []:
		with open('graph_values/user_data.json', "r") as f:
			data = json.load(f)
		user_labels = ast.literal_eval(data['label'])
		user_values = ast.literal_eval(data['data'])
	return jsonify(uLabel=user_labels, uData=user_values)


@app.route('/refreshKeywordData')
def refresh_keyword_graph_data():
	global keyword_labels, keyword_values
	if keyword_labels == [] or keyword_values == []:
		with open('graph_values/keyword_data.json', "r") as f:
			data = json.load(f)
		keyword_labels = ast.literal_eval(data['label'])
		keyword_values = ast.literal_eval(data['data'])
	return jsonify(kLabel=keyword_labels, kData=keyword_values)


@app.route('/updateHashtagData', methods=['POST'])
def update_hashtag_data():
	global hashtag_labels, hashtag_values
	if not request.form or 'data' not in request.form:
		return "error", 400
	hashtag_labels = ast.literal_eval(request.form['label'])
	hashtag_values = ast.literal_eval(request.form['data'])
	return "success", 201


@app.route('/updateWordData', methods=['POST'])
def update_word_data():
	global word_labels, word_values
	if not request.form or 'data' not in request.form:
		return "error", 400
	word_labels = ast.literal_eval(request.form['label'])
	word_values = ast.literal_eval(request.form['data'])
	return "success", 201

@app.route('/updateUserData', methods=['POST'])
def update_user_data():
	global user_labels, user_values
	if not request.form or 'data' not in request.form:
		return "error", 400
	user_labels = ast.literal_eval(request.form['label'])
	user_values = ast.literal_eval(request.form['data'])
	return "success", 201

@app.route('/updateKeywordData', methods=['POST'])
def update_keyword_data():
	global keyword_labels, keyword_values
	# if not request.form:
	# 	with open('graph_values/keyword_data.json', "r") as f:
	# 		data = json.load(f)
	# 	keyword_labels = data['label']
	# 	keyword_values = data['data']
	# elif 'data' not in request.form:
	# 	return "error", 400
	if not request.form or 'data' not in request.form:
		return "error", 400
	else:
		keyword_labels = ast.literal_eval(request.form['label'])
		keyword_values = ast.literal_eval(request.form['data'])
	return "success", 201


if __name__ == "__main__":
	app.run(host='localhost', port=5001)

