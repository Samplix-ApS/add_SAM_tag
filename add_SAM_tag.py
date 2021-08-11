import subprocess
import warnings
import sys, getopt
import os
import re
import gzip

def print_help():
    print ('addSAMtag.py -i <inputfilename>')
    print('This script is used add read name as tag at the end of each read.\n')
    print('-i      input alignment file in SAM or BAM format with header\n')
    print('-o      change the output file name for the tagged SAM/BAM file\n')
    print('-b      create sorted and indexed bam file. Default is true. Set to false to skip\n')
    print('-r      add read name as tag. Default is true. Set to false to chagne it.\n')
    print('-c      add mapped chromosomes as tag. Default is true. Set to false to chagne it.\n')
    ### whatever

def is_output_bam(bam_arg):
    if bam_arg == '':
        print('Create bam set to true.')
        return True

    if bam_arg.lower() == 'true':
        print('Create bam set to true')
        return True

    if bam_arg.lower() == 'false':
        print('Create bam set to false')
        return False

    print('Create bam input ignored. Use true or false. Defaulting to true')
    return True

def output_name_arg(output_name, input_name):
    path_name = os.path.basename(input_name)
    if output_name == '':
        path_name = os.path.splitext(path_name)[0]
        output_name = '%s.tag.sam' % path_name
        remove_sam = True
        return path_name, output_name, remove_sam

    if output_name.endswith('.bam'):
        path_name = os.path.splitext(output_name)[0]
        output_name = '%s.tag.sam' % path_name
        remove_sam = True
        return path_name, output_name,remove_sam

    if output_name.endswith('.sam'):
        path_name = os.path.splitext(output_name)[0]
        output_name = '%s.tag.sam' % path_name
        remove_sam = False
        return path_name,output_name, remove_sam

    print('Output name must end with .sam or .bam')
    quit()

def is_read_tag(read_tag_arg):
    if read_tag_arg == '':
        print('Add readname as tag set to true')
        return True

    if read_tag_arg.lower() == 'true':
        print('Add readname as tag set to true')
        return True

    if read_tag_arg.lower() == 'false':
        print('Add readname as tag set to false')
        return False

    print('Add readname as tag input ignored. Use true or false. Defaulting to true')
    return True

def is_chr_tag(chr_tag_arg):
    if chr_tag_arg == '':
        print('Add mapped chromosomes as tag set to true')
        return True

    if chr_tag_arg.lower() == 'true':
        print('Add mapped chromosomes as tag set to true')
        return True

    if chr_tag_arg.lower() == 'false':
        print('Add mapped chromosomes as tag set to false')
        return False

    print('Add mapped chromosomes as tag input ignored. Use true or false. Defaulting to true')
    return True

def match_name(name, object_name):
    r_name=re.compile(name)
    return True if r_name.match(object_name) else False

class SamNameChr:
    def __init__(self,n,c,a):
        self.name=n
        self.chr=c
        self.all=a

    def print_only_read_tag(self):
        print_str = '\t'.join(self.all)
        return print_str
        #self.tag

class TagChr:
    def __init__(self,n,t):
        self.name=n
        self.tag=t

class SamTag:
    def __init__(self,a):
        self.all=a
    def print_tag(self):
        print_str = str(self.all)
        return print_str

def get_unique(list):
    chr_list = []
    for ele in list:
        chr_list.append(ele)
    set_chr_list= set(chr_list)
    sort_chr_list = sorted(set_chr_list)
    return sort_chr_list


