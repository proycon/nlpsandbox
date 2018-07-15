#!/usr/bin/env python3

import csv
import sys
from bs4 import BeautifulSoup
from pynlpl.formats import folia


for filename in sys.argv[1:]:
    with open(filename, 'r',encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            docid = "historischekranten_" + row['id'] + '_' + row['article_id'] + '_' + row['paper_id']
            print("Processing " + docid,file=sys.stderr)
            doc = folia.Document(id=docid)
            for key in ('id', 'article_id', 'article_title', 'paper_id', 'paper_title', 'date','article', 'err_text_type', 'colophon', 'colophon_text'):
                doc.metadata[key] = row[key]
            doc.declare(folia.Paragraph, "https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/nederlab-historischekranten-par.ttl")
            body = doc.append(folia.Text(doc, id=docid+".text"))
            div = body.append(folia.Division, id=docid+".div")
            if row['header'].strip():
                head = div.append(folia.Head, BeautifulSoup(row['header'].strip(),'lxml').text, id=docid+".text.head")
            if row['subheader'].strip():
                div.append(folia.Paragraph, BeautifulSoup(row['subheader'].strip(), 'lxml').text, id=docid+".text.subheader", cls="subheader")
            for i, partext in enumerate(row['article_text'].split('\n\n')):
                partext = BeautifulSoup(partext.replace("=\n","").replace("\n"," "), "lxml").text.strip()
                if partext:
                    paragraph = div.append(folia.Paragraph, partext, id=docid+".text.p." + str(i+1), cls="normal")
            doc.save(docid + ".folia.xml")



