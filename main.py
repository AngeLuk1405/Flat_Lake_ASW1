from dataclasses import dataclass
import random
import math
import matplotlib.pyplot as plt
import argparse

# Constants:
WIDTH = 20 # Width of the lake grid (x-axis)
LENGTH = 20 # Length of the lake grid (y-axis)
NUM_FISHERS = 20 # Number of fisher-agents in the simulation
CAPACITY = 100.0 # Carrying capacity of biomass in each lake-patch
GROWTH_RATE = 0.08 # Growth rate of biomass in each patch
STRATEGIES = ["egoist", "imitator", "cooperator", "sanctioner"]
DIFFUSION_COEFFICIENT = 0.1 # Coefficient for diffusion of biomass between patches
SIMULATION_STEPS = 100
SIGHT_RADIUS = 3 # Radius within which fishers can see and interact with other fishers
COOPERATION_THRESHOLD = 50 # Minimal percentage of cooperators or sanctioners in sight for cooperators to cooperate
SANCTION_COST = 10
PUNISHER_COST = 0.2
SANCTION_THRESHOLD = 1.2
NACHHALTIG_FISCHEN_ABER_PROFIT_EIN_BISSCHEN_AUSREIZEN = 5
RANDOM_MOVE_CHANCE = 0.2 # Chance that a fisher moves to a random patch instead of the best patch
SANCTIONER_KEEP_RATIO = 0.3 # part of the catch that sanctioners keep for themselves, when they sanction others
DISTRIBUTION_SWEEP = False # If True, the sanction cost is distributed to sustainable fishers

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
    
    # Fisher catches fish from current patch based on their strategy:
    def catch_fish(self, patch, neighbors):
        """Fisher catches fish from the current patch based on their strategy and neighbors."""
        self.catch = 0.0 # Reset catch before calculating new catch based on strategy

        # Egoist:
        if self.strategy == "egoist":
            # Egoists catch as much as possible from their current patch:
            self.catch = patch.biomass
        
        #Cooperator:
        elif self.strategy == "cooperator":
            # Cooperators cooperate if there are not too many egoists in the sight radius.
            # Else they behave like egoists.
            # When there are no neighbors, they also cooperate.
            number_cooperative =sum(1 for neighbor in neighbors if is_cooperative(neighbor))

            if len(neighbors) == 0:
                # If there are no neighbors, cooperators cooperate:
                    self.catch = NACHHALTIG_FISCHEN_ABER_PROFIT_EIN_BISSCHEN_AUSREIZEN * patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
            else:
                if (number_cooperative / len(neighbors)) * 100 > COOPERATION_THRESHOLD:
                    # Cooperation means catching as much as the growth of the patch:
                    self.catch = NACHHALTIG_FISCHEN_ABER_PROFIT_EIN_BISSCHEN_AUSREIZEN *patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
                    
                else:
                    # If too many egoists are around, cooperators behave like egoists:
                    self.catch = patch.biomass
        
        # Imitator:
        elif self.strategy == "imitator":
            # Wir starten den Vergleich mit uns selbst!
            best_strategy = self.current_strategy
            best_total_catch = self.total_catch

            # Wenn Nachbarn da sind, prüfen wir, ob jemand besser war als wir selbst
            if len(neighbors) != 0:
                for neighbor in neighbors:
                    if neighbor.total_catch > best_total_catch:
                        best_total_catch = neighbor.total_catch
                        # Wir merken uns die aktuelle Strategie des erfolgreicheren Nachbarn
                        best_strategy = neighbor.current_strategy
                
                # Wir übernehmen die Strategie des Besten (das können wir auch selbst sein)
                self.current_strategy = best_strategy
            
            # Wenn keine Nachbarn da sind (len(neighbors) == 0), 
            # bleibt self.current_strategy einfach unverändert.

            # Jetzt fischt der Imitator basierend auf seiner (eventuell neuen) Strategie:
            if self.current_strategy == "egoist":
                self.catch = patch.biomass
            elif self.current_strategy in ["cooperator", "sanctioner"]:
                self.catch = NACHHALTIG_FISCHEN_ABER_PROFIT_EIN_BISSCHEN_AUSREIZEN * patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))

        #Sanctioner:
        elif self.strategy == "sanctioner":
            self.catch = NACHHALTIG_FISCHEN_ABER_PROFIT_EIN_BISSCHEN_AUSREIZEN * patch.growth_rate * patch.biomass * (1 - (patch.biomass / patch.capacity))
        #########
        # Sanktionierer: wenn Fischer im Sichtradius Egoisten sind -> STRAFE
        # Strafe auf alle verteilt oder auf die Kooperierer verteilt
        #########

    def move(self, fishers, grid):
        """Moves the fisher to a  neighboring patch, that is not occupied by another fisher."""

        # Alternative: Always move to a random neighbouring patch (without 10 tries)
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

