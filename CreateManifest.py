#!/usr/bin/python
import argparse
import os
import re


def makeArgs():
    parser = argparse.ArgumentParser(
        description="This script will create a mani file from a given directory of files with options to set the overall format", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-Input", required=True, nargs='+', help="Path to file/s or directory/ies")
    parser.add_argument("-multiple", action='store_true', help="This option allows mutiple file/directories for the Input option seperated by commas or with a *")
    parser.add_argument("-metaBuild", default=("_,1"), help="This option builds a meta tag from the file name. It takes two arguments the first being what to divide on and the second being which parts to take. If a single number is give it will take up to that part but if you want to select parts out of order put the ones desired seperate by commas. By default it splits the file by underbar and takes up to the first underbar.")
    parser.add_argument("-metaFile", help="A file containing a single column of meta tags. If no file or format given will take first part of filename up to the first underbar/score")
    parser.add_argument("-metaFormat", nargs='*', help="Meta tag format. This takes two arguemnts, tag format comma seperated ex. (barcode,lane) and a delimitor to seperate the values ex.(-). If no format or file given will take first part of filename up to the first underbar/score. To reference generated meta in this variable input meta into format")
    parser.add_argument("-order", default="file,lane,output,format,paired_end,meta", help="A list for the header order seperated by commas. Only restriction is format can't be last header in list")
    parser.add_argument("-metaCustom", help="A custom meta field")
    parser.add_argument("-fileType", help="Format of files ex. (fastq,fastqc). If variable formats in directory select -findType.")
    parser.add_argument("-findType", action='store_true', help="This option allows mutiple formats to occur in directory and will utlize the extension to determine the file format")
    parser.add_argument("-ProcessOutput", default="reads", help="Output of process that create files ex. (reads,fastqc)")
    parser.add_argument("-ucsc_db", default="hg38", help="UCSC reference assembly identifier")
    parser.add_argument("-pipeline", help="Pipeline used to create file")
    parser.add_argument("-ref_gene_set", help="Reference gene set")
    parser.add_argument("-outputFile",  help="Output file")
    parser.add_argument("-outputFileAdd", help="Output file to append new files.")
    return parser


if __name__ == "__main__":
    arguments = makeArgs()
    arguments = arguments.parse_args()
    Input = arguments.Input
    multiple = arguments.multiple
    metaBuild = arguments.metaBuild
    metaFile = arguments.metaFile
    metaFormat = arguments.metaFormat
    metaCustom = arguments.metaCustom
    order = arguments.order
    fileType = arguments.fileType
    findType = arguments.findType
    ProcessOutput = arguments.ProcessOutput
    ucsc_db = arguments.ucsc_db
    pipeline = arguments.pipeline
    ref_gene = arguments.ref_gene_set
    outputFile = arguments.outputFile
    addFile = arguments.outputFileAdd

File = False
Directory = False
MFile = False
MDirectory = False
order = order.lower()
headers = order.split(",")
if addFile:
    out = open(addFile, "a")
else:
    out = open(outputFile, "wb")
    out.write(order.replace(",", "\t")+"\n")


# This checks if the input is a single file/directory or multiple #
if multiple:
    if re.search(',', str(Input[0])):
        foo = Input[0].split(',')
        if os.path.isdir(foo[0]):
            MDirectory = True
        elif os.path.isfile(foo[0]):
            MFile = True
    elif type(Input) is list:
        inputs = Input[0]
        if os.path.isfile(inputs):
            MFile = True
        elif os.path.isdir(inputs):
            MDirectory = True
    else:
        print "Input neither file or directory"
        exit
else:
    if os.path.isfile(Input):
        File = True
    elif os.path.isdir(Input):
        Directory = True
    else:
        print "Input neither file or directory"
        exit


# This looks for the file type (format) by looking at the file extension #
def Typefinder(File):
    parts = File.split(".")
    ext = parts[-1]
    extType = {"bigwig": 'bigWig', "zip": "unknown",
               "abundance": "kallisto_abundance"}
#    extFancy=[fastqc,fastq,abundance]
    extSame = ['pdf', 'wig', 'html', 'fastq', 'fastqc',
               'bam', 'bam.bai', 'png', 'jpg', 'vcf']
    if ext in extType.keys():
        if str(ext) == "zip":
            if parts[-2] in extSame:
                fileType = str(parts[-2])
            else:
                fileType = extType[str(ext)]
        elif ext == "tsv":
            if parts[-2] in extType.keys():
                fileType = extType[str(parts[-2])]
            else:
                fileType = "text"
        else:
            fileType = extType[str(ext)]
    elif ext in extSame:
        fileType = ext
    else:
        fileType = "unknown"
    return fileType


# This builds a meta value from the filename based on a provided delimitor and an exlusive number of parts to include #
def buildMeta(File, sep):
    things = sep.split(',')
    div = things[0]
    if len(things) > 1:
        parts = things[1:]
        fileInfo = File.split(div)
        meta = ""
        for part in parts[:-1]:
            meta += fileInfo[int(part)]
            meta += '_'
        meta += fileInfo[int(parts[-1])]
    else:
        parts = int(things[1])
        fileInfo = File.split(div)
        meta = "_".join(fileInfo[:parts])
    return meta


# This takes in a file containing ordered meta tags and returns a list with them #
def grabMeta(meta):
    if os.path.isfile(meta):
        metaCol = []
        metafile = open(meta, "r")
        for lines in metafile:
            line = lines.strip("\n")
            if line == "meta":
                continue
            else:
                metaCol.append(line)
        return metaCol


# This creates a meta value based on a provided format which includes global and/or custom values and a seperator #
def getMeta(meta):
    if re.search(",", meta[0]):
        Format = meta[0].split(",")
        Values = []
        for val in Format:
            if val not in globals():
                Values.append(val)
            else:
                Values.append(globals()[val])
        if len(meta) > 1:
            metaFormat = meta[1].join(Values)
            return metaFormat
        else:
            metaFormat = "".join(Values)
            return metaFormat
    else:
        metaFormat = globals()[meta[0]]
        return metaFormat


# This searches for common values found in the file name such as read,lane and barcode #
def findCommonParts(File):
    Lanefound = re.search("_L([0-9]+)_", File)
    Readfound = re.search("_(R|I)([0-9])", File)
    Barcodefound = re.search("_([A-Z]{8}-[A-Z]{8})_", File)
    if Lanefound:
        lane = str(int(Lanefound.group(1)))
    else:
        if "lane" in headers:
            print "No lane in %s" % File
            exit
        lane = ""
    if Readfound:
        if Readfound.group(1) == "I":
            paired_end = ""
        elif Readfound.group(1) == "R":
            paired_end = Readfound.group(2)
    else:
        if "read" in headers:
            print "No read in filename"
            exit
        paired_end = ""
    if Barcodefound:
        barcode = Barcodefound.group(1)
    else:
        if "barcode" in headers:
            print "Barcodes not in filename %s" % File
        barcode = ""
    return lane, paired_end, barcode


# BigWig files have specific output values which this grabs based on parts of the filename #
def handleBigWig(File):
    strand = re.search("str(1|2)", File)
    multi = re.search("Multiple", File)
    if multi:
        if strand.group(1) == "1":
            output = "plus strand multi and unique map"
        elif strand.group(1) == "2":
            output = "minus strand multi and unique map"
        else:
            print "No strand in bigwig file name"
            exit
    else:
        if strand.group(1) == "1":
            output = "plus strand unique map"
        elif strand.group(1) == "2":
            output = "minus strand unique map"
        else:
            print "No strand in bigwig file name"
            exit
    return output


# This writes a manifest file with the data wanted in the order option #
def writeData(File, out, order, headers, lane, paired_end, barcode, meta, fileType, ProcessOutput, ucsc_db, pipeline, ref_gene_set):
    pairing = {"format": fileType, "reference_gene_set": ref_gene}
    for val in headers[:-1]:
        if val == "output":
            if fileType == "bigWig":
                output = handleBigWig(File)
                out.write("%s\t" % output)
            elif pipeline == "Picard":
                if fileType == "pdf":
                    out.write("RNACoveragePlot\t")
                else:
                    out.write("RNASeqQual\t")
            elif pipeline == "RSEM":
                if re.search("genes", File):
                    out.write("genes\t")
                elif re.search("isoforms", File):
                    out.write("isoforms\t")
            else:
                out.write("%s\t" % ProcessOutput)
        elif val in pairing.keys():
            out.write("%s\t" % pairing[val])
        elif val == "file":
            out.write("%s\t" % File)
        else:
            out.write("%s\t" % globals()[val])
    if headers[-1] == "output":
        if fileType == 'bigWig':
            output = handleBigWig(File)
            out.write("%s\n" % output)
        elif pipeline == "Picard":
            if fileType == "pdf":
                out.write("RNACoveragePlot\n")
            else:
                out.write("RNASeqQual\n")
        elif pipeline == "RSEM":
            if re.search("genes", File):
                out.write("genes\n")
            elif re.search("isoforms", File):
                out.write("isoforms\n")
        else:
            out.write("%s\n" % ProcessOutput)
    elif headers[-1] in pairing.keys():
        out.write("%s\n" % pairing[headers[-1]])
    else:
        out.write("%s\n" % globals()[headers[-1]])


# What to do if a single file #
if File:
    lane, read, barcode = findCommonParts(Input)
    if metaCustom:
        meta = metaCustom
    else:
        meta = buildMeta(Input, metaBuild)
    if metaFormat:
        meta = getMeta(metaFormat)
    elif metaFile:
        meta = grabMeta(metaFile)
        meta = meta[0]
    elif findType:
        fileType = Typefinder(Input)
    else:
        writeData(Input, out, order, headers, lane, read, barcode, meta, fileType, ProcessOutput, ucsc_db, pipeline, ref_gene)

# What to do if a single directory #
elif Directory:
    files = os.listdir(Input)
    sortedFiles = sorted(files)
    counter = 0
    for val in sortedFiles:
        lane, paired_end, barcode = findCommonParts(val)
        parts = metaBuild[0]
        div = metaBuild[1]
        file_path = Input+val
        if metaCustom:
            meta = metaCustom
        else:
            meta = buildMeta(val, parts, div)
        if metaFormat:
            meta = getMeta(metaFormat)
        elif metaFile:
            meta = grabMeta(metaFile)
            meta = meta[counter]
        elif findType:
            fileType = Typefinder(val)
        writeData(file_path, out, order, headers, lane, paired_end, barcode, meta, fileType, ProcessOutput, ucsc_db, pipeline, ref_gene)
        counter += 1

# What to do with mutiple files #
elif MFile:
    if re.search(',', str(Input[0])):
        Input = Input[0].split(',')
    for val in Input:
        parts = val.split('/')
        Fi = parts[-1]
        lane, paired_end, barcode = findCommonParts(Fi)
        if metaCustom:
            meta = metaCustom
        else:
            meta = buildMeta(Fi, metaBuild)
        if metaFormat:
            meta = getMeta(metaFormat)
        elif metaFile:
            meta = grabMeta(metaFile)
            meta = meta[0]
        elif findType:
            fileType = Typefinder(Fi)
        writeData(val, out, order, headers, lane, paired_end, barcode, meta, fileType, ProcessOutput, ucsc_db, pipeline, ref_gene)


# What to do with multiple directories #
elif MDirectory:
    if re.search(',', str(Input[0])):
        Input = Input[0].split(',')
    for thing in Input:
        files = os.listdir(thing)
        sortedFiles = sorted(files)
        counter = 0
        for val in sortedFiles:
            parts = val.split('/')
            Fi = parts[-1]
            lane, paired_end, barcode = findCommonParts(val)
            file_path = thing+val
            if metaCustom:
                meta = metaCustom
            else:
                meta = buildMeta(Fi, metaBuild)
            if metaFormat:
                meta = getMeta(metaFormat)
            elif metaFile:
                metalist = grabMeta(metaFile)
                print metalist
                meta = metalist[counter]
            elif findType:
                fileType = Typefinder(val)
            writeData(file_path, out, order, headers, lane, paired_end, barcode, meta, fileType, ProcessOutput, ucsc_db, pipeline, ref_gene)
            counter += 1

else:
    print "Things didn't work"
out.close()
