# -*- coding: utf-8 -*-  
from sklearn.externals import joblib
from key_entity import key_entity_predictor

content = joblib.load("./data/content.pkl")
ids = joblib.load("./data/ids.pkl")
url = joblib.load("./data/url.pkl")
title = joblib.load("./data/title.pkl")

pred = key_entity_predictor()

for cnt in range(70000, 70005):
    text_content = content[cnt]
    text_title = title[cnt]
    text_id = ids[cnt]
    text_url = url[cnt]
    all_entities = pred.predict_all(text_title+" "+text_content)
    key_entities = pred.predict_key(text_title+" "+text_content)

    print "ID: ",text_id,"\n"
    print "Url: ",text_url,"\n"
    print"Title: ",text_title,"\n"
    print text_content,"\n"

    print "Key Entities: "
    for key, value in key_entities.iteritems():
        print key," ",value
    print "\n\n"

    print "Content All Entities: "
    for key, value in all_entities.iteritems():
        print key," ",value
    print "\n\n"




