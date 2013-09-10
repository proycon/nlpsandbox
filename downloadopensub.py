#!/usr/bin/env python3

import os

languages = ['af','ar','az','be','bg','bn','bs','ca','cs','da','de','el','en','es','et','eu','fa','fi','fr','gl','he','hi','hr','hu','id','is','it','ja','kk','ko','lt','lv','mk','ms','nb','nl','pl','pt','pt_br','ro','ru','si','sk','sl','sq','sr','sv','th','tr','uk','ur','vi','zh','zh_cn','zh_tw']

for i, lang in enumerate(languages):
    for j, lang2 in enumerate(languages):
        if i < j:
            os.system("wget http://opus.lingfil.uu.se/OpenSubtitles2012/" + lang + "-" + lang2 + ".txt.zip")


