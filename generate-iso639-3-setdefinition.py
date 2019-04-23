#!/usr/bin/env python3
#Download input data manually from: https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3.tab

print("""@prefix fsd: <http://folia.science.ru.nl/setdefinition#> .
@prefix iso639_3: <http://folia.science.ru.nl/setdefinition/iso639_3#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

""")

data = {}
with open("iso-639-3.tab",'r',encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i>0:
            fields = line.split("\t")
            code = fields[0]
            name = fields[6]
            data[code] = name

print("iso639_3:Set a skos:Collection ;")
print("    skos:member")
for i, (code, name) in enumerate(data.items()):
    print(f"        iso639_3:{code}", end="")
    if i < len(data) - 1:
        print(",")
    else:
        print(";")
print("    skos:notation \"languagecodes\" .")
print()

for i, (code, name) in enumerate(data.items()):
    print(f"iso639_3:{code} a skos:Concept ;")
    print(f"    skos:notation \"{code}\" ;")
    print(f"    skos:prefLabel \"{name}\" .")
    print()



