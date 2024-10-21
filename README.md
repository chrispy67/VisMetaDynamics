# VisMetaDynamics
An interactive tutorial to metadynamics and enhanced sampling techniques for molecular dynamics simulations

$$
V_S(t) = t_0 \sum_{t'=\tau_G} W_0 \exp \left( - \frac{(S_i - S_i(t'))^2}{2\sigma_i^2} \right)
$$

# Introduction

## <b>What is Metadynamics?</b>
Metadynamics (MetaD) is an enhanced sampling technique used in conjunction with molecular dynamics (MD) simulations to sample rare events by encouraging a system to adopt otherwise energetically unfavorable configurations. Most importantly, MetaD allows the free energy landscape of a particular observable to be recovered by a process called reweighting. 

First described by [Laio and Parrinello][1] in 2002, MetaD has proven to be useful in applications such as [drug discovery][2], [materials science][3], [ligand bindings][4], and [much more][5]. Since then, numerous versions of MetaD have been designed to address the shortcomings of classical metadynamics; parallel-bias metadynamics, well-tempered metadynamics, and bias-exchange metadynamics are all flavors of the original 2002 paper. MetaD and all related acronyms can be applied easily to modern MD engines via plugins or built in functions, making this family of enhanced sampling techinques widely accessible. A thorough review of the rigorously correct implementations and limitations for specific use cases of MetaD are beyond the scope of this resource, but users are encouraged to consult [documentation](https://www.plumed.org/) and [practical applications](https://www.plumed-nest.org/) on their own. 


## <b> What/who is this resource for for? </b>

VisMetaDynamics is designed for someone already familiar with MD simulations. This tool is meant to augment [existing tutorials](http://www.plumed-tutorials.org/browse.html) and resources by offering a visual, qualitative understanding of the effect of hyperparameters on the resulting free energy surface and performance. Users are encouraged to play with these sliders and observe changes in simulation performance, accuracy of the free energy surface, and overall simulation behavior as a function of these parameters. 

# About

VisMetaDynamics is a 1-dimensional Langevian integrator using a pre-defined free energy surface. This free energy surface is the result of a short MetaD simulation of alanine dipeptide, similar to this [tutorial](https://www.plumed.org/doc-v2.8/user-doc/html/lugano-3.html) and many others using alanine dipeptide as a toy system. The unmistakable, *a priori* free energy surface consistent alanine dipeptide's preference towards (cis/trans??) is an instantly recognizable and repeatedly proven result, both computationally and experimentally. 
## Installation

# Troubleshooting

# Contributing 

# References
[1]: https://doi.org/10.1073/pnas.202427399
[2]: https://pubs.acs.org/doi/10.1021/acs.jmedchem.6b01642
[3]: https://doi.org/10.1038/nmat1696
[4]: https://pubs.acs.org/doi/full/10.1021/acs.jpcb.3c07972
[5]: https://doi.org/10.1088/0034-4885/71/12/126601

