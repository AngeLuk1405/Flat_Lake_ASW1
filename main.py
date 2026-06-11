############# Import Packages #############
from dataclasses import dataclass
import random
import math
import matplotlib.pyplot as plt
import argparse

################ Constants ################
WIDTH = 20 # Width of the lake grid (x-axis)
LENGTH = 20 # Length of the lake grid (y-axis)
NUM_FISHERS = 20 # Number of fisher-agents in the simulation, if not specified by command line arguments
CAPACITY = 100.0 # Carrying capacity of biomass in each lake-patch
GROWTH_RATE = 0.08 # Growth rate of biomass in each patch
STRATEGIES = ["egoist", "imitator", "cooperator", "sanctioner"] # Possible strategies for fishers: egoist, imitator, cooperator, sanctioner
DIFFUSION_COEFFICIENT = 0.1 # Coefficient for diffusion of biomass between patches
SIMULATION_STEPS = 300 # Number of steps to run the simulation
SIGHT_RADIUS = 3 # Radius within which fishers can see and interact with other fishers
COOPERATION_THRESHOLD = 50 # Minimal percentage of cooperators or sanctioners in sight for cooperators to cooperate
SANCTION_COST = 10 # Amount of catch that is confiscated from egoists by sanctioners when they sanction them
SANCTION_THRESHOLD = 1.2
SUSTAINABLE_CATCH_MULTIPLIER = 5
RANDOM_MOVE_CHANCE = 0.2 # Chance that a fisher moves to a random patch instead of the best patch
SANCTIONER_KEEP_RATIO = 0.5 # part of the catch that sanctioners keep for themselves, when they sanction others
DISTRIBUTION_SWEEP = False # If True, the sanction cost is distributed to sustainable fishers

########### Create dataclasses for Patch and Fisher ###########
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
    """Fishers are the agents that interact with each other and the patches by catching fish."""
    x_position: int
    y_position: int
    strategy: str
    current_strategy: str
    catch: float = 0.0
    total_catch: float = 0.0
    sanction_cost: float = 0.0
    
    ################### Catching Fish ###################
    # Fisher catches fish from current patch based on their strategy:
    def catch_fish(self, patch, neighbors):
        """Fisher catches fish from the current patch based on their strategy and neighbors."""
        self.catch = 0.0 # Reset catch before calculating new catch based on strategy

        ############## Egoist ###############
        # Egoists catch as much as possible from their current patch:
        if self.strategy == "egoist":
            self.catch = patch.biomass
        
        ########### Cooperator ##############
        # Cooperators cooperate if there are not too many egoists in the sight radius.
        # Else they behave like egoists. When there are no neighbors, they also cooperate.
        elif self.strategy == "cooperator":
            number_cooperative = sum(1 for neighbor in neighbors if is_cooperative(neighbor))

            if len(neighbors) == 0:
                # If there are no neighbors, cooperators cooperate:
                self.catch = SUSTAINABLE_CATCH_MULTIPLIER * patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
            else:
                if (number_cooperative / len(neighbors)) * 100 > COOPERATION_THRESHOLD:
                    # Cooperation means catching as much as the growth of the patch:
                    self.catch = SUSTAINABLE_CATCH_MULTIPLIER * patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
                else:
                    # If too many egoists are around, cooperators behave like egoists:
                    self.catch = patch.biomass
        
        ############ Imitator ##############
        # Imitators look at their neighbors in the sight radius and imitate the strategy of the neighbor with the highest total catch, 
        # if that catch is higher than their own total catch. If there are no neighbors, they keep their current strategy. 
        # After potentially changing their strategy, they catch fish according to their (possibly new) strategy.
        elif self.strategy == "imitator":
            best_strategy = self.current_strategy
            best_total_catch = self.total_catch

            # Comparing the total catch of the neighbors to find the best strategy in the sight radius:
            if len(neighbors) != 0:
                for neighbor in neighbors:
                    if neighbor.total_catch > best_total_catch:
                        best_total_catch = neighbor.total_catch
                        # Best strategy is the strategy of the neighbor with the highest total catch:
                        best_strategy = neighbor.current_strategy
                
                # Imitator adopts the best strategy in sight if it is better than its own total catch:
                self.current_strategy = best_strategy

            # Now the imitator catches fish according to its current strategy, which could have changed after looking at the neighbors:
            if self.current_strategy == "egoist":
                self.catch = patch.biomass
            elif self.current_strategy in ["cooperator", "sanctioner"]:
                self.catch = SUSTAINABLE_CATCH_MULTIPLIER * patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))

        ########### Sanctioner ##############
        # Sanctioners behave like cooperators, but they also sanction egoists in their sight radius by reducing their catch.
        elif self.strategy == "sanctioner":
            self.catch = SUSTAINABLE_CATCH_MULTIPLIER * patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))


    ############### Moving Fishers ###############
    def move(self, fishers, grid):
        """Moves the fisher to a neighboring patch, that is not occupied by another fisher."""

        # Define possible grid states around the fisher and check if they are occupied by other fishers:
        occupied = {(f.x_position, f.y_position) for f in fishers if f is not self}

        candidates = [
            (max(0, min(WIDTH - 1, self.x_position + dx)),
             max(0, min(LENGTH - 1, self.y_position + dy)))
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if (dx, dy) != (0, 0)
        ]

        free = [pos for pos in candidates if pos not in occupied]

        if free:
            if random.random() < RANDOM_MOVE_CHANCE:
                self.x_position, self.y_position = random.choice(free) # move to a random free patch
            else:
                best_position = max(free, key=lambda pos: grid[pos[1]][pos[0]].biomass) # move to the patch with the most biomass
                self.x_position, self.y_position = best_position


