# Annotated Bibliography


### Marocco, D., & Nolfi, S. (2007)
Main experiment the current project builds on.  
Specs:
- Environment
  - size: 270 * 270 cm
  - 2 target areas, each
- Agents
  - morphology
    - circular body, radius = 11 cm
  - controller:
    - fixed architecture
    - free parameters:
      - synaptic weights
      - biases
      - time constants
    - sensors (14 in total)
      - 8 infrared sensors
        - * how are they placed?V
      - 1 ground sensor
        - * how are they placed?V
      - 4 communication sensors
        - each encode intensity of signals produced by robots located within 100 cm distance from a orthogonal direction (frontal, rear, left, right; each include 90 degrees)
      - 1 communication sensors for comm. state at t-1
    - actuators
      - 2 motor units
      - 1 communication unit (range: [0.0~1.0])
    - internal neurons
      - 2 internal neurons
        - * why these internal neurons?
- Trial
  - 4 robots with identical controllers
  - random start position and orientation, outside of target areas
  - each trial lasts for 100 seconds (w/ 100ms timestep)
    - i.e. 1000 timesteps
- Evolution Run
  - each team allowed to live for 20 trials
  - initial population = 100 randomly generated genotypes
  - 20 best genotypes are allowed to reproduce
    - generate 5 copies
    - each copy with 2% bits replaced with new random values
  - each run lasts 100 generations
  - replicated 10 times, each with a different initial population
- Fitness calculation
  - for each timestep:
    - 0.25 points for each robot located in a target area
    - -1.00 for each extra robot exceeding 2 in a target area
  - total fitness score = summing fitness gathered at each timestep
- Genome encoding
  - each parameter:
    - encoded with 8 bits
    - biases and weights normalized to [-5.0, 5.0]
    - time constants normalized to [0.0, 1.0]



### Szathmáry et al. (2007)
- the emergence of language is a hard problem
- uses evolutionary
- doesn't care about modality, more concerned with
- brain ontogenesis, neuron morphologies, indirect genetic encoding


##### References

 Marocco, D., & Nolfi, S. (2007). Communication in Natural and Artificial Organisms: Experiments in Evolutionary Robotics. _Emergence of Communication and Language_, 189-205. doi:[10.1007/978-1-84628-779-4_9](https://www.researchgate.net/publication/226281786_Communication_in_Natural_and_Artificial_Organisms_Experiments_in_Evolutionary_Robotics)

 Szathmáry, E., Szathmáry, Z., Ittzés, P., Orbaán, G., Zachár, I., Huszár, F., . . . Számadó, S. (2007). In silico Evolutionary Developmental Neurobiology and the Origin of Natural Language. _Emergence of Communication and Language_, 151-187. doi:[10.1007/978-1-84628-779-4_8](https://link.springer.com/chapter/10.1007%2F978-1-84628-779-4_8)
