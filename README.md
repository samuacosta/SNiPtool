# SNiPtool

Analysis of single-nucleotide polymorphism prediction tools.


## Features

SNiPtool generates a dataset of all possible SNP-caused variants for a chosen set of genes and calculates pathogenicity prediction values for all of them. It does this in two main processes.

It starts by receiving a list of HGNC gene symbols (e.g., ‘BRCA1’, ‘ATM’). It retrieves the transcript coding sequence using the Ensembl REST API. It then proceeds to read the codons sequentially and evaluate all the SNPs that would result in a missense mutation. The tool supports the use of a custom genetic code provided in a CSV file. If absent, the standard genetic code is used. A variant is generated in the dataset for each of the mutation-causing SNP in the HGVS Simple Variant Nomenclature. All the generated variants belong to a mutation batch, which allows separating different genes in groups. Due to the possible high volume of generated data, the generation process is asynchronous. A batch appears in the list as soon its generation process is complete.

The second part involves sending generated mutation batches to the VEP to retrieve the pathogenicity predictions. After a generated batch is provided by the user, the tool retrieves all the predictions for each method for all the variants that belong to that batch using the REST API, and stores this information in the database.

The latest stable version of the tool was deployed in an AWS EC2 container and it is accessible at http://samuacosta.info/software/sniptool.


## Author
Samuel Acosta [samuel.acostamelgarejo AT postgrad.manchester.ac.uk]

## License
[GPLv3](https://choosealicense.com/licenses/gpl-3.0/)