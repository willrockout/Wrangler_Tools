#!/usr/bin/python

import datetime
import os
import re

salk = '/data/cirm/submit/neomorph.salk.edu/'
stanford = '/data/cirm/submit/stanford/Labs/'
email = 'wisulliv@uscsc.edu'
Whattime = datetime.datetime.now()
# labs_salk = ['belmonte', 'bruneau', 'chi', 'crooks', 'fan', 'frazer', 'jones']
labs_salk = ['chi']
# labs_salk = ['chi', 'crooks']


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
    file_location = {}
    for lab in labs:
        for direc in direcs:
            direc_path = path + direc
            if re.search(lab, direc.lower()):
                if lab not in file_location.keys():
                    file_location[lab] = []
                    file_location[lab].append(direc_path)
                else:
                    file_location[lab].append(direc_path)
                if lab not in lab_files.keys():
                    lab_files[lab] = {}
                    for root, dirs, files in os.walk(direc_path):
                        for File in files:
                            if re.search('fastq.gz', File):
                                if 'fastq' not in lab_files.get(lab, {}):
                                    lab_files[lab]['fastq'] = []
                                    lab_files[lab]['fastq'].append(str(File))
                                else:
                                    lab_files[lab]['fastq'].append(str(File))
                            elif re.search('bcl.gz', File):
                                if 'bcl' not in lab_files.get(lab, {}):
                                    lab_files[lab]['bcl'] = []
                                    lab_files[lab]['bcl'].append(str(File))
                                else:
                                    lab_files[lab]['bcl'].append(str(File))
                else:
                    for root, dirs, files in os.walk(direc_path):
                        for File in files:
                            if re.search('fastq.gz', File):
                                if 'fastq' not in lab_files.get(lab, {}):
                                    lab_files[lab]['fastq'] = []
                                    lab_files[lab]['fastq'].append(str(File))
                                else:
                                    lab_files[lab]['fastq'].append(str(File))
                            elif re.search('bcl.gz', File):
                                if 'bcl' not in lab_files.get(lab, {}):
                                    lab_files[lab]['bcl'] = []
                                    lab_files[lab]['bcl'].append(str(File))
                                else:
                                    lab_files[lab]['bcl'].append(str(File))
    return lab_files


def fileNum(lab_files_dic):
    lab_file_counts = []
    for lab, filetype in lab_files_dic.items():
        for filetype in lab_files_dic[lab].keys():
            lab_file_counts.append('%s: %s %s files' % (lab, len(lab_files_dic[lab][filetype]), filetype))
    return lab_file_counts


labfiles = getFiles(salk, getDirecs(salk, labs_salk), labs_salk)
for item in fileNum(labfiles):
    print item
# print fileNum(labfiles)
# for val in labfiles.values():
#    print len(val)