############### Initialization ###############
# Initialization function to set up the lake-grid and the fishers:
def initialize(initial_counts = None):
    """Initializes the grid of patches and the list of fishers."""
    # Create a grid of patches:
    grid = []
    for y in range(LENGTH):
        row = []
        for x in range(WIDTH):
            biomass = random.uniform(0, 100)
            patch = Patch(biomass=biomass, capacity=CAPACITY, growth_rate=GROWTH_RATE)
            row.append(patch)
        grid.append(row)

    # Create a list of fishers:
    fishers = []

    # Check if initial counts for strategies are provided and valid, otherwise initialize with random strategies:
    use_initial_counts = initial_counts is not None and all(count is not None for count in initial_counts.values())
    if use_initial_counts:
        counts = {s: initial_counts[s] if initial_counts[s] is not None else 0 for s in STRATEGIES}
        print(f"Initial counts provided: {counts}")

        for strategy, count in counts.items():
            for _ in range(count):
                x = random.randint(0, WIDTH - 1)
                y = random.randint(0, LENGTH - 1)
                if strategy == "imitator":
                    current_strategy = random.choice(["egoist", "cooperator", "sanctioner"])
                else:
                    current_strategy = strategy
                fisher = Fisher(x_position=x, y_position=y, strategy=strategy, current_strategy=current_strategy)
                fishers.append(fisher)
    else: 
        print(f"No initial counts provided, initializing fishers with random strategies.")
        for i in range(NUM_FISHERS):
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, LENGTH - 1)
            strategy = random.choice(STRATEGIES)

            # Imitators start with a random strategy
            if strategy == "imitator":
                current_strategy = random.choice(["egoist", "cooperator", "sanctioner"]) 
            else:
                current_strategy = strategy
            fisher = Fisher(x_position=x, y_position=y, strategy=strategy, current_strategy=current_strategy)
            fishers.append(fisher)
        
    # Move fishers to ensure they don't start on the same patch
    for fisher in fishers:
        fisher.move(fishers, grid) 

    return grid, fishers


############## Sensing and Interaction ##############
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
    
