import argparse
import os
import re

def multi(args):
    if re.search(',', str(args.Input[0])):
        foo = args.Input[0].split(',')
        if os.path.isdir(foo[0]):
            return "MDirectory"
        elif os.path.isfile(foo[0]):
            return "MFile"
    elif type(args.Input) is list:
        if os.path.isfile(args.Input[0]):
            return "MFile"
        elif os.path.isdir(args.Input[0]):
            return "MDirectory"
        else:
            return "Input neither file or directory"
    else:
        if os.path.isfile(args.Inputs):
            return "File"
        elif os.path.isdir(args.Inputs):
            return "Directory"
        else:
            return "Input neither file or directory"


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
def findCommonParts(File, args):
    lanefound = re.search("_L([0-9]+)_", File)
    readfound = re.search("_(R|I)([0-9])", File)
    barcodefound = re.search("_([A-Z]{8}-[A-Z]{8})_", File)
    if lanefound:
        lane = str(int(lanefound.group(1)))
    else:
        if "lane" in args.order.split():
            print("No lane in %s" % File)
            exit()
        lane = ""
    if readfound:
        if readfound.group(1) == "I":
            paired_end = ""
        elif readfound.group(1) == "R":
            paired_end = readfound.group(2)
        else:
            paired_end = ""
    else:
        if "read" in args.order.split():
            print("No read in filename")
            exit()
        paired_end = ""
    if barcodefound:
        barcode = barcodefound.group(1)
    else:
        if "barcode" in args.order.split():
            print("Barcode not in filename %s" % File)
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
            print("No strand in bigwig file name")
            exit()
    else:
        if strand.group(1) == "1":
            output = "plus strand unique map"
        elif strand.group(1) == "2":
            output = "minus strand unique map"
        else:
            print("No strand in bigwig file name")
            exit()
    return output


