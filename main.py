from dataclasses import dataclass
import random
import math
import matplotlib.pyplot as plt

# Constants:
WIDTH = 20 # Width of the lake grid (x-axis)
LENGTH = 20 # Length of the lake grid (y-axis)
NUM_FISHERS = 20 # Number of fisher-agents in the simulation
CAPACITY = 100.0 # Carrying capacity of biomass in each lake-patch
GROWTH_RATE = 0.3 # Growth rate of biomass in each patch
STRATEGIES = ["egoist", "imitator", "cooperator", "sanctioner"]
DIFFUSION_COEFFICIENT = 0.1 # Coefficient for diffusion of biomass between patches
SIMULATION_STEPS = 100
SIGHT_RADIUS = 3 # Radius within which fishers can see and interact with other fishers
COOPERATION_THRESHOLD = 50 # Minimal percentage of cooperators or sanctioners in sight for cooperators to cooperate
SANCTION_COST = 10
PUNISHER_COST = 0.2
SANCTION_THRESHOLD = 1.2
NACHHALTIG_FISCHEN_ABER_PROFIT_EIN_BISSCHEN_AUSREIZEN = 5

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

    def move(self, fishers):
        """Moves the fisher to a random neighboring patch, that is not occupied by another fisher."""
        for _ in range(10): # Try max. 10 times to find a free patch, else stay
            # Moves to a random patch in Moore neighborhood or stay in place
            dx = random.choice([-1,0,1])
            dy = random.choice([-1,0,1])
            new_x = max(0, min(WIDTH - 1, self.x_position + dx))
            new_y = max(0, min(LENGTH - 1, self.y_position + dy))

            # Check if the new patch is already occupied:
            if not any(other.x_position == new_x and other.y_position == new_y for other in fishers if other is not self):
                self.x_position = new_x
                self.y_position = new_y
                break



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
            #current_strategy = "egoist" # Imitators start as egoists but can change their strategy later
            current_strategy = random.choice(["egoist", "cooperator", "sanctioner"]) #Gemini hat vorgeschlagen, Imitatoren zu Beginn auch zufällig wählen zu lassen
        else:
            current_strategy = strategy
        fisher = Fisher(x_position=x, y_position=y, strategy=strategy, current_strategy=current_strategy)
        fishers.append(fisher)
    
    for fisher in fishers:
        fisher.move(fishers) # Move fishers to ensure they don't start on the same patch

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

    for sanctioner in fishers:

        if sanctioner.strategy != "sanctioner":
            continue

        neighbors = get_neighbors(sanctioner, fishers)

        for neighbor in neighbors:

            if neighbor.catch > SANCTION_THRESHOLD * sustainable_catch:

                neighbor.total_catch -= SANCTION_COST #Kosten für regelbruch
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
        fisher.move(fishers)


def visualize_simulation(steps=SIMULATION_STEPS):
    """Führt die Simulation in einer Endlosschleife aus, erlaubt Pausen per Leertaste

    und startet nach Ablauf der Schritte automatisch von vorne.
    """
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Zustand für die Pausenfunktion
    is_paused = [False] # Liste, damit wir sie in der Event-Funktion modifizieren können

    # Event-Handler für Tastaturdrücke (Leertaste für Pause)
    def on_press(event):
        if event.key == ' ':
            is_paused[0] = not is_paused[0]
            if is_paused[0]:
                ax.set_title(f"{ax.get_title()} (PAUSIERT - Leertaste drücken)")
            fig.canvas.draw()

    fig.canvas.mpl_connect('key_press_event', on_press)

    color_map = {
        "egoist": "red",
        "cooperator": "blue",
        "sanctioner": "green",
        "imitator": "gold"
    }

    # UNENDLICHE SCHLEIFE: Startet immer wieder von vorne
    while True:
        # Jedes Mal, wenn wir von vorne starten, initialisieren wir den See & die Fischer neu
        grid, fishers = initialize()
        
        current_step = 0
        while current_step < steps:
            # Wenn pausiert ist, warten wir einfach und überspringen den Simulationsschritt
            if is_paused[0]:
                plt.pause(0.1)
                continue
                
            # 1. Simulationsschritt ausführen
            step(grid, fishers)
            
            # 2. Plot zurücksetzen
            ax.clear()
            
            # 3. Biomasse-Grid als Hintergrund (Heatmap)
            biomass_matrix = [[patch.biomass for patch in row] for row in grid]
            im = ax.imshow(biomass_matrix, cmap='YlGn', origin='lower', vmin=0, vmax=CAPACITY)
            
            if current_step == 0:
                # Colorbar nur beim ersten Frame des aktuellen Durchlaufs hinzufügen
                if not hasattr(visualize_simulation, '_cbar'):
                    visualize_simulation._cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.7)
                    visualize_simulation._cbar.set_label('Biomasse (Fischbestand)', rotation=270, labelpad=15)
            
            # 4. Fischer als Punkte zeichnen
            strategy_groups = {strat: ([], []) for strat in STRATEGIES}
            for f in fishers:
                strategy_groups[f.strategy][0].append(f.x_position)
                strategy_groups[f.strategy][1].append(f.y_position)
                
            for strategy, (xs, ys) in strategy_groups.items():
                if xs:
                    ax.scatter(xs, ys, c=color_map[strategy], label=strategy, 
                               s=100, edgecolors='black', zorder=3)
            
            # 5. Titel und Achsen
            
            ax.set_title(f"Flachsee Simulation - Schritt {current_step + 1}/{steps}", fontsize=14, pad=25)
            
            # KORREKTUR: Wir nutzen y=1.03 für eine feste, saubere Position über dem Grid
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
            ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
            
            # --- GESCHWINDIGKEIT RECODELN ---
            # Ändere diese Zahl, um es schneller (z.B. 0.01) oder langsamer (z.B. 0.5) zu machen:
            plt.pause(0.2) 
            
            current_step += 1
            
        print("Durchlauf beendet. Starte neuen Durchlauf...")
        plt.pause(1.5) # Kurze Verschnaufpause vor dem automatischen Neustart

    plt.ioff()
    plt.show()

def main():
    # Seed entfernen oder drin lassen (mit Seed sieht jeder Neustart exakt gleich aus!)
    # random.seed(42) 
    
    print("Starte Live-Visualisierung mit interaktiver Pause...")
    # Ruft die neue Visualisierung auf
    visualize_simulation(steps=SIMULATION_STEPS)

if __name__ == "__main__":
    main()

########
#Diagramme: Biomasse über Zeit, Total Catch (in Abh. der Strategien evtl. mit Imitator) über Zeit
#Anzahl der Strategien über Zeit
########