# Helper function to apply sanctions by sanctioners to egoists in their sight radius:
def apply_sanctions(fishers):
    sustainable_catch = GROWTH_RATE * CAPACITY * 0.5
    total_subsidy_pool = 0.0

    for sanctioner in fishers:
        if sanctioner.strategy != "sanctioner":
            continue

        # Check for neighbors to sanction:
        neighbors = get_neighbors(sanctioner, fishers)
        for neighbor in neighbors:
            if neighbor.catch > SANCTION_THRESHOLD * sustainable_catch:
                confiscated_fish = min(SANCTION_COST, neighbor.catch) 
                neighbor.catch -= confiscated_fish

                # Distribution Sweep: Sanction cost is distributed to sustainable fishers
                if DISTRIBUTION_SWEEP:
                    keep_amount = confiscated_fish * SANCTIONER_KEEP_RATIO
                    subsidy_amount = confiscated_fish * (1 - SANCTIONER_KEEP_RATIO)
                    sanctioner.total_catch += keep_amount
                    total_subsidy_pool += subsidy_amount

    if DISTRIBUTION_SWEEP and total_subsidy_pool > 0:
        sustainable_fishers = [f for f in fishers if f.catch <= SANCTION_THRESHOLD * sustainable_catch]
        if len(sustainable_fishers) > 0:
            share_per_fisher = total_subsidy_pool / len(sustainable_fishers)
            for f in sustainable_fishers:
                f.catch += share_per_fisher
                
############ Diffusion of Biomass ############
def diffuse_biomass(grid):
    """Calculates the diffusion of biomass between the patches (Moore neighborhood)."""
    # 1. Create temporary grid to store new biomass values after diffusion, starting with current biomass values:
    new_biomass_grid = [[patch.biomass for patch in row] for row in grid]
    
    # 2. Calculate diffusion for each patch based on the average biomass of its neighbors:
    for y in range(LENGTH):
        for x in range(WIDTH):
            current_biomass = grid[y][x].biomass
            
            # Look for neighbours
            neighbor_biomass_sum = 0.0
            neighbor_count = 0
            
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue # Skip the current patch itself
                    
                    nx, ny = x + dx, y + dy
                    # Check if neighbor coordinates are within grid bounds
                    if 0 <= nx < WIDTH and 0 <= ny < LENGTH:
                        neighbor_biomass_sum += grid[ny][nx].biomass
                        neighbor_count += 1
            
            if neighbor_count > 0:
                # Calculate the average biomass of the neighbors
                neighbor_average = neighbor_biomass_sum / neighbor_count
                
                # Formula: New Value = Current Value + Diffusion Coefficient * (Average - Current Value)
                # This ensures that biomass flows from "full" to "empty" patches.
                new_biomass = current_biomass + DIFFUSION_COEFFICIENT * (neighbor_average - current_biomass)
                new_biomass_grid[y][x] = max(0.0, min(CAPACITY, new_biomass))

    # 3. Copy the new biomass values back to the original grid:
    for y in range(LENGTH):
        for x in range(WIDTH):
            grid[y][x].biomass = new_biomass_grid[y][x]


################# Step Function #################
# Step function simulates one time step of the model. Biomass grows, fishers catch fish.
def step(grid, fishers):
    """Advances the simulation by one step, updating biomass, fishing, sanctions
    and strategies."""

# At first, biomass grows in each patch and diffuses to neighboring patches:
    diffuse_biomass(grid)
    # Update the biomass of each patch:
    for row in grid:
        for patch in row:
            patch.grow()
    
    # Each fisher catches fish from current patch:
    for fisher in fishers:
        patch = grid[fisher.y_position][fisher.x_position]
        neighbors = get_neighbors(fisher, fishers)
        fisher.catch_fish(patch, neighbors)
        
        fisher.catch = min(fisher.catch, patch.biomass) # Catch cannot be more than the available biomass
        patch.biomass -= fisher.catch
        patch.biomass = max(0.0, patch.biomass) # Biomass cannot be negative
       
    # After all fishers have caught fish, sanctioners apply sanctions to egoists in their sight radius:
    apply_sanctions(fishers)

    # After sanctions, we update the total catch of each fisher by adding the catch of this step to their total catch:
    for fisher in fishers:
        fisher.total_catch += fisher.catch
        
    # After all fishers have caught fish, they move to a new patch:
    for fisher in fishers:
        fisher.move(fishers, grid)


