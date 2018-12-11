from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext
import sys
import requests
import nltk
import time
from nltk.corpus import stopwords
import json

nltk.download('stopwords')
stopset = set(stopwords.words('english'))
stopset.update(("rt", "", "-", "like", "i’m", "i'm", "u", "&amp;", "#", "@"))

keywords = ["trump", 'flu', 'zika', "diarrhea", "ebola", "headache", "measles"]

global hour_tag
hour_tag = time.time()

def hour_passed(oldepoch):
    return time.time() - oldepoch >= 10 # change to hour


def update_hour_tag():
    hour_tag = time.time()

def aggregate_tag_counts(newvalues, totalsum):
    return sum(newvalues) + (totalsum or 0)


def get_sql_context_instance(spark_context):
    if 'sqlContextSingletonInstance' not in globals():
        globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)
    return globals()['sqlContextSingletonInstance']


def send_hdf_to_dashboard(df):
    # extract the hashtags from dataframe and convert them into array
    top_tags = [str(t.hashtag) for t in df.select("hashtag").collect()]
    # extract the counts from dataframe and convert them into array
    tags_count = [p.hashtag_count for p in df.select("hashtag_count").collect()]
    # initialize and send the data through REST API
    if hour_passed(hour_tag):
        update_hour_tag()
        url = 'http://localhost:5001/updateHashtagData'
        request_data = {'label': str(top_tags), 'data': str(tags_count)}
        with open('graph_values/hashtag_data.json', 'w') as outfile:
            json.dump(request_data, outfile)
            outfile.close()
        requests.post(url, data=request_data)


def send_wdf_to_dashboard(df):
    # extract the hashtags from dataframe and convert them into array
    top_words = [str(t.rel_word) for t in df.select("rel_word").collect()]
    # extract the counts from dataframe and convert them into array
    word_count = [p.word_count for p in df.select("word_count").collect()]
    # initialize and send the data through REST API
    if hour_passed(hour_tag):
        update_hour_tag()
        url = 'http://localhost:5001/updateWordData'
        request_data = {'label': str(top_words), 'data': str(word_count)}
        with open('graph_values/word_data.json', 'w') as outfile:
            json.dump(request_data, outfile)
            outfile.close()
        requests.post(url, data=request_data)


def send_udf_to_dashboard(df):
    # extract the hashtags from dataframe and convert them into array
    top_users = [str(t.user_name) for t in df.select("user_name").collect()]
    # extract the counts from dataframe and convert them into array
    user_count = [p.user_count for p in df.select("user_count").collect()]
    # initialize and send the data through REST API
    if hour_passed(hour_tag):
        update_hour_tag()
        url = 'http://localhost:5001/updateUserData'
        request_data = {'label': str(top_users), 'data': str(user_count)}
        with open('graph_values/user_data.json', 'w') as outfile:
            json.dump(request_data, outfile)
            outfile.close()
        requests.post(url, data=request_data)


def send_kdf_to_dashboard(df):
    # extract the hashtags from dataframe and convert them into array
    keywords = [str(t.keyword) for t in df.select("keyword").collect()]
    # extract the counts from dataframe and convert them into array
    keyword_count = [p.keyword_count for p in df.select("keyword_count").collect()]
    # initialize and send the data through REST API
    if hour_passed(hour_tag):
        update_hour_tag()
        url = 'http://localhost:5001/updateKeywordData'
        request_data = {'label': str(keywords), 'data': str(keyword_count)}
        with open('graph_values/keyword_data.json', 'w') as outfile:
            json.dump(request_data, outfile)
            outfile.close()
        requests.post(url, data=request_data)


def process_rdd_hashtag(time, rdd):
    try:
        # Get spark singleton context from the current context
        sql_context = get_sql_context_instance(rdd.context)
        # Convert RDD to RowRDD
        row_rdd = rdd.map(lambda w: Row(hashtag=w[0], hashtag_count=w[1]))
        # create a DF from the Row RDD
        df = sql_context.createDataFrame(row_rdd)
        # Register Dataframe as table
        df.registerTempTable("hashtags")
        # get the top 10 hashtags from the table using SQL and print them
        count_df = sql_context.sql("select hashtag, hashtag_count from hashtags order by hashtag_count desc limit 10")
        count_df.show()
        # call this method to prepare top 10 hashtags DF and send them
        send_hdf_to_dashboard(count_df)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


