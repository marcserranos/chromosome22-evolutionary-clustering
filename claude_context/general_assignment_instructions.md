# **Teaching Assignment**

The goal of this project is to implement an algorithm that, using data from chromosome 22 of the SGDP (Simons Genome Diversity Project) and the geographical location of individuals or populations, is able to find $K$ groups separated by genetic barriers. The algorithm must search for a partition of the set of samples or populations such that the genetic diversity is as homogeneous as possible within the groups, while the genetic difference between groups is maximized.

The central question is not only which groups appear, but also where these boundaries fall geographically and what biological or historical meaning they may have. The project combines population genetics, genetic distances, spatial information, and combinatorial optimization, and is particularly suited to be solved using an evolutionary algorithm.

# **Biological Motivation**

Human populations are not separated into perfectly defined blocks, but they do not form a single homogeneous continuum either.

Geography, demographic history, migrations, and isolation have generated patterns of genetic variation that can often be interpreted as barriers or transitions.

Chromosome 22 is small enough to be manageable in a teaching laboratory, but contains enough variation to detect population structure.

# **Recommended Dataset for the Base Version**

It is recommended to use SGDP data corresponding to chromosome 22\. To simplify the problem, you can work at the population level instead of the individual level, using a representative geographical location for each population. This greatly reduces complexity and facilitates interpretation.

* Variants of chromosome 22 from the SGDP.  
* Assignment of each sample to a population or superpopulation.  
* Representative geographical coordinates for each population.  
* Optionally, a subset of SNPs (Single Nucleotide Polymorphisms) filtered by MAF (Minor Allele Frequency) or LD (Linkage Disequilibrium) to reduce dimensionality.

# **Biological Question**

Is it possible to find $K$ geographical groups defined by genetic barriers such that the diversity within each group is low and the difference between groups is high?

* Do the groups coincide with continents, superpopulations, or other finer structures?  
* Are there populations that act as bridges between groups?  
* Does the interpretation change when $K$ is varied?

# **Input Data**

* Genotype, haplotype, or allele frequency matrix of chromosome 22\.  
* Genetic distance matrix between individuals or populations. $F\_{\\text{ST}}$, $1 \- \\text{IBS}$, Euclidean distances over PCA, or distances between allele frequencies can be considered.  
* Geographical coordinates of populations or individuals.  
* Value of $K$, predefined or explored in various experiments.  
* Optionally, additional information such as superpopulation or a world map to visualize the results.

# **Representation of the Problem for the Evolutionary Algorithm**

Each individual in the evolutionary population represents a possible partition of the set of populations or samples into $K$ groups. A simple representation is an assignment vector:

$$w \= \[g\_1, g\_2, \\dots, g\_n\], \\quad g\_i \\in \\{1, \\dots, K\\}$$

where $g\_i$ indicates which group population or sample $i$ belongs to. This representation is easy to mutate and recombine. A geographic contiguity constraint or a penalty can also be added if a group becomes fragmented into highly distant regions.

* Each population or sample must be assigned to a single group.  
* One can avoid having overly small groups by imposing a minimum size.  
* It is also possible to penalize a partition that separates populations that are geographically very close but genetically similar.

# **Objective Function and Fitness**

The fitness must balance three components: intragroup genetic homogeneity, intergroup genetic separation, and geographic coherence. One possible formulation is:

$$\\text{Fitness} \= \\alpha \\cdot \\text{Intergroup\\\_Separation} \- \\beta \\cdot \\text{Intragroup\\\_Variance} \- \\gamma \\cdot \\text{Geographic\\\_Cost}$$

* **Separation between groups**: average genetic distance between groups or distance between genetic centroids.  
* **Variance within groups**: internal genetic diversity or average intragroup distance.  
* **Geographic cost**: penalty if a group contains highly dispersed populations without geographic continuity.

In a simpler version, the fitness can be defined using only the first two terms. In a richer version, a measure similar to the silhouette score adapted to genetics and geography can be added.

# **Recommended Working Model**

* Calculate a genetic distance matrix between populations or individuals of chromosome 22\.  
* Run the evolutionary algorithm to find the best partition into $K$ groups.  
* Represent the groups on a map and compare them with known population labels.  
* Repeat the analysis for various values of $K$ and compare the quality of the partitions.

# **Evolutionary Algorithm**

* Random initialization of partitions into $K$ groups.  
* Selection by tournament or elitist selection.  
* Crossover by partial exchange of assignments between two solutions.  
* Mutation by changing the assignment of one or several populations to another group.  
* Elitism to preserve the best partitions across generations.

# **Work Plan**

| Block | Objective | Content |
| :---- | :---- | :---- |
| 1 | Data Preparation | Select variants of chromosome 22, filter if necessary, group by populations, and obtain geographical coordinates. |
| 2 | Distance Calculation | Construct the genetic distance matrix and, optionally, a geographical distance matrix. |
| 3 | Model Implementation | Define the representation of individuals, the fitness function, and the evolutionary operators. |
| 4 | Experiments | Explore different values of $K$, different random seeds, and different distance metrics. |
| 5 | Interpretation | Visualize the groups in a PCA plot and on a map, and discuss the biological meaning of the results. |
| 6 | Final Presentation | Prepare slides with motivation, methods, results, limitations, and conclusions. |

# **Key Experiments**

* Compare groups obtained for $K \= 2, 3, 4$, and $5$.  
* Measure partition stability across multiple runs.  
* Compare a purely genetic partition with a partition incorporating geographical cost.  
* Analyze if groups coincide with classical 1000 Genomes superpopulations or reveal additional substructure.

# **Questions the Student Should Answer**

* Where do the found groups fall geographically?  
* Which populations are clearly grouped and which ones remain on the border?  
* Do the groups make sense from a historical or demographic standpoint?  
* How does the interpretation change when modifying $K$?  
* Is there any value of $K$ that seems particularly natural according to fitness or visualization?

# **Expected Results**

* A functional implementation of an evolutionary algorithm to detect genetic barriers.  
* One or several partitions of the set of populations into $K$ groups.  
* Figures clearly relating genetics and geography.  
* A discussion of the meaning of the groups from the perspective of population genetics.

# **Biological Interpretation**

* Groups may correspond approximately to large continental clusters.  
* Populations may also appear that do not fit perfectly into a single block, reflecting admixture or gradual transitions.  
* A discrepancy between geography and genetics is not an error: often it is precisely the most interesting result.

# **Suggested Figures**

* World map with populations colored according to the assigned group.  
* Genetic PCA colored by group.  
* Heatmap of genetic distances reordered according to the groups found.  
* Evolution of fitness over generations.  
* Visual comparison of partitions for different values of $K$.

