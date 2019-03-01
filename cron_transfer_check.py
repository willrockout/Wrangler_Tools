#!/usr/bin/python

import datetime
import os
import re
import csv
import smtplib
from email.mime.text import MIMEText
# from collections import defaultdict

salk = '/data/cirm/submit/neomorph.salk.edu/'
stanford = '/data/cirm/submit/stanford/Labs/'
email = 'wisulliv@uscsc.edu'
Whattime = datetime.datetime.now()
labs_salk = ['belmonte', 'bruneau', 'chi', 'crooks', 'fan', 'frazer', 'jones']
labs_stanford = ['corn', 'geschwind', 'loring', 'sanford', 'snyder', 'weissman', 'wu', 'yeo']
will_labs = ['chi', 'crooks', 'sanford', 'loring']
chris_labs = ['corn', 'weissman', 'yeo', 'geschwind']
paris_labs = ['fan', 'frazer', 'jones', 'belmonte', 'bruneau', 'snyder', 'wu']


# This grabs the directories from a location
# that have provided lab names in there name
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


# This walks through a set of directories and returns a dictionary with info
# such as related lab, filetype, whether a file is a link or real and last
# the full path to the file
def getFiles(path, direcs, labs):
    lab_files = {}
    for lab in labs:
        for direc in direcs:
            direc_path = path + direc
            if re.search(lab, direc.lower()):
                if lab not in lab_files.keys():
                    lab_files[lab] = {}  # Look at presetting ditionary structure with lab_file = defaultdict(lamda:defaultdict(lamda:blahblahblah
                    for root, dirs, files in os.walk(direc_path):
                        for File in files:
                            if re.search('fastq\.gz', File):
                                if 'fastq' not in lab_files[lab].keys():
                                    gen_path = os.path.join(root, File)
                                    lab_files[lab]['fastq'] = {}
                                    if os.path.islink(gen_path):
                                        if 'S' not in lab_files[lab]['fastq'].keys():
                                            lab_files[lab]['fastq']['S'] = set()
                                            lab_files[lab]['fastq']['S'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['fastq']['S'].add(str(gen_path))
                                    else:
                                        if 'F' not in lab_files[lab]['fastq'].keys():
                                            lab_files[lab]['fastq']['F'] = set()
                                            lab_files[lab]['fastq']['F'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['fastq']['F'].add(str(gen_path))
                                else:
                                    gen_path = os.path.join(root, File)
                                    if os.path.islink(gen_path):
                                        if 'S' not in lab_files[lab]['fastq'].keys():
                                            lab_files[lab]['fastq']['S'] = set()
                                            lab_files[lab]['fastq']['S'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['fastq']['S'].add(str(gen_path))
                                    else:
                                        if 'F' not in lab_files[lab]['fastq'].keys():
                                            lab_files[lab]['fastq']['F'] = set()
                                            lab_files[lab]['fastq']['F'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['fastq']['F'].add(str(gen_path))
                            elif re.search('bcl\.gz', File):
                                if 'bcl' not in lab_files[lab].keys():
                                    gen_path = os.path.join(root, File)
                                    lab_files[lab]['bcl'] = {}
                                    if os.path.islink(gen_path):
                                        if 'S' not in lab_files[lab]['bcl'].keys():
                                            lab_files[lab]['bcl']['S'] = set()
                                            lab_files[lab]['bcl']['S'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['bcl']['S'].add(str(gen_path))
                                    else:
                                        if 'F' not in lab_files[lab]['bcl'].keys():
                                            lab_files[lab]['bcl']['F'] = set()
                                            lab_files[lab]['bcl']['F'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['bcl']['F'].add(str(gen_path))
                                else:
                                    gen_path = os.path.join(root, File)
                                    if os.path.islink(gen_path):
                                        if 'S' not in lab_files[lab]['bcl'].keys():
                                            lab_files[lab]['bcl']['S'] = set()
                                            lab_files[lab]['bcl']['S'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['bcl']['S'].add(str(gen_path))
                                    else:
                                        if 'F' not in lab_files[lab]['bcl'].keys():
                                            lab_files[lab]['bcl']['F'] = set()
                                            lab_files[lab]['bcl']['F'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['bcl']['F'].add(str(gen_path))
                                            
                else:
                    for root, dirs, files in os.walk(direc_path):
                        for File in files:
                            if re.search('fastq\.gz', File):
                                if 'fastq' not in lab_files[lab].keys():
                                    gen_path = os.path.join(root, File)
                                    lab_files[lab]['fastq'] = {}
                                    if os.path.islink(gen_path):
                                        if 'S' not in lab_files[lab]['fastq'].keys():
                                            lab_files[lab]['fastq']['S'] = set()
                                            lab_files[lab]['fastq']['S'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['fastq']['S'].add(str(gen_path))
                                    else:
                                        if 'F' not in lab_files[lab]['fastq'].keys():
                                            lab_files[lab]['fastq']['F'] = set()
                                            lab_files[lab]['fastq']['F'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['fastq']['F'].add(str(gen_path))
                                else:
                                    gen_path = os.path.join(root, File)
                                    if os.path.islink(gen_path):
                                        if 'S' not in lab_files[lab]['fastq'].keys():
                                            lab_files[lab]['fastq']['S'] = set()
                                            lab_files[lab]['fastq']['S'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['fastq']['S'].add(str(gen_path))
                                    else:
                                        if 'F' not in lab_files[lab]['fastq'].keys():
                                            lab_files[lab]['fastq']['F'] = set()
                                            lab_files[lab]['fastq']['F'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['fastq']['F'].add(str(gen_path))
                            elif re.search('bcl\.gz', File):
                                if 'bcl' not in lab_files[lab].keys():
                                    gen_path = os.path.join(root, File)
                                    lab_files[lab]['bcl'] = {}
                                    if os.path.islink(gen_path):
                                        if 'S' not in lab_files[lab]['bcl'].keys():
                                            lab_files[lab]['bcl']['S'] = set()
                                            lab_files[lab]['bcl']['S'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['bcl']['S'].add(str(gen_path))
                                    else:
                                        if 'F' not in lab_files[lab]['bcl'].keys():
                                            lab_files[lab]['bcl']['F'] = set()
                                            lab_files[lab]['bcl']['F'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['bcl']['F'].add(str(gen_path))
                                else:
                                    if os.path.islink(gen_path):
                                        if 'S' not in lab_files[lab]['bcl'].keys():
                                            lab_files[lab]['bcl']['S'] = set()
                                            lab_files[lab]['bcl']['S'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['bcl']['S'].add(str(gen_path))
                                    else:
                                        if 'F' not in lab_files[lab]['bcl'].keys():
                                            lab_files[lab]['bcl']['F'] = set()
                                            lab_files[lab]['bcl']['F'].add(str(gen_path))
                                        else:
                                            lab_files[lab]['bcl']['F'].add(str(gen_path))
    return lab_files


# This grabs the base location of files from the full path
def localGrab(new_file_dic, direc_pos):
    locations = {}
    for key in new_file_dic.keys():
        for val in new_file_dic[key].keys():
            for link in new_file_dic[key][val].keys():
                for File in new_file_dic[key][val][link]:
                    file_break = File.split('/')
                    main_direc = file_break[direc_pos]
                    if key not in locations.keys():
                        locations[key] = {}
                        if val not in locations[key].keys():
                            locations[key][val] = {}
                            if link not in locations[key][val].keys():
                                locations[key][val][link] = set()
                                locations[key][val][link].add(main_direc)
                            else:
                                locations[key][val][link].add(main_direc)
                        else:
                            if link not in locations[key][val].keys():
                                locations[key][val][link] = set()
                                locations[key][val][link].add(main_direc)
                            else:
                                locations[key][val][link].add(main_direc)
                    else:
                        if val not in locations[key].keys():
                            locations[key][val] = {}
                            if link not in locations[key][val].keys():
                                locations[key][val][link] = set()
                                locations[key][val][link].add(main_direc)
                            else:
                                locations[key][val][link].add(main_direc)
                        else:
                            if link not in locations[key][val].keys():
                                locations[key][val][link] = set()
                                locations[key][val][link].add(main_direc)
                            else:
                                locations[key][val][link].add(main_direc)
    return locations


# This takes a directory of files and locations and makes a list of clean
# outputs for each lab, filetype, link type and file
def fileNum(lab_files_dic, locations):
    lab_file_counts = []
    for lab, filetype in lab_files_dic.items():
        for filetype in lab_files_dic[lab].keys():
            for link in lab_files_dic[lab][filetype].keys():
                if link == 'S':
                    lab_file_counts.append('%s: %s %s/s submitted in %s' % (lab, len(lab_files_dic[lab][filetype][link]), filetype, locations[lab][filetype][link]))
                elif link == 'F':
                    lab_file_counts.append('%s: %s %s/s added in %s' % (lab, len(lab_files_dic[lab][filetype][link]), filetype, locations[lab][filetype][link]))
    return lab_file_counts


# This writes a directory to a tsv file with the current time in the name
def writeCurrent(currentFD, path):
    with open('%s.will_log/.new_fileCheck_%s.txt' % (path, Whattime), 'wb') as test:
        csvwriter = csv.writer(test, delimiter='\t')
        csvwriter.writerow(['#lab', 'filetype', 'link', 'filename'])
        for lab in currentFD:
            for filetype in currentFD[lab]:
                for link in currentFD[lab][filetype]:
                    for File in currentFD[lab][filetype][link]:
                        csvwriter.writerow([lab, filetype, File, link])


# This reads a tab seperated file and places it into a dictionary to compare
def readPrevious(oldfile):
    prev_dict = {}
    with open(oldfile, 'rb') as old:
        for lines in old:
            line = lines.strip()
            if line[0] != '#':
                (key, val, dval, tval) = line.split('\t')
                if key not in prev_dict.keys():
                    prev_dict[key] = {}
                    if val not in prev_dict[key].keys():
                        prev_dict[key][val] = {}
                        if tval not in prev_dict[key][val].keys():
                            prev_dict[key][val][tval] = set()
                            prev_dict[key][val][tval].add(dval)
                        else:
                            prev_dict[key][val][tval].add(dval)
                    else:
                        if tval not in prev_dict[key][val].keys():
                            prev_dict[key][val][tval] = set()
                            prev_dict[key][val][tval].add(dval)
                        else:
                            prev_dict[key][val][tval].add(dval)
                else:
                    if val not in prev_dict[key].keys():
                        prev_dict[key][val] = {}
                        if tval not in prev_dict[key][val].keys():
                            prev_dict[key][val][tval] = set()
                            prev_dict[key][val][tval].add(dval)
                        else:
                            prev_dict[key][val][tval].add(dval)
                    else:
                        if tval not in prev_dict[key][val].keys():
                            prev_dict[key][val][tval] = set()
                            prev_dict[key][val][tval].add(dval)
                        else:
                            prev_dict[key][val][tval].add(dval)
    return prev_dict


# This compares two dictionaries and returns a dictionary or varying files
def cmpDict(old, new):
    new_files = {}
    for key in new.keys():
        for val in new[key].keys():
            for link in new[key][val].keys():
                for File in new[key][val][link]:
                    if File not in old[key][val][link]:
                        if key not in new_files.keys():
                            new_files[key] = {}
                            if val not in new_files[key].keys():
                                new_files[key][val] = {}
                                if link not in new_files[key][val].keys():
                                    new_files[key][val][link] = set()
                                    new_files[key][val][link].add(File)
                                else:
                                    new_files[key][val][link].add(File)
                            else:
                                if link not in new_files[key][val].keys():
                                    new_files[key][val][link] = set()
                                    new_files[key][val][link].add(File)
                                else:
                                    new_files[key][val][link].add(File)
                        else:
                            if val not in new_files[key].keys():
                                new_files[key][val] = {}
                                if link not in new_files[key][val].keys():
                                    new_files[key][val][link] = set()
                                    new_files[key][val][link].add(File)
                                else:
                                    new_files[key][val][link].add(File)
                            else:
                                if link not in new_files[key][val].keys():
                                    new_files[key][val][link] = set()
                                    new_files[key][val][link].add(File)
                                else:
                                    new_files[key][val][link].add(File)
                    else:
                        pass
    return new_files


def rename(path):
    for File in os.listdir('%s.will_log' % path):
        if re.search('old', File):
            name_change = str(File).replace('old_fileCheck', 'older_file_check')
            os.rename('%s.will_log/%s' % (path, File), '%s.will_log/%s' % (path, name_change))
        elif re.search('new', File):
            name_change = str(File).replace('new', 'old')
            os.rename('%s.will_log/%s' % (path, File), '%s.will_log/%s' % (path, name_change))


def Compare(path, current, Sumlist, direc_pos):
    for File in os.listdir('%s.will_log' % path):
        if re.search('old_fileCheck', File):
            old = readPrevious('%s.will_log/%s' % (path, File))
            compared = cmpDict(old, current)
            summary = fileNum(compared, localGrab(compared, direc_pos))
            if summary:
                Sumlist.append(summary)


SClabfiles = getFiles(salk, getDirecs(salk, labs_salk), labs_salk)
NClabfiles = getFiles(stanford, getDirecs(stanford, labs_stanford), labs_stanford)
rename(salk)
rename(stanford)
writeCurrent(SClabfiles, salk)
writeCurrent(NClabfiles, stanford)
summary = []
Compare(salk, SClabfiles, summary, 5)
Compare(stanford, NClabfiles, summary, 5)

# for File in os.listdir('%s.will_log' % salk):
#     if re.search('old_fileCheck', File):
#         old = readPrevious('%s.will_log/%s' % (salk, File))
#         compared = cmpDict(old, labfiles)
#         summary = fileNum(compared, localGrab(compared))
# #        print fileNum(compared, localGrab(compared))


# Below is writing the email with above info

if summary:
    sum_info = open('/data/home/willrockout/.will_cron_log/.summary_%s.txt' % Whattime, 'wb')
    for item in summary:
        sum_info.write('%s\n' % item)
    sum_info.close()
    with open('/data/home/willrockout/.will_cron_log/.summary_%s.txt' % Whattime, 'rb') as fp:
        msg = MIMEText(fp.read())
    fromaddr = 'cron_file_test@ucsc.edu'
    toaddr = ['wisulliv@ucsc.edu', 'pnejad@ucsc.edu', 'cjvillar@ucsc.edu', 'clayfischer@ucsc.edu']
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Subject'] = 'Files transfered from Salk and Stanford'
    text = msg.as_string()
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login('wisulliv@ucsc.edu', 'fexpovuwyolkgdra')
    smtpObj.sendmail(fromaddr, toaddr, text)
    smtpObj.quit()
