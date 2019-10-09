.PHONY: download-wiki download-pubmed install-requirements

DATA = ./data/
WIKI = ./data/wiki
PUBMED = ./data/pubmed

download-wiki: 
	mkdir -p ${WIKI}
	echo "Downloading latest Wikipedia Dump"
	wget -c -q -P ${WIKI} https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
	echo "Completed"
	echo "Downloading latest Simple Wikipedia Dump"
	wget -c -q -P ${WIKI} https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-articles.xml.bz2
	echo "Completed"
	

download-pubmed:
	mkdir -p ${PUBMED}
	echo "Downloading Pubmed Abstract corpus"
	wget -P ${PUBMED} -c -q -r -A .xml.gz ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/
	echo "Completed"

install-requirements:
	pip install -U gensim
	pip install -U kenlm
	
 
	