# This writes a manifest file with the data wanted in the order option #
def writeData(File, out, order, headers, lane, paired_end, barcode, meta, fileType, ProcessOutput, ucsc_db, pipeline, ref_gene_set):
    pairing = {"format": fileType, "reference_gene_set": ref_gene_set}
    for header in headers[:-1]:
        if header == "output":
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
        elif header in pairing.keys():
            out.write("%s\t" % pairing[header])
        elif header == "file":
            out.write("%s\t" % File)
        else:
            out.write("%s\t" % globals()[header])
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script will create a mani file from a given directory of files with options to set the overall format", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-Input", required=True, nargs='+', help="Path to file/s or directory/ies")
    parser.add_argument("-multiple", action='store_true', help="This option allows multiple file/directories for the Input option separated by commas or with a *")
    parser.add_argument("-metaBuild", default="_,1", help="This option builds a meta tag from the file name. It takes two arguments the first being what to divide on and the second being which parts to take. If a single number is give it will take up to that part but if you want to select parts out of order put the ones desired separate by commas. By default it splits the file by under-bar and takes up to the first under-bar.")
    parser.add_argument("-metaFile", help="A file containing a single column of meta tags. If no file or format given will take first part of filename up to the first under-bar/score")
    parser.add_argument("-metaFormat", nargs='*', help="Meta tag format. This takes two arguments, tag format comma separated ex. (barcode,lane) and a delimiter to separate the values ex.(-). If no format or file given will take first part of filename up to the first under-bar/score. To reference generated meta in this variable input meta into format")
    parser.add_argument("-order", default="file,lane,output,format,paired_end,meta", help="A list for the header order separated by commas. Only restriction is format can't be last header in list")
    parser.add_argument("-metaCustom", help="A custom meta field")
    parser.add_argument("-fileType", help="Format of files ex. (fastq,fastqc). If variable formats in directory select -findType.")
    parser.add_argument("-findType", action='store_true', help="This option allows multiple formats to occur in directory and will utilize the extension to determine the file format")
    parser.add_argument("-ProcessOutput", default="reads", help="Output of process that create files ex. (reads,fastqc)")
    parser.add_argument("-ucsc_db", default="hg38", help="UCSC reference assembly identifier")
    parser.add_argument("-pipeline", help="Pipeline used to create file")
    parser.add_argument("-ref_gene_set", help="Reference gene set")
    parser.add_argument("-outputFile",  help="Output file")
    parser.add_argument("-outputFileAdd", help="Output file to append new files.")
    args = parser.parse_args()

    InputType = multi(args)
    if args.outputFileAdd:
        out = open(args.outputFileAdd, "a")
    else:
        out = open(args.outputFile, "wb")
        out.write(args.order.replace(",", "\t") + "\n")

    # What to do if a single file #
    if InputType == "File":
        lane, read, barcode = findCommonParts(args.Input, args)
        if args.metaCustom:
            meta = args.metaCustom
        else:
            meta = buildMeta(args.Input, args.metaBuild)
        if args.metaFormat:
            meta = getMeta(args.metaFormat)
        elif args.metaFile:
            meta = grabMeta(args.metaFile)
            meta = meta[0]
        elif args.findType:
            args.fileType = Typefinder(args.Input)
        else:
            writeData(args.Input, out, args.order.lower(), args.order.split(","), lane, read, barcode, meta, args.fileType, args.ProcessOutput, args.ucsc_db, args.pipeline, args.ref_gene_set)

    # What to do if a single directory #
    elif InputType == "Directory":
        files = os.listdir(args.Input)
        sortedFiles = sorted(files)
        counter = 0
        for val in sortedFiles:
            parts = val.split('/')
            Fi = parts[-1]
            lane, paired_end, barcode = findCommonParts(val, args)
            file_path = args.Input+val
            if args.metaCustom:
                meta = args.metaCustom
            else:
                meta = buildMeta(Fi, args.metaBuild)
            if args.metaFormat:
                meta = getMeta(args.metaFormat)
            elif args.metaFile:
                meta = grabMeta(args.metaFile)
                meta = meta[counter]
            elif args.findType:
                args.fileType = Typefinder(val)
            writeData(file_path, out, args.order.lower(), args.order.split(","), lane, paired_end, barcode, meta, args.fileType, args.ProcessOutput, args.ucsc_db, args.pipeline, args.ref_gene_set)
            counter += 1

    # What to do with multiple files #
    elif InputType == "MFile":
        if re.search(',', str(args.Input[0])):
            args.Input = args.Input[0].split(',')
        for val in args.Input:
            parts = val.split('/')
            Fi = parts[-1]
            lane, paired_end, barcode = findCommonParts(Fi, args)
            if args.metaCustom:
                meta = args.metaCustom
            else:
                meta = buildMeta(Fi, args.metaBuild)
            if args.metaFormat:
                meta = getMeta(args.metaFormat)
            elif args.metaFile:
                meta = grabMeta(args.metaFile)
                meta = meta[0]
            elif args.findType:
                args.fileType = Typefinder(Fi)
            writeData(val, out, args.order.lower(), args.order.split(","), lane, paired_end, barcode, meta, args.fileType, args.ProcessOutput, args.ucsc_db, args.pipeline, args.ref_gene_set)


    # What to do with multiple directories #
    elif InputType == "MDirectory":
        if re.search(',', str(args.Input[0])):
            args.Input = args.Input[0].split(',')
        for thing in args.Input:
            files = os.listdir(thing)
            sortedFiles = sorted(files)
            counter = 0
            for val in sortedFiles:
                parts = val.split('/')
                Fi = parts[-1]
                lane, paired_end, barcode = findCommonParts(val, args)
                file_path = thing+val
                if args.metaCustom:
                    meta = args.metaCustom
                else:
                    meta = buildMeta(Fi, args.metaBuild)
                if args.metaFormat:
                    meta = getMeta(args.metaFormat)
                elif args.metaFile:
                    metalist = grabMeta(args.metaFile)
                    meta = metalist[counter]
                elif args.findType:
                    args.fileType = Typefinder(val)
                writeData(file_path, out, args.order.lower(), args.order.split(","), lane, paired_end, barcode, meta, args.fileType, args.ProcessOutput, args.ucsc_db, args.pipeline, args.ref_gene_set)
                counter += 1

    else:
        print("Things didn't work")
    out.close()
