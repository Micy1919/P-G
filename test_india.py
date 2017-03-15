# -*- coding: UTF-8 -*-
from sklearn.externals import joblib
from key_entity import key_entity_predictor

content = joblib.load("./data/IN_content.pkl")
ids = joblib.load("./data/IN_ids.pkl")
url = joblib.load("./data/IN_url.pkl")
title = joblib.load("./data/IN_title.pkl")

pred = key_entity_predictor()

IN_selected_all_entities = []
IN_selected_key_entities = []
IN_selected_title = []
IN_selected_content = []
IN_selected_url = []
IN_selected_id =[]

for cnt in range(60000, 60200):
    text_content = content[cnt]
    text_title = title[cnt]
    text_id = ids[cnt]
    text_url = url[cnt]
    all_entities = pred.predict_all(text_title+" "+text_content)
    key_entities = pred.predict_key(text_title+" "+text_content)

#    print "ID: ",text_id,"\n"
#    print "Url: ",text_url,"\n"
 #   print"Title: ",text_title,"\n"
 #   print text_content,"\n"

    key_entities_str = ""
    all_entities_str = ""

  #  print "Key entities:"
    for key,value in key_entities.iteritems():
        mark = True
        for i, c in enumerate(key):
            if c.encode('utf-8') == "Â":
               mark = False
               continue
        if mark == False:
           continue
        key_entities_str += key.encode('utf-8') +" "+str(value)+"  "
       # print key," ",value
    print "\n\n"

   # print " All Entities: "
    for key, value in all_entities.iteritems():
        mark = True
        for i, c in enumerate(key):
            #print c
            if c.encode('utf-8') == 'Â':
               mark = False
	    #print type('Â'), type(c), type(c.encode('utf-8'))
        #if  'Â'.encode('utf-8') in key:
        #    mark = False
        if mark == True:
           all_entities_str += key.encode('utf-8') + " " + str(value) +"  "
      #     print key," ",value
    print "\n"
#    print key_entities_str,"\n"
 #   print all_entities_str
    print "\n\n"

    IN_selected_id.append(text_id)
    IN_selected_url.append(text_url)
    IN_selected_all_entities.append(all_entities_str)
    IN_selected_key_entities.append(key_entities_str)
    IN_selected_title.append(text_title)   
    IN_selected_content.append(text_content)


joblib.dump(IN_selected_id, "./data/IN_selected_id.pkl")
joblib.dump(IN_selected_url, "./data/IN_selected_url.pkl")
joblib.dump(IN_selected_title, "./data/IN_selected_title.pkl")
joblib.dump(IN_selected_content, "./data/IN_selected_content.pkl")
joblib.dump(IN_selected_key_entities, "./data/IN_selected_key_entities.pkl")
joblib.dump(IN_selected_all_entities, "./data/IN_selected_all_entities.pkl")