class SamList:
    def __init__(self):
        self.sam_list = []
        self.sam_head = []

    def add_name_chr(self,item):
        self.sam_list.append(item)

    def add_sam_head(self,item):
        self.sam_head.append(item)


    def print_head(self):
        print_str = '\n'.join(self.sam_head)
        return print_str

    def get_unique(self):
        print('Finding unique read names')
        name_list = []
        for object in self.sam_list:
            name_list.append(str(object.name))
        set_name_list = set(name_list)
        return set_name_list

    def get_chr_list(self):
        name_list = self.get_unique()
        print('Finding tags')
        chromo_list= []
        for name in name_list:
            chr_list= []
            for object in self.sam_list:
                match = False
                if match_name(name, object.name) == True:
                    match = True
                if match == True:
                    chr_list.append(object.chr)
            tag_list = get_unique(chr_list)
            tag_list=';'.join(tag_list)
            tag_list = 'RZ:Z:'+tag_list
            chromo_list.append(TagChr(name, tag_list))
        return chromo_list

    def get_tags(self):
        sam_tag_list = []
        chromo_list = self.get_chr_list()
        print('Adding tags')
        for object in chromo_list:
            for sam in self.sam_list:
                if match_name(object.name, sam.name) == True:
                    tag = sam.all
                    tag += [object.tag]
                    tag= '\t'.join(tag)
                    sam_tag_list.append(SamTag(tag))
        return sam_tag_list

def main(argv):
    input_name = ''
    output_name= ''
    bam_arg = ''
    read_tag_arg = ''
    chr_tag_arg = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:b:r:c:",["help=", "inputfilename=", "outputfilename=", "makebam=","readtag=","chrtag="])
    except getopt.GetoptError:
        print ('addSAMtag.py -i <inputfilename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-i", "--inputfilename"):
            input_name = arg
        elif opt in ("-o", "--outputfilename"):
            output_name = arg
        elif opt in ("-b", "--makebam"):
            bam_arg = arg
        elif opt in ("-r", "--readtag"):
            read_tag_arg = arg
        elif opt in ("-c", "--chrtag"):
            chr_tag_arg = arg

    path_name, output_name, remove_sam = output_name_arg(output_name, input_name)
    read_tag_arg = is_read_tag(read_tag_arg)
    chr_tag_arg = is_chr_tag(chr_tag_arg)
    if read_tag_arg == False and chr_tag_arg == False:
        print('readtag and chrtag are both false. One of the statements has to be true. Aborting')
        quit()

    input_bam_to_sam = ''
    if input_name.endswith('.bam'):
        input_bam_to_sam = '%s.sam' % path_name
    if input_bam_to_sam != '':
        print('Input file is in BAM format. Converting to SAM.')
        call_samtools_view = subprocess.call(['/usr/local/samtools/bin/samtools', 'view', '-h', input_name, ('-o'+input_bam_to_sam)])
        f_input=open(input_bam_to_sam)
    else:
        f_input = open(input_name)



    sam_list = SamList()
    header = False
    for line in f_input:
        line=line.strip()
        if len(line.split("\t")) >9:
            line=line.split("\t")
            if read_tag_arg:
                tag = 'RG:Z:'+line[0]
                line += [tag]
            sam_list.add_name_chr(SamNameChr(line[0], line[2], line))
        else:
            sam_list.add_sam_head(line)
            header = True
    f_input.close()
    print('File read')

    fout=open(output_name, "wt")
    if header == True:
        fout.write(sam_list.print_head()+'\n')
    else:
        print('Header seems to be lacking. Cannot sort and index with SAMtools')

    if chr_tag_arg == False:
        for object in sam_list.sam_list:
            fout.write(object.print_only_read_tag()+'\n')
        fout.close()

    if chr_tag_arg:
        sam_tag_list = sam_list.get_tags()
        for object in sam_tag_list:
            fout.write(object.print_tag()+'\n')
        fout.close()

    if is_output_bam(bam_arg) == False:
        remove_sam = False

    if header == False:
        print('Output file:', output_name)
    elif is_output_bam(bam_arg):
        if remove_sam == False:
            print('Output file:', output_name)
        outputBamName = '%s.tag.bam' % path_name
        print('Sorting and indexing with SAMtools.')
        call_samtools_sort = subprocess.call(['/usr/local/samtools/bin/samtools', 'sort', '-@16 -O BAM', ('-o'+outputBamName), output_name])
        print('Output file:', outputBamName)
        call_samtools_index = subprocess.call(['/usr/local/samtools/bin/samtools', 'index', '-@16', outputBamName])
        print('Output file:', outputBamName+'.bai')
    else:
        print('Output file:', output_name)
    if remove_sam == True:
        os.remove(output_name)

    if input_bam_to_sam != '':
        os.remove(input_bam_to_sam)

if __name__ == "__main__":
   main(sys.argv[1:])
