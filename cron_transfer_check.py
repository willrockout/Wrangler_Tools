#!/usr/bin/python

import datetime
import os
import re

salk = '/data/cirm/submit/neomorph.salk.edu/'
stanford = '/data/cirm/submit/stanford/Labs/'
email = 'wisulliv@uscsc.edu'
time = datetime.datetime.now()

# labs_salk = ['belmonte', 'bruneau', 'chi', 'crooks', 'fan', 'frazer', 'jones']
labs_salk = ['chi']


def getDirecs(path, labs):
    direcs = []
    lab_contents = os.listdir(path)
    for item in lab_contents:
        item_path = path + item
        for lab in labs:
            labCheck = re.search(lab, item.lower())
            if os.path.isdir(item_path):
                if labCheck:
                    direcs.append(item)
    return direcs


def getFiles(path, direcs, labs):
    lab_files = {}
    for direc in direcs:
        direc_path = path + direc
        # dp, dn, fn = os.walk(direc_path)
        for root, dirs, files in os.walk(direc_path):
            for File in files:
                if re.search('fastq', File):
                    for lab in labs:
                        if re.search(lab, direc.lower()):
                            lab_files[lab] = str(files)
    return lab_files


def fileNum(lab_files_dic):
    
    for key, val in lab_files_dic.items():
        return '%s : %s' % (key, len(val))


labfiles = getFiles(salk, getDirecs(salk, labs_salk), labs_salk)
print fileNum(labfiles)
# for val in labfiles.values():
#    print len(val)
