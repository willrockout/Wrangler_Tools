#!/usr/bin/env python

import datetime
import os
import re
import csv
import smtplib
from collections import defaultdict
from email.mime.text import MIMEText


class TransferCheck:
    def __init__(self):
        self.Whattime = datetime.datetime.now
        self.salk = '/data/cirm/submit/neomorph.salk.edu/'
        self.stanford = '/data/cirm/submit/stanford/Labs/'
        self.salk_labs = ['belmonte', 'bruneau', 'chi', 'crooks', 'fan',
                          'frazer', 'jones']
        self.stanford_labs = ['corn', 'geschwind', 'loring', 'sanford',
                              'snyder', 'weissman', 'wu', 'yeo']

    def getDirecs(self):
        direcs = []
        salk_direcs = os.listdir(self.salk)
        stanford_direcs = os.listdir(self.stanford)
        labs = self.salk_labs + self.stanford_labs
        for salk_f, stan_f in map(None, salk_direcs, stanford_direcs):
            salk_full = self.salk + str(salk_f)
            stan_full = self.stanford + str(stan_f)
            for lab in labs:
                if re.search(lab, str(salk_f).lower()):
                    if os.path.isdir(salk_full):
                        direcs.append(salk_full)
                    else:
                        continue
                if re.search(lab, str(stan_f).lower()):
                    if os.path.isdir(stan_full):
                        direcs.append(stan_full)
                    else:
                        continue
        return direcs

    def getFiles(self, direcs):
        lab_files = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        labs = self.salk_labs + self.stanford_labs
        for lab in labs:
            for direc in direcs:
                for root, dirs, files in os.walk(direc):
                    for File in files:
                        if re.search('fastq\.gz', File):
                            gen_path = os.path.join(root,File)
                            if os.path.islink(gen_path):
                                lab_files[lab]['fastq']['S'].add(str(gen_path))
                            else:
                                lab_files[lab]['fastq']['F'].add(str(gen_path))
                        else:
                            continue
        return lab_files

    def writeCurrent(self, lab_files):
        overview_direcs = [self.salk, self.stanford]
        for path in overview_direcs:
            with open('%s.will_log/.new_fileCheck_%s.txt' % (path, self.Whattime), 'wb') as log:
                csvwriter = csv.writer(log, delimiter='\t')
                csvwriter.writerow(['#lab', 'filetype', 'link', 'filename'])
                for lab in lab_files:
                    for filetype in lab_files[lab]:
                        for link in lab_files[lab][filetype]:
                            for File in lab_files[lab][filetype][link]:
                                csvwriter.writerow([lab, filetype, File, link])

    def readPrevious(self, old_file):
        old_files = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        with open(old_file, 'rb') as old:
            for lines in old:
                line = lines.strip()
                if line[0] != '#':
                    (lab, filetype, link, filename) = line.split('\t')
                    old_files[lab][filetype][link] = filename
        return old_files


    def cmpDict(old, new):
        new_files = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        for key in new.keys():
            for val in new[key].keys():
                for link in new[key][val].keys():
                    for File in new[key][val][link]:
                        if File not in old[key][val][link]:
                            new_files[key][val][link].add(File)
                        else:
                            pass
        return new_files


    def rename(self):
        centers = [self.salk, self.stanford]
        for center in centers:
            for File in os.listdir('%s.will_log' % center):
                if re.search('old', File):
                    name_change = str(File).replace('old_fileCheck', 'older_file_check')
                    os.rename('%s.will_log/%s' % (center, File), '%s.will_log/%s' % (center, name_change))
                elif re.search('new', File):
                    name_change = str(File).replace('new', 'old')
                    os.rename('%s.will_log/%s' % (center, File), '%s.will_log/%s' % (center, name_change))


    def Compare(self, current, ):


        
if __name__ == '__main__':

    Transfer = TransferCheck()

    Direcs = Transfer.getDirecs()

    test = ['/data/cirm/submit/neomorph.salk.edu/DCM_ChiGroup']
    
    Files = Transfer.getFiles(test)

    Transfer.writeCurrent(Files)

    old_read = '/data/cirm/submit/neomorph.salk.edu/.will_log/.new_fileCheck_2018-08-31 02:00:01.293254.txt'

    previous = Transfer.readPrevious(old_read)
    
    