# Initialization function to set up the lake-grid and the fishers:
def initialize():
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
    for i in range(NUM_FISHERS):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, LENGTH - 1)
        strategy = random.choice(STRATEGIES)  ####Evtl nicht random sondern bestimmte Anteile
        if strategy == "imitator":
            #current_strategy = "egoist" # Imitators start as egoists but can change their strategy later
            current_strategy = random.choice(["egoist", "cooperator", "sanctioner"]) #Gemini hat vorgeschlagen, Imitatoren zu Beginn auch zufällig wählen zu lassen
        else:
            current_strategy = strategy
        fisher = Fisher(x_position=x, y_position=y, strategy=strategy, current_strategy=current_strategy)
        fishers.append(fisher)
    
    for fisher in fishers:
        fisher.move(fishers, grid) # Move fishers to ensure they don't start on the same patch

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
        
def apply_sanctions(fishers):

    sustainable_catch = GROWTH_RATE * CAPACITY * 0.5

    total_subsidy_pool = 0.0
    sustainable_fishers = []


    for sanctioner in fishers:
        if sanctioner.strategy != "sanctioner":
            continue

        neighbors = get_neighbors(sanctioner, fishers)
        for neighbor in neighbors:
            if neighbor.catch > SANCTION_THRESHOLD * sustainable_catch:
                neighbor.total_catch -= SANCTION_COST #Kosten für regelbruch

                if DISTRIBUTION_SWEEP:
                    keep_amount = SANCTION_COST * SANCTIONER_KEEP_RATIO
                    subsidy_amount = SANCTION_COST * (1 - SANCTIONER_KEEP_RATIO)
                    sanctioner.total_catch += (keep_amount - PUNISHER_COST)
                    total_subsidy_pool += subsidy_amount
                else:
                    sanctioner.total_catch -= PUNISHER_COST
                
                sanctioner.sanction_cost += PUNISHER_COST

        if DISTRIBUTION_SWEEP:
            for f in fishers:
                if f.catch <= SANCTION_THRESHOLD * sustainable_catch:
                    sustainable_fishers.append(f)

            if total_subsidy_pool > 0 and len(sustainable_fishers) > 0:
                share_per_fisher = total_subsidy_pool / len(sustainable_fishers)
                for f in sustainable_fishers:
                    f.total_catch += share_per_fisher


#kosten für die durchführung der sanktion
                sanctioner.total_catch -= PUNISHER_COST
                sanctioner.sanction_cost += PUNISHER_COST
                

def diffuse_biomass(grid):
    """Berechnet die Diffusion der Biomasse zwischen den Patches (Moore-Nachbarschaft)."""
    # 1. Temporäres Grid erstellen, um Werte aus 'Tick-1' einzufrieren
    new_biomass_grid = [[patch.biomass for patch in row] for row in grid]
    
    # 2. Diffusion berechnen

    for y in range(LENGTH):
        for x in range(WIDTH):
            current_biomass = grid[y][x].biomass
            
            # Nachbarn suchen (Ränder werden berücksichtigt)
            neighbor_biomass_sum = 0.0
            neighbor_count = 0
            
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue # Das eigene Feld überspringen
                    
                    nx, ny = x + dx, y + dy
                    # Prüfen, ob der Nachbar innerhalb der Grid-Grenzen liegt
                    if 0 <= nx < WIDTH and 0 <= ny < LENGTH:
                        neighbor_biomass_sum += grid[ny][nx].biomass
                        neighbor_count += 1
            
            if neighbor_count > 0:
                # Durchschnitt der Nachbarn berechnen
                neighbor_average = neighbor_biomass_sum / neighbor_count
                
                # Formel: Neuer Wert = Aktueller Wert + Diffusionskoeffizient * (Durchschnitt - Aktueller Wert)
                # Das sorgt dafür, dass Biomasse von "voll" nach "leer" fließt.
                new_biomass = current_biomass + DIFFUSION_COEFFICIENT * (neighbor_average - current_biomass)
                new_biomass_grid[y][x] = max(0.0, min(CAPACITY, new_biomass))

    # 3. Die berechneten Werte in das echte Grid zurückschreiben
    for y in range(LENGTH):
        for x in range(WIDTH):
            grid[y][x].biomass = new_biomass_grid[y][x]


