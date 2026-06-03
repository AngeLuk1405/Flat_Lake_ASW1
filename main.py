from dataclasses import dataclass
import random
import math

# Constants:
WIDTH = 20 # Width of the lake grid
LENGTH = 20 # Length of the lake grid
NUM_FISHERS = 10 # Number of fisher-agents in the simulation
CAPACITY = 100.0 # Carrying capacity of biomass in each lake-patch
GROWTH_RATE = 0.3 # Growth rate of biomass in each patch
STRATEGIES = ["egoist", "imitator", "cooperator", "sanctioner"]
DIFFUSION_COEFFICIENT = 0.1 # Coefficient for diffusion of biomass between patches
SIMULATION_STEPS = 100
SIGHT_RADIUS = 3 # Radius within which fishers can see and interact with other fishers
COOPERATION_THRESHOLD = 50 # Minimal percentage of cooperators or sanctioners in sight for cooperators to cooperate


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
    current_strategy: str
    catch: float = 0.0
    total_catch: float = 0.0
    sanction_cost: float = 0.0

    # Fisher catches fish from current patch based on their strategy:
    def catch_fish(self, patch, neighbors):
        """Fisher catches fish from the current patch based on their strategy and neighbors."""
        
        # Egoist:
        if self.strategy == "egoist":
            # Egoists catch as much as possible from their current patch:
            self.catch = patch.biomass
        
        #Cooperator:
        elif self.strategy == "cooperator":
            # Cooperators cooperate if ther are not too many egoists in the sight radius.
            # Else they behave like egoists.
            # When there are no neighbors, they also cooperate.
            number_cooperative =sum(1 for neighbor in neighbors if is_cooperative(neighbor))

            if len(neighbors) == 0:
                # If there are no neighbors, cooperators cooperate:
                    self.catch = patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
            else:
                if (number_cooperative / len(neighbors)) * 100 > COOPERATION_THRESHOLD:
                    # Cooperation means catching as much as the growth of the patch:
                    self.catch = patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
                    
                else:
                    # If too many egiosts are around, cooperators behave like egoists:
                    self.catch = patch.biomass
        
        # Imitator:
        elif self.strategy == "imitator":
            best_neighbor = None
            best_total_catch = self.total_catch

            if len(neighbors) != 0:
                for neighbor in neighbors:
                    if neighbor.total_catch > best_total_catch:
                        best_neighbor = neighbor
                        best_total_catch = best_neighbor.total_catch     
                if best_neighbor is not None:
                    self.current_strategy = best_neighbor.strategy

            if self.current_strategy == "egoist":
                self.catch = patch.biomass

            elif self.current_strategy in ["cooperator", "sanctioner"]:
                self.catch = patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))

        #Sanctioner:
        elif self.strategy == "sanctioner":
            self.catch = patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
        #########
        # Sanktionierer: wenn Fischer im Sichtradius Egoisten sind -> STRAFE
        # Strafe auf alle verteilt oder auf die Kooperierer verteilt
        #########



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
        strategy = random.choice(STRATEGIES)  ####Evtl nicht random sondern bestimmte Anteile
        if strategy == "imitator":
            current_strategy = "egoist" # Imitators start as egoists but can change their strategy later
        else:
            current_strategy = strategy
        fisher = Fisher(x_position=x, y_position=y, strategy=strategy, current_strategy=current_strategy)
        fishers.append(fisher)
        
    return grid, fishers


# Get a list of neighboring fishers within the sight radius of a given fisher:
def get_neighbors(fisher, fishers):
    """Returns a list of neighboring fishers within the sight radius"""
    neighbors = []
    for other in fishers:
        if other is fisher:
            continue
        distance = math.sqrt(((fisher.x_position - other.x_position) ** 2 ) 
                             + ((fisher.y_position - other.y_position) ** 2)) # compute distance between fishers
        if distance <= SIGHT_RADIUS:
            neighbors.append(other)
    return neighbors

# Helper function to see if a fisher is cooperative (cooperator or sanctioner):
def is_cooperative(fisher):
    """Returns True if the fisher is cooperative, False if not cooperative."""
    if fisher.strategy in ["cooperator", "sanctioner"]:
        return True
    elif fisher.strategy == "imitator":
        return fisher.current_strategy in ["cooperator", "sanctioner"]
    else:
        return False
    
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
# Diffusion: Nachbarzellen Druchschnitt, speichern als Variable in Tick-1
# im nächsten Schritt Biomass = Biomass von davor, danach erst Wachstum 
#########


# Step function simulates one time step of the model. Biomass grows, fishers catch fish.
# Sanktioner strategy, and diffusion are yet to be implemented!
# For now imitators behave like egoists and sanctioners like cooperators.
def step(grid, fishers):
    """Advances the simulation by one step, updating biomass, fishing, sanctions
    and strategies."""
    # Update the biomass of each patch:
    for row in grid:
        for patch in row:
            #####
            #Biomasse für Wert von Tick-1 übernehmen, dann erst growen
            #####
            patch.grow()
    
    # Each fisher catches fish from current patch:
    for fisher in fishers:
        patch = grid[fisher.y_position][fisher.x_position]
        neighbors = get_neighbors(fisher, fishers)
        fisher.catch_fish(patch, neighbors)
        
        fisher.catch = min(fisher.catch, patch.biomass) # Catch cannot be more than the available biomass
        fisher.total_catch += fisher.catch
        patch.biomass -= fisher.catch
        patch.biomass = max(0.0, patch.biomass) # Biomass cannot be negative

        ######
        #Fischer bewegen sich in zufällige Richtung (in x und y, random.choice([-1, 0, 1])),
        #sicherstellen dass sie nicht aus dem Grid rauskommen
        #sicherstellen, dass sich nicht auf ein besetzten Feld fahren
        #evtl Schleife mit Abbruch sobald er ein passendes Feld gefunden hat
        ######



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

########
#Visualisierung: ganz mit KI  
#Feld von See, am besten animiert
#Farben für Biomasse, Fischer als farbiger Punkt für Strategie, mit Legende
#Diagramme: Biomasse über Zeit, Total Catch (in Abh. der Strategien evtl. mit Imitator) über Zeit
#Anzahl der Strategien über Zeit
########