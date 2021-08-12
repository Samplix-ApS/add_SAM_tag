# add_SAM_tag
Tool for adding tags to S/BAM files to aid viewing in IGV. 

## Description

Two tags are currently possible: read name (RG) and all chromosomes which each read aligns to (RZ), e.g. if read A maps to chr_01, chr_05, and chr_08, the tag will be chr_01;chr_05;chr_08. This tag will be added to each instance of read A present in the S/BAM alignment file. 
Using these two tags, this allows for coloring by read name (enabling to see chimeric reads) and grouping alignments by chromosomes. This is highly useful when working with inserts. 


## Getting Started

### Dependencies

* Python3
* samtools 1.9 (using htslib 1.9)(the script has not been tested with later versions, but would likely work)
### Installation

Download the python script. 

### Executing program

* To add the tags run the following command:
```
python3 add_SAM_tag.py -i S/BAM_file <optional> 

```
-i	input alignment file in BAM or SAM format with header
-o	change the output file name for the tagged SAM/BAM file
-b	create sorted and indexed bam file. Default is true. Set to false to skip.
-r	add read name as tag. Default is true. Set to false to skip. 
-c	add mapped chromosomes as tag. Default is true. Set to false to skip.

## Help

Any advise for common problems or issues.
```
python3 add_SAM_tag.py -h
```

## Authors

Camille Johnston 