# Step function simulates one time step of the model. Biomass grows, fishers catch fish.
# Sanctioner strategy, and diffusion are yet to be implemented!
# For now imitators behave like egoists and sanctioners like cooperators.
def step(grid, fishers):
    """Advances the simulation by one step, updating biomass, fishing, sanctions
    and strategies."""

# --- NEU: Zuerst diffundiert die Biomasse zwischen den Zellen ---
    diffuse_biomass(grid)
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
       
    apply_sanctions(fishers)
        
    # After all fishers have caught fish, they move to a new patch:
    for fisher in fishers:
        fisher.move(fishers, grid)


def visualize_simulation(steps=SIMULATION_STEPS):
    """Visulaizes the simulation live an allows to pause by pressing the spacebar."""
    history = {
        "biomass": [],
        "catch": {s: [] for s in STRATEGIES},
        "cum_catch": {s: [] for s in STRATEGIES},
        "counts": {s: [] for s in STRATEGIES}
    }   
    

    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(1, 2, 1) # Hauptplot für die Biomasse und die Positionen der Fischer
    ax_biomass = fig.add_subplot(4, 2, 2)   # Biomasse oben rechts
    ax_current = fig.add_subplot(4, 2, 4)    # Catch mitte rechts
    ax_catch = fig.add_subplot(4, 2, 6)    # Catch mitte rechts
    ax_strategies = fig.add_subplot(4, 2, 8) # Strategien unten rechts

    # ax_cum = {}
    # for i, s in enumerate(STRATEGIES):
    #     ax_cum[s] = plt.subplot2grid((4, 3), (i, 2))


    # Zustand für die Pausenfunktion
    is_paused = [False] # Liste, damit wir sie in der Event-Funktion modifizieren können
    current_step = [0]
    grid, fishers = initialize() 
    cbar = None

    color_map = {
        "egoist": "red",
        "cooperator": "blue",
        "sanctioner": "green",
        "imitator": "gold"
    }

    # Event-Handler für Tastaturdrücke (Leertaste für Pause)
    def on_press(event):
        if event.key == ' ':
            is_paused[0] = not is_paused[0]
            fig.canvas.draw()


    def update(*args, **kwargs):
        nonlocal cbar
        if is_paused[0]:
            return
        
        if current_step[0] >= steps:
            timer.stop()
            return
        
        step(grid, fishers)
        ax.clear()

        biomass_matrix = [[patch.biomass for patch in row] for row in grid]
        im = ax.imshow(biomass_matrix, cmap='YlGn', origin='lower', vmin=0, vmax=CAPACITY)

        if cbar is None:
            cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.7)
            cbar.set_label('Biomasse (Fischbestand)', rotation=270, labelpad=15)

        strategy_groups = {strat: ([], []) for strat in STRATEGIES}
        for f in fishers:
            strategy_groups[f.strategy][0].append(f.x_position)
            strategy_groups[f.strategy][1].append(f.y_position)

        for strategy, (xs, ys) in strategy_groups.items():
            if xs:
                ax.scatter(xs, ys, c=color_map[strategy], label=strategy, 
                           s=100, edgecolors='black', zorder=3)
        
        ax.set_title(f"Flat-Lake simulation - Step {current_step[0] + 1}/{steps}", fontsize=14, pad=25)

        if is_paused[0]:
            ax.text(0.5, 1.03, "[ PAUSIERT ] - Leertaste drücken zum Fortsetzen", 
                    transform=ax.transAxes, color="red", weight="bold", ha="center", va="bottom")
        else:
            ax.text(0.5, 1.03, "Tipp: [ Leertaste ] drücken zum Pausieren", 
                    transform=ax.transAxes, color="gray", style="italic", ha="center", va="bottom")
        
        ax.set_xlabel("X-Koordinate")
        ax.set_ylabel("Y-Koordinate")
        ax.set_xlim(-0.5, WIDTH - 0.5)
        ax.set_ylim(-0.5, LENGTH - 0.5)
        ax.legend(loc='upper center', bbox_to_anchor = (0.5, -0.12), ncol = 4, frameon = True, fontsize = 10)

        # Daten sammeln
        history["biomass"].append(sum(patch.biomass for row in grid for patch in row) / (WIDTH * LENGTH))

        for s in STRATEGIES:
            fishers_of_strategy = [f for f in fishers if f.strategy == s]
            current_catch_sum = sum(f.catch for f in fishers_of_strategy)
            history["catch"][s].append(current_catch_sum)

            total_group_catch = sum(f.total_catch for f in fishers_of_strategy)
            history["cum_catch"][s].append(total_group_catch)

        for s in ["egoist", "cooperator", "sanctioner"]:
            history["counts"][s].append(sum(1 for f in fishers if f.current_strategy == s))

        # Diagramme zeichnen
        x = list(range(len(history["biomass"])))

        ax_biomass.clear()
        ax_biomass.plot(x, history["biomass"], color="green")
        ax_biomass.set_title("Ø Biomasse pro Schritt", fontsize=9)
        ax_biomass.set_ylabel("Biomasse")

        ax_current.clear()
        for s in STRATEGIES:
            ax_current.plot(x, history["catch"][s], color=color_map[s],linewidth=1.5)
        ax_current.set_title("Aktueller Fang pro Schritt", fontsize=9)
        ax_current.set_ylabel("Fang")
        ax_current.grid(True, linestyle=':', alpha=0.5)

        ax_catch.clear()
        for s in STRATEGIES:
            ax_catch.plot(x, history["cum_catch"][s], color=color_map[s], linewidth=2, label=s)
        ax_catch.set_title("Kumulativer Fang pro Schritt", fontsize=9)
        ax_catch.set_ylabel("Gesamtertrag")
        ax_catch.grid(True, linestyle=':', alpha=0.5)
        ax_catch.legend(loc='upper left', fontsize=8)

        ax_strategies.clear()
        for s in ["egoist", "cooperator", "sanctioner"]:
            ax_strategies.plot(x, history["counts"][s], color=color_map[s], label=s)
        ax_strategies.set_title("Anzahl Strategien", fontsize=9)
        ax_strategies.set_ylabel("Anzahl")
        ax_strategies.set_xlabel("Schritt")
        ax_strategies.legend(fontsize=7)

        current_step[0] += 1
        fig.canvas.draw()

    fig.canvas.mpl_connect('key_press_event', on_press)
    timer = fig.canvas.new_timer(interval=200) # Update alle 200 ms
    timer.add_callback(update)
    timer.start()
    
    plt.tight_layout()

    plt.show()