def process_rdd_rel_words(time, rdd):
    try:
        # Get spark singleton context from the current context
        sql_context = get_sql_context_instance(rdd.context)
        # Convert RDD to RowRDD
        row_rdd = rdd.map(lambda w: Row(rel_word=w[0], word_count=w[1]))
        # create a DF from the Row RDD
        df = sql_context.createDataFrame(row_rdd)
        # Register Dataframe as table
        df.registerTempTable("relevant_words")
        # get the top 10 hashtags from the table using SQL and print them
        count_df = sql_context.sql("select rel_word, word_count from relevant_words order by word_count desc limit 10")
        count_df.show()
        # call this method to prepare top 10 hashtags DF and send them
        send_wdf_to_dashboard(count_df)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


def process_rdd_user_names(time, rdd):
    try:
        # Get Spark singleton context form the current context
        sql_context = get_sql_context_instance(rdd.context)
        # Convert RDD to RowRDD
        row_rdd = rdd.map(lambda w: Row(user_name=w[0], user_count=w[1]))
        # create a DF from the row RDD
        df = sql_context.createDataFrame(row_rdd)
        # Register Dataframe as table
        df.registerTempTable("twitter_users")
        # Get the top 10 usersfrom thetable using SQL
        count_df = sql_context.sql("select user_name, user_count from twitter_users order by user_count desc limit 10")
        count_df.show()
        send_udf_to_dashboard(count_df)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


def process_rdd_keywords(time, rdd):
    try:
        # Get Spark singleton context form the current context
        sql_context = get_sql_context_instance(rdd.context)
        # Convert RDD to RowRDD
        row_rdd = rdd.map(lambda w: Row(keyword=w[0], keyword_count=w[1]))
        # create a DF from the row RDD
        df = sql_context.createDataFrame(row_rdd)
        # Register Dataframe as table
        df.registerTempTable("twitter_keywords")
        # Get the top 10 usersfrom the table using SQL
        count_df = sql_context.sql("select keyword, keyword_count from twitter_keywords order by keyword_count desc")
        count_df.show()
        send_kdf_to_dashboard(count_df)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


# create spark coniguration
conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark context with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# create a Streaming context from the above spark context with interval size of 2 seconds
ssc = StreamingContext(sc, 10)
# setting a checkpoint to allow RDD recovery
ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009
dataStream = ssc.socketTextStream("localhost", 9009)


user_names = dataStream.map(lambda line: line.split("|||", 1)[0] if "|||" in line else "NULL").filter(lambda word: word not in "NULL")
status = dataStream.map(lambda line: line.split("|||", 1)[1] if "|||" in line else line.split("|||")[0])

# split each tweet into words (one set for hashtags and another set for relevant words)
words = status.flatMap(lambda line: line.split(" "))
words_for_hashtag = status.flatMap(lambda line: line.split(" "))
keywords_list = status.flatMap(lambda line: line.split(" "))

# For Hashtags
# filter the words to get only hashtags, then map each hashtag to be a pair of (hashtag,1)
hashtags = words_for_hashtag.filter(lambda w: '#' in w).map(lambda x: (x, 1))
# adding the count of each hashtag to its last count
tags_total = hashtags.updateStateByKey(aggregate_tag_counts)

# For RelevantWords
rel_words = words.filter(lambda w: '#' not in w).filter(lambda w: '@' not in w)
relevant_words = rel_words.filter(lambda word: word.lower() not in stopset).map(lambda x: (x.lower(), 1))
# adding the count of each relevant word to its last count
rel_total = relevant_words.updateStateByKey(aggregate_tag_counts)

# For User_Names
user_names_map = user_names.map(lambda x: (x, 1))
user_names_total = user_names_map.updateStateByKey(aggregate_tag_counts)

# For keywords
keywords_map = keywords_list.filter(lambda word: word.lower() in keywords)
keywords_map = keywords_map.map(lambda x: (x.lower(), 1))
keywords_total = keywords_map.updateStateByKey(aggregate_tag_counts)

# Do processing for each RDD generated to its last count
tags_total.foreachRDD(process_rdd_hashtag)
rel_total.foreachRDD(process_rdd_rel_words)
user_names_total.foreachRDD(process_rdd_user_names)
keywords_total.foreachRDD(process_rdd_keywords)


# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