############ Visualization ############
def visualize_simulation(steps = SIMULATION_STEPS, initial_counts = None):
    """Visualizes the simulation live and allows to pause by pressing the spacebar."""
    history = {
        "biomass": [],
        "catch": {s: [] for s in STRATEGIES},
        "cum_catch": {s: [] for s in STRATEGIES},
        "counts": {s: [] for s in STRATEGIES}
    }   
    

    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(1, 2, 1) # Mainplot for the grid
    ax_biomass = fig.add_subplot(4, 2, 2)   # Biomass upper right
    ax_current = fig.add_subplot(4, 2, 4)    # Current catch second row right
    ax_catch = fig.add_subplot(4, 2, 6)    # Total catch third row right
    ax_strategies = fig.add_subplot(4, 2, 8) # Strategies bottom right

    # Pause function using a mutable type (list) to allow modification inside the event handler
    is_paused = [False]
    current_step = [0]
    grid, fishers = initialize(initial_counts = initial_counts) 
    cbar = None

    # Define a color map for the different strategies to use in the scatter plot:
    color_map = {
        "egoist": "red",
        "cooperator": "blue",
        "sanctioner": "green",
        "imitator": "gold"
    }

    # Event handler for key presses to toggle pause when spacebar is pressed:
    def on_press(event):
        if event.key == ' ':
            is_paused[0] = not is_paused[0]
            fig.canvas.draw()

    # Update function to advance the simulation and update the visualization at each step:
    def update(*args, **kwargs):
        nonlocal cbar
        if current_step[0] >= steps:
            timer.stop()
            return

        if not is_paused[0]:
            step(grid, fishers)

        ax.clear()

        # Create a matrix of biomass values for the heatmap:
        biomass_matrix = [[patch.biomass for patch in row] for row in grid]
        im = ax.imshow(biomass_matrix, cmap='YlGn', origin='lower', vmin=0, vmax=CAPACITY)
        # Add colorbar
        if cbar is None:
            cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.7)
            cbar.set_label('Biomass (Fish Stock)', rotation=270, labelpad=15)

        # Group fishers by strategy for plotting
        strategy_groups = {strat: ([], []) for strat in STRATEGIES}
        for f in fishers:
            strategy_groups[f.strategy][0].append(f.x_position)
            strategy_groups[f.strategy][1].append(f.y_position)

        for strategy, (xs, ys) in strategy_groups.items():
            if xs:
                ax.scatter(xs, ys, c=color_map[strategy], label=strategy, 
                           s=100, edgecolors='black', zorder=3)
        
        # Set title and labels
        ax.set_title(f"Flat-Lake Simulation - Step {current_step[0] + 1}/{steps}", fontsize=14, pad=25)

        if is_paused[0]:
            ax.text(0.5, 1.03, "[ PAUSED ] - Press spacebar to resume", 
                    transform=ax.transAxes, color="red", weight="bold", ha="center", va="bottom")
        else:
            ax.text(0.5, 1.03, "Tip: Press [ spacebar ] to pause", 
                    transform=ax.transAxes, color="gray", style="italic", ha="center", va="bottom")
        
        ax.set_xlabel("X-Coordinate")
        ax.set_ylabel("Y-Coordinate")
        ax.set_xlim(-0.5, WIDTH - 0.5)
        ax.set_ylim(-0.5, LENGTH - 0.5)
        ax.legend(loc='upper center', bbox_to_anchor = (0.5, -0.12), ncol = 4, frameon = True, fontsize = 10)

        if not is_paused[0]:
            ##### Update history for plots #####
            history["biomass"].append(sum(patch.biomass for row in grid for patch in row) / (WIDTH * LENGTH))

            # Update current catch and cumulative catch for each strategy, as well as the count of fishers using each strategy:
            for s in STRATEGIES:
                fishers_of_strategy = [f for f in fishers if f.strategy == s]
                count = len(fishers_of_strategy)
                current_catch_sum = sum(f.catch for f in fishers_of_strategy) / count if count > 0 else 0
                history["catch"][s].append(current_catch_sum)

                total_group_catch = sum(f.total_catch for f in fishers_of_strategy) / count if count > 0 else 0
                history["cum_catch"][s].append(total_group_catch)

            for s in ["egoist", "cooperator", "sanctioner"]:
                history["counts"][s].append(sum(1 for f in fishers if f.current_strategy == s))


        ##### Update the plots on the right side #####
        x = list(range(len(history["biomass"])))

        ax_biomass.clear()
        ax_biomass.plot(x, history["biomass"], color="green")
        ax_biomass.set_title("Ø Biomass", fontsize=9)
        ax_biomass.set_ylabel("Biomass")
        ax_biomass.grid(True, linestyle=':', alpha=0.5)

        ax_current.clear()
        for s in STRATEGIES:
            ax_current.plot(x, history["catch"][s], color=color_map[s],linewidth=1.5)
        ax_current.set_title("Current Catch per Capita", fontsize=9)
        ax_current.set_ylabel("Catch")
        ax_current.grid(True, linestyle=':', alpha=0.5)

        ax_catch.clear()
        for s in STRATEGIES:
            ax_catch.plot(x, history["cum_catch"][s], color=color_map[s], linewidth=2, label=s)
        ax_catch.set_title("Cumulative Catch per Capita", fontsize=9)
        ax_catch.set_ylabel("Total Catch")
        ax_catch.grid(True, linestyle=':', alpha=0.5)
        ax_catch.legend(loc='upper left', fontsize=8)

        ax_strategies.clear()
        for s in ["egoist", "cooperator", "sanctioner"]:
            ax_strategies.plot(x, history["counts"][s], color=color_map[s], label=s)
        ax_strategies.set_title("Number of Strategies", fontsize=9)
        ax_strategies.set_ylabel("Count")
        ax_strategies.set_xlabel("Step")
        ax_strategies.legend(fontsize=7)
        ax_strategies.grid(True, linestyle=':', alpha=0.5)

        # Increment the current step and redraw the canvas to update the visualization:
        if not is_paused[0]:
            current_step[0] += 1
        fig.canvas.draw()

    # Connect the key press event to the on_press function and start the timer to update the simulation:
    fig.canvas.mpl_connect('key_press_event', on_press)
    timer = fig.canvas.new_timer(interval=100) # Update every 100 milliseconds (10 updates per second)
    timer.add_callback(update)
    timer.start()
    
    plt.tight_layout(pad=3.0)

    plt.show()

