# VisMetaDynamics
An interactive tutorial to metadynamics and enhanced sampling techniques for molecular dynamics simulations


# Introduction

## <b>What is Metadynamics?</b>
Metadynamics (MetaD) is an enhanced sampling technique used in conjunction with molecular dynamics (MD) simulations to sample rare events by encouraging a system to adopt otherwise energetically unfavorable configurations. Most importantly, MetaD allows the free energy landscape of a particular observable to be recovered by a process called reweighting. The potential as a function of time is modeled by equation below. 


$$
V_S(t) = t_0 \sum_{t'=\tau_G} W_0 \exp \left( - \frac{(S_i - S_i(t'))^2}{2\sigma_i^2} \right)
$$

First described by [Laio and Parrinello][1] in 2002, MetaD has proven to be useful in applications such as [drug discovery][2], [materials science][3], [ligand bindings][4], and [much more][5]. Since then, numerous versions of MetaD have been designed to address the shortcomings of classical metadynamics; parallel-bias metadynamics, well-tempered metadynamics, and bias-exchange metadynamics are all flavors of the original 2002 paper. MetaD and all related acronyms can be applied easily to modern MD engines via plugins or built in functions, making this family of enhanced sampling techinques widely accessible. A thorough review of the rigorously correct implementations and limitations for specific use cases of MetaD are beyond the scope of this resource, but users are encouraged to consult [documentation](https://www.plumed.org/) and [practical applications](https://www.plumed-nest.org/) on their own. 

# About

VisMetaDynamics is a 1-dimensional Langevian integrator using a pre-defined free energy surface. This free energy surface is the result of a short MetaD simulation of alanine dipeptide, similar to this [tutorial](https://www.plumed.org/doc-v2.8/user-doc/html/lugano-3.html) and many others using alanine dipeptide as a toy system. The unmistakable, *a priori* free energy surface consistent alanine dipeptide's preference towards (cis/trans??) is an instantly recognizable and repeatedly proven result, both computationally and experimentally. 

When first learning how to use metadynamics, I struggled to visualize the effects these parameters had on the resulting free energy surface. Besides running several metadynamics simulations with slightly different parameters, there was no way to understand the effects these hyperparameters had on the reweighted free energy surface. VisMetaDynamics allows you to tune these parameters by hand with many options to visualize and compare simulations in seconds.

VisMetaDynamics is intentionally free of any explanations, interpretations, or guided questions to answer. Rarely, if ever, do we truly know the underlying free energy surface that metadynamics is sampling. Even in this case, the underlying potential that defines this system is an approximation—a sine/cosine fit of a free energy surface from an *in vacuo* metadynamics simulation of alanine dipeptide with its own parameters and 3D modes of motion. <b>Trying to recreate the underlying free energy surface exactly is NOT the goal of this tutorial.</b> Rather, users should be trying to answer these questions:
> * How do the metadynamics parameters affect resolution of the free energy surface? 
> * How do the metadynamics parameters affect simulation performance? Am I wasting time adding really small Gaussians? 
> * How does the starting point of the simulation affect sampling? What about simulation time?
> * What does good sampling or "convergence" look like?
> * <b>How can I get an adequate estimate of the free energy surface with the lowest computational cost?</b>

## <b> What/who is this resource for for? </b>

VisMetaDynamics is designed for someone already familiar with MD simulations. This tool is meant to augment [existing tutorials](http://www.plumed-tutorials.org/browse.html) and resources by offering a visual, qualitative understanding of the effect of hyperparameters on the resulting free energy surface and performance. Users are encouraged to play with these sliders and observe changes in simulation performance, accuracy of the free energy surface, and overall simulation behavior as a function of these parameters. 

# Installation
Using this tutorial is as simple as cloning the repo and running `python app.py`. This will automatically open up a Flask webpage on your default browser. The Python scripts are run locally and can be computationally intensive, depending on the parameters chosen. The ranges of the values on the sliders are chosen to allow the user to explore many combinations of parameters, but may result in computationally intractable calculations.
>  This tutorial uses common libraries and has few dependencies, such as Scipy, Numpy, and Flask. `environment.yml` is included if needed. 


# Troubleshooting

> If the Flask webpage is not opening or showing a black screen, try running `python src/walker.py` to get the raw output of the integrator with the parameters from `src/config.py`


# Contributing 

# References
[1]: https://doi.org/10.1073/pnas.202427399
[2]: https://pubs.acs.org/doi/10.1021/acs.jmedchem.6b01642
[3]: https://doi.org/10.1038/nmat1696
[4]: https://pubs.acs.org/doi/full/10.1021/acs.jpcb.3c07972
[5]: https://doi.org/10.1088/0034-4885/71/12/126601