def main():
    # Seed entfernen oder drin lassen (mit Seed sieht jeder Neustart exakt gleich aus!)
    # random.seed(42) 
    global DISTRIBUTION_SWEEP

    parser = argparse.ArgumentParser(description="Flat Lake Simulation")
    parser.add_argument('--distribution-sweep', action='store_true', help='Activate distribution sweep for sanctions')
    parser.add_argument('--egoists', type=int, default = None, help='Initial number of egoist fishers')
    parser.add_argument('--imitators', type=int, default = None, help='Initial number of imitator fishers')
    parser.add_argument('--cooperators', type=int, default = None, help='Initial number of cooperator fishers')
    parser.add_argument('--sanctioners', type=int, default = None, help='Initial number of sanctioner fishers')
    
    
    args = parser.parse_args()
    DISTRIBUTION_SWEEP = args.distribution_sweep

    print("Starte Live-Visualisierung mit interaktiver Pause...")
    print("=" * 50)
    if DISTRIBUTION_SWEEP:
        print("STATUS: Distribution Sweep activated - Sanction costs will be distributed to sustainable fishers.")
    else:
        print("STATUS: Distribution Sweep deactivated - Sanction costs will be borne by sanctioners only.")
    
    # Ruft die neue Visualisierung auf
    visualize_simulation(steps=SIMULATION_STEPS)

if __name__ == "__main__":
    main()
