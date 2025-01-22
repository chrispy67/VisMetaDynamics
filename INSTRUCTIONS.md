# INSTRUCTIONS

<b>This resource assumes you are familiar with molecular dynamics simulations and have completed [Plumed Masterclass 21.004](https://www.plumed-tutorials.org/lessons/21/004/data/NAVIGATION.html)! This resource is meant to help users build an intuition for choosing metadynamics parameters using alanine dipeptide as an example system. </b>


1. <b>Clone the Github repository for this tutorial.</b>
    ```
    git clone https://github.com/chrispy67/VisMetaDynamics.git
    ```

2. <b>Ensure dependencies are installed by creating or updating your Python environment with `environment.yml`.  </b>

    Dependencies include NumPy, matplotlib, Pickle, Flask, ffmpeg, etc. 

    Create a new environment:
    ```
    conda env create -f environment.yml
    ```
    or update an existing environment:
    ```
    conda env update --file environment.yml --prune
    ```

3. <b>Navigate to the home directory and launch the static webpage. </b>
    ```
    cd VisMetaDynamics/
    python app.py
    ```

    This *should* automatically launch the tutorial in your browser. If you are having issues and <b> restarting the app does not work</b>, there is also a simple CLI. Here are a couple of example commands.

    Achieve better sampling with a longer metadynamics simulation and more even sampling:
    ```
    python src/walker.py --steps 100000 --metad --w 1.0 --hfreq 100
    ```

    Or just watch the ball go back and forth with an unbiased simulation:
    ```
    python src/walker.py --steps 10000
    ```

4. <b>Build an intution for choosing MD simulation and metadynamics parameters. </b>

    Play with the sliders and visualize the effects of poor parameters, undersampling, oversampling, and much more. There is no one right answer for this tutorial. Rather, users are encouraged to address the following questions (also found on the webpage):
    
    - How do the metadynamics parameters affect resolution of the free energy surface? 

    - How do the metadynamics parameters affect simulation performance?

    - Am I wasting time adding really small Gaussians?

    - How does the starting point of the simulation affect sampling?

    - What does good sampling look like?

    - If the underlying potential is NOT known, how could these results be misinterpreted?

    - <b>How can I get an adequate estimate of the free energy surface with the lowest computational cost?</b>
