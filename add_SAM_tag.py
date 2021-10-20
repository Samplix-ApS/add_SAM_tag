import subprocess
import warnings
import sys, getopt
import os
import re
import gzip

def printHelp():
    print ('addSAMtag.py -i <inputfilename>')
    print('This script is used add read name as tag at the end of each read.\n')
    print('-i      input alignment file in SAM or BAM format with header\n')
    print('-o      change the output file name for the tagged SAM/BAM file\n')
    print('-b      create sorted and indexed bam file. Default is true. Set to false to skip\n')
    print('-r      add read name as tag. Default is true. Set to false to chagne it.\n')
    print('-c      add mapped chromosomes as tag. Default is true. Set to false to chagne it.\n')

def isOutputBam(bamArg):
    if bamArg == '':
        print('Create bam set to true.')
        return True

    if bamArg.lower() == 'true':
        print('Create bam set to true')
        return True

    if bamArg.lower() == 'false':
        print('Create bam set to false')
        return False

    print('Create bam input ignored. Use true or false. Defaulting to true')
    return True

def outputNameArg(outputName, inputName):
    pathName = os.path.basename(inputName)
    if outputName == '':
        pathName = os.path.splitext(pathName)[0]
        outputName = '%s.tag.sam' % pathName
        removeSam = True
        return pathName, outputName, removeSam

    if outputName.endswith('.bam'):
        pathName = os.path.splitext(outputName)[0]
        outputName = '%s.tag.sam' % pathName
        removeSam = True
        return pathName, outputName,removeSam

    if outputName.endswith('.sam'):
        pathName = os.path.splitext(outputName)[0]
        outputName = '%s.tag.sam' % pathName
        removeSam = False
        return pathName,outputName, removeSam

    print('Output name must end with .sam or .bam')
    quit()

def isReadTag(readTagArg):
    if readTagArg == '':
        print('Add readname as tag set to true')
        return True

    if readTagArg.lower() == 'true':
        print('Add readname as tag set to true')
        return True

    if readTagArg.lower() == 'false':
        print('Add readname as tag set to false')
        return False

    print('Add readname as tag input ignored. Use true or false. Defaulting to true')
    return True

def isChrTag(chrTagArg):
    if chrTagArg == '':
        print('Add mapped chromosomes as tag set to true')
        return True

    if chrTagArg.lower() == 'true':
        print('Add mapped chromosomes as tag set to true')
        return True

    if chrTagArg.lower() == 'false':
        print('Add mapped chromosomes as tag set to false')
        return False

    print('Add mapped chromosomes as tag input ignored. Use true or false. Defaulting to true')
    return True

def matchName(name, objectName):
    rName=re.compile(name)
    return True if rName.match(objectName) else False

class SamNameChr:
    def __init__(self,n,c,a):
        self.name=n
        self.chr=c
        self.all=a

    def printOnlyReadTag(self):
        printStr = '\t'.join(self.all)
        return printStr
        #self.tag

class TagChr:
    def __init__(self,n,t):
        self.name=n
        self.tag=t

class SamTag:
    def __init__(self,a):
        self.all=a
    def printTag(self):
        printStr = str(self.all)
        return printStr

def getUnique(list):
    chrList = []
    for ele in list:
        chrList.append(ele)
    setChrList= set(chrList)
    sortChrList = sorted(setChrList)
    return sortChrList


class SamList:
    def __init__(self):
        self.samList = []
        self.samHead = []
        self.dictTag = {}

    def addNameChr(self,item):
        self.samList.append(item)

    def addSamHead(self,item):
        self.samHead.append(item)

    def addDict(self, name, chr):
        if name not in self.dictTag:
            self.dictTag[name]=set()
        self.dictTag[name].add(chr)

    def printHead(self):
        printStr = '\n'.join(self.samHead)
        return printStr

    def addTags(self):
        samTagList = []
        print('Adding tags')
        for sam in self.samList:
            samAll = sam.all
            tagDict = self.dictTag[sam.name]
            sortTagDict = sorted(tagDict)
            tag = 'RZ:Z:'+';'.join(sortTagDict)
            fullNewLine = '\t'.join(samAll + [tag])
            samTagList.append(SamTag(fullNewLine))
        return samTagList

def main(argv):
    inputName = ''
    outputName= ''
    bamArg = ''
    readTagArg = ''
    chrTagArg = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:b:r:c:",["help=", "inputfilename=", "outputfilename=", "makebam=","readtag=","chrtag="])
    except getopt.GetoptError:
        print ('addSAMtag.py -i <inputfilename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()
        elif opt in ("-i", "--inputfilename"):
            inputName = arg
        elif opt in ("-o", "--outputfilename"):
            outputName = arg
        elif opt in ("-b", "--makebam"):
            bamArg = arg
        elif opt in ("-r", "--readtag"):
            readTagArg = arg
        elif opt in ("-c", "--chrtag"):
            chrTagArg = arg

    pathName, outputName, removeSam = outputNameArg(outputName, inputName)
    readTagArg = isReadTag(readTagArg)
    chrTagArg = isChrTag(chrTagArg)
    if readTagArg == False and chrTagArg == False:
        print('readtag and chrtag are both false. One of the statements has to be true. Aborting')
        quit()

    inputBamtoSam = ''
    if inputName.endswith('.bam'):
        inputBamtoSam = '%s.sam' % pathName
    if inputBamtoSam != '':
        print('Input file is in BAM format. Converting to SAM.')
        call_samtools_view = subprocess.Popen(['/usr/local/samtools/bin/samtools', 'view', '-h', inputName], stdout=subprocess.PIPE)
        stdout, stderr = call_samtools_view.communicate()
        stdout=stdout.decode("utf-8")
        stdout=stdout.split('\n')
        finput=stdout
    else:
        finput = open(inputName)



    samList = SamList()
    header = False
    for line in finput:
        line=line.strip()
        if len(line.split("\t")) >9:
            line=line.split("\t")
            if readTagArg:
                tag = 'RG:Z:'+line[0]
                line += [tag]
            samList.addNameChr(SamNameChr(line[0], line[2], line))
            samList.addDict(line[0],line[2])
        else:
            samList.addSamHead(line)
            header = True
    if inputBamtoSam == '':
        finput.close()
    print('File read')

    fout=open(outputName, "wt")
    if header == True:
        fout.write(samList.printHead()+'\n')
    else:
        print('Header seems to be lacking. Cannot sort and index with SAMtools')

    if chrTagArg == False:
        for object in samList.samList:
            fout.write(object.printOnlyReadTag()+'\n')
        fout.close()

    if chrTagArg:
        samTagList = samList.addTags()
        for object in samTagList:
            fout.write(object.printTag()+'\n')
        fout.close()

    if isOutputBam(bamArg) == False:
        removeSam = False

    if header == False:
        print('Output file:', outputName)
    elif isOutputBam(bamArg):
        if removeSam == False:
            print('Output file:', outputName)
        outputBamName = '%s.tag.bam' % pathName
        print('Sorting and indexing with SAMtools.')
        call_samtools_sort = subprocess.call(['/usr/local/samtools/bin/samtools', 'sort', '-@16 -O BAM', ('-o'+outputBamName), outputName])
        print('Output file:', outputBamName)
        call_samtools_index = subprocess.call(['/usr/local/samtools/bin/samtools', 'index', '-@16', outputBamName])
        print('Output file:', outputBamName+'.bai')
    else:
        print('Output file:', outputName)
    if removeSam == True:
        os.remove(outputName)


if __name__ == "__main__":
   main(sys.argv[1:])
