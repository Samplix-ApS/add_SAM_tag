import subprocess
import warnings
import sys, getopt
import os
from os import path
import re
import gzip
from natsort import natsorted, ns

SAMTOOLS_HANDLE = '/usr/local/samtools/bin/samtools'
ALIGNMENT_LIMIT = 10**6

TEMP_INPUT_SAM = 'temp_add_tag_input.sam'
TEMP_OUTPUT_SAM = 'temp_add_tag_output.sam'

def printHelp():
    print ('add_SAM_tag.py -i <inputfilename>')
    print('This script is used add read name as tag at the end of each read.\n')
    print('-i      input alignment file in SAM or BAM format with header\n')
    print('-o      change the output file name for the tagged SAM/BAM file\n')
    print('-b      create sorted and indexed bam file. Default is true. Set to false to skip\n')
    print('-r      add read name as tag. Default is true. Set to false to chagne it.\n')
    print('-c      add mapped chromosomes as tag. Default is true. Set to false to chagne it.\n')


class SamTag:
    def __init__(self):
        self.dictTag = {}


    def add_dict(self, name, chr):
        if name not in self.dictTag:
            self.dictTag[name]=set()
        self.dictTag[name].add(chr)

def validate_input(input_name, read_tag, chr_tag):
    if path.exists(input_name) == False:
        print('Provided BAM/SAM file does not exist')
        quit()
    if path.isfile(input_name) == False:
        print(input_name, 'is a directory, not a file.')
        quit()

    if input_name.endswith('.sam') == False and input_name.endswith('.bam') == False:
        print('Input file is not SAM or BAM file. Exiting program')
        quit()

    if chr_tag.lower() == 'true' or chr_tag == '':
        chr_tag = 'true'
        #print('-c set to true')
    elif chr_tag.lower() == 'false':
        chr_tag = 'false'
        print('-c set to false')
    else:
        print('Input for adding chromosomes as tag not understood. Use true or false')
        quit()

    if read_tag.lower() == 'true' or read_tag == '':
        read_tag = 'true'
        #print('-r set to true')
    elif read_tag.lower() == 'false':
        read_tag = 'false'
        print('-r set to false')
    else:
        print('Input for adding read name as tag not understood. Use true or false')
        quit()

    if chr_tag == 'false' and read_tag == 'false':
        print('Both tag arguments are false. One (or both) must be true. Exiting program')
        quit()

    return input_name, read_tag, chr_tag

def output_bam_arg(input_name,output_bam):
    if output_bam == '':
        path_name1 = os.path.basename(input_name)
        path_name2 = os.path.splitext(path_name1)[0]
        if path_name2.endswith('.sort'):
            path_name2 = path_name2[:-5]
        output_bam = '%s_tag.bam' % path_name2

    elif output_bam.endswith('.bam'):
        output_bam = output_bam

    elif output_bam.endswith('.sam'):
        print('Output name given in SAM format. Reverting to BAM format:')
        output_bam = output_bam[:-4]+'.bam'

    else:
        print('Output name not in BAM or SAM format. Exiting program')
        quit()

    if path.isfile(output_bam):
        print(output_bam, 'exists. Will be overwritten.')
        os.remove(output_bam)

    return output_bam

def return_code(process, cmd):
    if process.returncode != 0:
        print('\nsamtools', cmd,'FAILED\n')
        print()
        quit()

def samtools_sort(output_bam):
    print('Sorting bam file')
    run_samtools_sort = subprocess.run([SAMTOOLS_HANDLE, 'sort', '-@16 -O BAM', ('-o'+output_bam), TEMP_OUTPUT_SAM])
    return_code(run_samtools_sort, 'sort')
    print('Indexing bam file')
    run_samtools_index = subprocess.run([SAMTOOLS_HANDLE, 'index', '-@16', output_bam])
    return_code(run_samtools_sort, 'index')

def remove_temp():
    if path.exists(TEMP_INPUT_SAM):
        os.remove(TEMP_INPUT_SAM)

    if path.exists(TEMP_OUTPUT_SAM):
        os.remove(TEMP_OUTPUT_SAM)

def bam2sam(input_name):
    if input_name.endswith('.bam'):
        print('Input file is in BAM format. Converting to SAM.')
        input_sam = TEMP_INPUT_SAM
        call_samtools_view = subprocess.run([SAMTOOLS_HANDLE, 'view','-@ 16','-h','-o',input_sam, input_name])
        return_code(call_samtools_view, 'view')
        return input_sam

    if input_name.endswith('.sam'):
        input_sam = input_name
        return input_sam

def get_tags(input_sam, chr_tag):
    if chr_tag == 'true':
        f_input = open(input_sam)
        print('Obtaining tags:')
        sam_list = SamTag()
        for line in f_input:
            line=line.strip()
            if len(line) > 0:
                if bool(re.match('^@', line)) == False:
                    line_split=line.split("\t")
                    sam_list.add_dict(line_split[0],line_split[2])
        print('File read')
        return sam_list

    if chr_tag == 'false':
        sam_list = None

def add_chr_tag(line_split, read_name, sam_list):
    try:
        tag_dict = sam_list.dictTag[read_name]
    except KeyError:
        print(line_split)
        print(read_name)
        quit()
    sorted_tag_dict = natsorted(tag_dict)
    tag = 'RZ:Z:'+';'.join(sorted_tag_dict)
    added_tag = line_split + [tag]
    return added_tag

def add_read_tag(line_split, read_name):
    tag = 'RG:Z:'+read_name
    added_tag = line_split + [tag]
    return added_tag

def add_tags(sam_list, read_tag, chr_tag, input_sam):
    f_input = open(input_sam)
    if path.exists(TEMP_OUTPUT_SAM):
        os.remove(TEMP_OUTPUT_SAM)
    f_out = open(TEMP_OUTPUT_SAM, 'a')
    print('Adding tags')

    for line in f_input:
        line=line.strip()
        if len(line) > 0:
            if bool(re.match('^@', line)):
                f_out.write(line+'\n')
            else:
                line_split=line.split("\t")
                read_name = line_split[0]
                if read_tag == 'true':
                    line_split = add_read_tag(line_split, read_name)
                if chr_tag == 'true':
                    line_split = add_chr_tag(line_split, read_name, sam_list)
                line_tag = '\t'.join(line_split)
                f_out.write(line_tag+'\n')
    f_out.close()

def run_commands(input_name, output_bam,chr_tag, read_tag):
    input_name, read_tag, chr_tag = validate_input(input_name, read_tag, chr_tag)
    output_bam = output_bam_arg(input_name,output_bam)
    input_sam = bam2sam(input_name)
    sam_list = get_tags(input_sam, chr_tag)
    add_tags(sam_list, read_tag, chr_tag, input_sam)
    samtools_sort(output_bam)
    remove_temp()
    print('Generated tagged BAM-file:', output_bam)
    print('Generated index:', output_bam+'.bai')

def main(argv):
    input_name = ''
    output_bam= ''
    read_tag = ''
    chr_tag = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:c:",["help=", "input=", "output=","readtag=","chrtag="])
    except getopt.GetoptError:
        print ('addSAMtag.py -i <inputfilename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()
        elif opt in ("-i", "--input"):
            input_name = arg
        elif opt in ("-o", "--output"):
            output_bam = arg
        elif opt in ("-r", "--readtag"):
            read_tag = arg
        elif opt in ("-c", "--chrtag"):
            chr_tag = arg


    run_commands(input_name, output_bam, chr_tag, read_tag)



if __name__ == "__main__":
   main(sys.argv[1:])
