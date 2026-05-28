from dataclasses import dataclass
import random

# Constants:
WIDTH = 20 # Width of the lake grid
LENGTH = 20 # Length of the lake grid
NUM_FISHERS = 10 # Number of fisher-agents in the simulation
CAPACITY = 100.0 # Carrying capacity of biomass in each lake-patch
GROWTH_RATE = 0.3 # Growth rate of biomass in each patch
STRATEGIES = ["egoist", "imitator", "cooperator", "sanctioner"]
DIFFUSION_COEFFICIENT = 0.1 # Coefficient for diffusion of biomass between patches
SIMULATION_STEPS = 100

@dataclass
class Patch:
    """Patches are the cells that make up the lake grid."""
    biomass: float
    capacity: float
    growth_rate: float
    
    def grow(self):
        """Updates the biomass of the patch according to its growth rate
        and using a logistic growth function."""
        self.biomass += self.growth_rate * self.biomass * (1 - (self.biomass / self.capacity))


@dataclass
class Fisher:
    """Fishers are the agents that interact with eachother and the patches by catching fish."""
    x_position: int
    y_position: int
    strategy: str
    catch: float = 0.0
    total_catch: float = 0.0
    sanction_cost: float = 0.0


# Initialization function to set up the lake-grid and the fishers:
def initialize():
    """Initializes the grid of patches and the list of fishers."""
    # Create a grid of patches:
    grid = []
    for y in range(LENGTH):
        row = []
        for x in range(WIDTH):
            biomass = random.uniform(50, 100)
            patch = Patch(biomass=biomass, capacity=CAPACITY, growth_rate=GROWTH_RATE)
            row.append(patch)
        grid.append(row)

    # Create a list of fishers:
    fishers = []
    for i in range(NUM_FISHERS):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, LENGTH - 1)
        strategy = random.choice(STRATEGIES)
        fisher = Fisher(x_position=x, y_position=y, strategy=strategy)
        fishers.append(fisher)
        
    return grid, fishers


# def diffuse(grid):
#     """ Diffuses biomass between neighboring patches using a diffusion coefficient."""
#     for y in range(LENGTH):
#         for x in range(WIDTH):
#             patch = grid[y][x]

#             # Get moore-neighbors:
#             neighbors = []
#             for dx in range (-1, 2):
#                 for dy in range (-1, 2):
#                     if dx == 0 and dy == 0:
#                         continue
#                     # Ensure we don't get positions outside the grid:
#                     neighbor_x = max(0, min(WIDTH - 1, x + dx))
#                     neighbor_y = max(0, min(LENGTH - 1, y + dy))

#                     neighbors.append(grid[neighbor_y][neighbor_x])
            
#             mean_neighbor_biomass = sum(neighbor.biomass for neighbor in neighbors) / len(neighbors)

#             biomass = patch.biomass + DIFFUSION_COEFFICIENT * (mean_neighbor_biomass - patch.biomass)


#########
# Diffusion: entweder KI fragen oder: Nachbarzellen Druchschnitt, speichern als Variable in Tick-1
# im nächsten Schritt Biomass = Biomass von davor, danach erst Wachstum 
#########


# Step function simulates one time step of the model. Biomass grows, fishers catch fish.
# Imitator strategy, sanctioner strategy, and diffusion are yet to be implemented!
# For now imitators behave like egoists and sanctioners like cooperators.
def step(grid, fishers):
    """Advances the simulation by one step, updating biomass, fishing, sanctions
    and strategies."""
    # Update the biomass of each patch:
    for row in grid:
        for patch in row:
            patch.grow()
    
    for fisher in fishers:
        patch = grid[fisher.y_position][fisher.x_position]
        if fisher.strategy == "egoist":
            # Egoists catch as much as possible from their current patch:
            fisher.catch = patch.biomass
        
        elif fisher.strategy in ["cooperator", "sanctioner"]:
            # Cooperators and sanctioners catch as much as the growth of the patch:
            fisher.catch = patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
        
        elif fisher.strategy == "imitator":
            # Placeholder for imitator strategy, currently like egoist:
            fisher.catch = patch.biomass

            #########
            # Fischer mit höchster Total Catch finden, diese Strategie übernehmen
            #########

            #########
            # Sanktionierer überhaupt mal machen
            #########
        
        fisher.catch = min(fisher.catch, patch.biomass) # Catch cannot be more than the available biomass
        fisher.total_catch += fisher.catch
        patch.biomass -= fisher.catch



def main():
    print("Hello from flat-lake!")
    grid, fishers = initialize()

    # Test: Print initial biomass of patch (0,0) and total catch and strategy of fisher 0:
    print(f'Intitial biomass of patch (0,0): {grid[0][0].biomass}')
    print(f'Strategy of fisher 0: {fishers[0].strategy}')
    print(f'Initial total catch of fisher 0: {fishers[0].total_catch}')

    step(grid, fishers)

    # Test: Print biomass of patch (0,0) and total catch of fisher 0 after one step:
    print(f'Biomass of patch (0,0) after one step: {grid[0][0].biomass}')
    print(f'Total catch of fisher 0 after one step: {fishers[0].total_catch}')


"""Schlauer Kommentar"""
"""Nicht so schlauer Kommentar"""
'''Allerschlauster Kommentar'''

if __name__ == "__main__":
    main()

#########
#Visualisierung: ganz mit KI  
#########