def main():
    random.seed(42) 
    # Set up command line arguments to allow users to specify initial conditions and activate distribution sweep for sanctions:
    global DISTRIBUTION_SWEEP

    # Create an argument parser to handle command line arguments for initial strategy counts and distribution sweep option
    parser = argparse.ArgumentParser(description="Flat Lake Simulation")
    parser.add_argument('--distribution-sweep', action='store_true', help='Activate distribution sweep for sanctions')
    parser.add_argument('--egoists', type=int, default = None, help='Initial number of egoist fishers')
    parser.add_argument('--imitators', type=int, default = None, help='Initial number of imitator fishers')
    parser.add_argument('--cooperators', type=int, default = None, help='Initial number of cooperator fishers')
    parser.add_argument('--sanctioners', type=int, default = None, help='Initial number of sanctioner fishers')
    
    args = parser.parse_args()
    DISTRIBUTION_SWEEP = args.distribution_sweep

    # Print initial status and settings for the simulation based on command line arguments
    print("Starting live visualization with interactive pause...")
    print("=" * 50)
    if DISTRIBUTION_SWEEP:
        print("STATUS: Distribution Sweep activated - Sanction costs will be distributed to sustainable fishers.")
    else:
        print("STATUS: Distribution Sweep deactivated - Sanction costs will be borne by sanctioners only.")

    initial_counts = {
        "egoist": args.egoists,
        "imitator": args.imitators,
        "cooperator": args.cooperators,
        "sanctioner": args.sanctioners
    }

    # Call the visualization function with the specified parameters
    visualize_simulation(steps = SIMULATION_STEPS, initial_counts = initial_counts)

if __name__ == "__main__":
    main()
