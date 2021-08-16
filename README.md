# add_SAM_tag
Tool for adding tags to S/BAM files to aid viewing in IGV. 

## Table of Contents
- [Description](#descrip)
- [Getting Started](#get_started)
  - [Dependencies](#dependencies)
  - [Installation](#install_)
  - [Executing program](#execute_program)
  - [Viewing in IGV](#view_IGV)
  - [Help](#help_)
  - [Authors](#authors_)

## <a name="descrip"></a> Description

Two tags are currently possible: read name (RG) and all chromosomes which each read aligns to (RZ), e.g. if read A maps to chr_01, chr_05, and chr_08, the tag will be chr_01;chr_05;chr_08. This tag will be added to each instance of read A present in the S/BAM alignment file. 
Using these two tags, this allows for coloring by read name (enabling to see chimeric reads) and grouping alignments by chromosomes. This is highly useful when working with inserts. 

Coloring and grouping by readname (tag RG):

![image](https://user-images.githubusercontent.com/60882704/129158470-d4f5edfc-5230-4d82-80a9-fbc85c071cc7.png)

Coloring and grouping by chromosome (tag RZ):

![image](https://user-images.githubusercontent.com/60882704/129158712-cf2bde45-b985-4c86-8b57-bd72061d70d2.png)


Coloring by readname (tag RG) and grouping by chromosome (tag RZ): 

![image](https://user-images.githubusercontent.com/60882704/129158273-87011e96-d639-4697-8f76-495424ccf022.png)

Viewing reads mapped to insertion sequence and comparing to reads mapped to chromosome 18:

![image](https://user-images.githubusercontent.com/60882704/129162641-04091ff4-a106-4ee1-9b1e-4f3fc9c3a8d1.png)

## <a name="get_started"></a> Getting Started

### <a name="dependencies"></a>Dependencies

* Python3
* samtools 1.9 (using htslib 1.9)(the script has not been tested with later versions, but would likely work) must be in path
* IGV for viewing the alignment
### <a name="install_"></a> Installation

Download the python script. 

### <a name="execute_program"></a> Executing program

* To add the tags run the following command:
```
python3 add_SAM_tag.py -i S/BAM_file <optional> 

```
* The following parameters can be used.
```
-i	input alignment file in BAM or SAM format with header
-o	change the output file name for the tagged SAM/BAM file
-b	create sorted and indexed bam file. Default is true. Set to false to skip.
-r	add read name as tag. Default is true. Set to false to skip. 
-c	add mapped chromosomes as tag. Default is true. Set to false to skip.
```

### <a name="view_IGV"></a> Viewing in IGV
In IGV it is recommended to color by tag RG (read name) and group by tag RZ (mapped chromosomes). Sometimes it is necessary to group by tag RG, color by tag RG, and then group by tag RZ to get correct colors out. 

To view two different sites in the alignment, it is recommended to save the IGV session, close it, and open two new seperate windows. It is necessary to save, as the colors change upon saving, however, grouping is not affected. 

## <a name="help_"></a>Help

```
python3 add_SAM_tag.py -h
```

## <a name="authors_"></a>Authors

Camille Johnston 


