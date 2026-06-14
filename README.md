# Fischerei und Allmende - Flat Lake

*English version below*

Dieses Projekt untersucht die Nutzung einer gemeinsam genutzten Fischerei-Ressource (Common-Pool Resource) mithilfe eines agentenbasierten Modells. Ziel ist es zu analysieren, unter welchen Bedingungen ein Fischbestand langfristig erhalten bleibt oder durch Übernutzung kollabiert.

Die Simulation basiert auf den theoretischen Ansätzen von **Garrett Hardin** („Tragedy of the Commons“) und **Elinor Ostrom** (gemeinschaftliche Ressourcenverwaltung). Dabei wird untersucht, wie unterschiedliche Verhaltensstrategien von Fischern die Entwicklung einer gemeinsamen Ressource beeinflussen.

## Modellbeschreibung

Der See wird als zweidimensionales Gitter von Patches modelliert, auf denen sich Fischbiomasse durch logistisches Wachstum regeneriert und zwischen benachbarten Patches diffundiert. Fischer bewegen sich auf diesem Gitter, entnehmen Fischbestände und interagieren mit anderen Fischern in ihrem Sichtradius.

Das Modell beinhaltet vier **Agententypen**:
- **Egoisten** fangen so viel wie möglich vom aktuellen Patch.
- **Kooperatoren** fischen nachhaltig wenn ihre Nachbarn das auch mehrheitlich tun, andernfalls handeln sie wie Egoisten.
- **Imitatoren** betrachten alle Fischer im Sichtradius und übernehmen die Fang-Strategie desjenigen mit dem höchsten kumulativen Fang.
- **Sanktionierer** fischen nachhaltig und bestrafen Fischer im Sichtradius, deren Fang einen Schwellenwert überschreitet, indem sie einen Teil des Fangs konfiszieren.

Die Simulation läuft als Live-Visualisierung, die das See-Gitter mit der aktuellen Biomasse und die Positionen der Fisher anzeigt. Zusätzlich werden Biomasse, aktuelle und kumulative Fangmengen sowie die Anzahl der Fischer pro Strategie über die Zeit geplottet.

## Parameter
Die folgenden Parameter sind in `main.py` definiert und können dort angepasst werden.

| Parameter | Bedeutung | Wert |
|---|---|---|
| `WIDTH` | Breite des See-Gitters | 20 |
| `LENGTH` | Länge des See-Gitters | 20 |
| `NUM_FISHERS` | Anzahl der Fischer | 20 |
| `CAPACITY` | Tragfähigkeit an Biomasse pro Patch | 100 |
| `GROWTH_RATE` | Wachstumsrate der Biomasse pro Patch | 0.08 |
|`DIFFUSION_COEFFICIENT`| Koeffizient für die Diffusion der Biomasse zwischen Patches | 0.1 |
| `SIMULATION_STEPS` | Anzahl der Simulationsschritte (Simulationsdauer) | 300 |
| `SIGHT_RADIUS` | Sichtradius, in dem ein Fischer Nachbaren wahrnimmt | 3 |
|`COOPERATION_THRESHOLD`| *Kooperator*: Mindestanteil der kooperativen Nachbarn, um als Kooperator zu fungieren | 0.5 |
|`SANCTION_COST`| *Sanktionierer*: maximale Menge an konfisziertem Fang | 10 |
|`SANCTION_THRESHOLD`| *Sanktionierer*: Faktor, um den der Fang die nachhaltige Fangmenge überschreiten muss, um sanktioniert zu werden | 1.2 |
|`SUSTAINABLE_CATCH_MULTIPLIER`| Multiplikator für die nachhaltige Fangmenge  | 5 |
|`RANDOM_MOVE_CHANCE`| Wahrscheinlichkeit, dass sich ein Fischer zufällig bewegt, statt auf den besten Nachbar-Patch | 0.2 |
| `SANCTIONER_KEEP_RATIO` | *Sanktionierer*: Anteil des konfiszierten Fangs, der vom Sanktionierer behalten wird (bei aktivem `DISTRIBUTION_SWEEP`) | 0.5 |
|`DISTRIBUTION_SWEEP`| Aktiviert den Verteilungsmechanismus für konfiszierten Fang | False |

## Verwendung

Benötigt [UV](https://github.com/astral-sh/uv).\
<br>
Beim Ausführen öffnet sich ein matplotlib-Fenster mit der Live-Simulation. Links wird das See-Gitter mit der aktuellen Biomasse durch Farbintensität dargestellt, die Positionen der Fischer sind als Punkte markiert (Farbe entsprechend der Strategie). Rechts werden Biomasse, aktueller und kumulativer Fang sowie die Strategieverteilung der Fischer über die Zeit in Diagrammen dargestellt.

```bash
# Zufällige Strategieverteilung
uv run main.py

# Strategieanzahlen festlegen
# Beispiel: 5 Fischer je Strategie
uv run main.py --egoists 5 --cooperators 5 --sanctioners 5 --imitators 5

# Beispiel: 20 Egoisten
uv run main.py --egoists 20 --cooperators 0 --sanctioners 0 --imitators 0
```

Der `--distribution-sweep` Parameter aktiviert einen optionalen Mechanismus, bei dem konfiszierter Fang nicht einfach verschwindet, sondern anteilig an alle nachhaltigen Fischer verteilt wird.

```bash
# Mit Distribution Sweep
uv run main.py --egoists 4 --cooperators 6 --sanctioners 6 --imitators 4 --distribution-sweep
```

**Leertaste** drücken zum Pausieren/Fortsetzen.

---
<br>
<br>

# Flat-Lake (English)

This project investigates the use of a shared fishery resource (common-pool resource) using an agent-based model. The goal is to analyze under which conditions a fish stock remains sustainable or collapses due to overexploitation.

The simulation is based on the theoretical frameworks of **Garrett Hardin** ("Tragedy of the Commons") and **Elinor Ostrom** (community-based resource management). It examines how different behavioral strategies among fishers influence the development of a shared resource.

## Model description

The lake is modeled as a two-dimensional grid of patches, where fish biomass regenerates through logistic growth and diffuses between neighboring patches. Fishers move across the grid, harvest fish stocks, and interact with other fishers within their sight radius.

The model includes four **agent types**:
- **Egoists** catch as much as possible from the current patch.
- **Cooperators** fish sustainably as long as the majority of their neighbors do the same, otherwise they act like egoists.
- **Imitators** observe all fishers within their sight radius and adopt the strategy of the one with the highest cumulative catch.
- **Sanctioners** fish sustainably and penalize fishers within their sight radius whose catch exceeds a threshold by confiscating part of their haul.

The simulation runs as a live visualization showing the Lake grid with current biomass and the positions of the fishers. Additionally, biomass, current and cumulative catches as well as the number of fishers per strategy are plotted over time.

## Parameters
The following parameters are defined in `main.py` and can be adjusted there.

| Parameter | Meaning | Value |
|---|---|---|
| `WIDTH` | Width of the lake grid | 20 |
| `LENGTH` | Length of the lake grid | 20 |
| `NUM_FISHERS` | Number of fishers | 20 |
| `CAPACITY` | Carrying capacity of biomass per patch | 100 |
| `GROWTH_RATE` | Growth rate of biomass per patch | 0.08 |
|`DIFFUSION_COEFFICIENT`| Coefficient for diffusion of biomass between patches | 0.1 |
| `SIMULATION_STEPS` | Number of simulation steps (simulation time) | 300 |
| `SIGHT_RADIUS` | Sight radius within which fishers can see and interact with other fishers | 3 |
|`COOPERATION_THRESHOLD`| *Cooperator*: Minimal percentage of cooperative neighbors in sight to behave cooperatively | 0.5 |
|`SANCTION_COST`| *Sanctioner*: maximum amount of confiscated catch | 10 |
|`SANCTION_THRESHOLD`| *Sanctioner*: Factor by which a fisher's catch must exceed the sustainable catch to be sanctioned | 1.2 |
|`SUSTAINABLE_CATCH_MULTIPLIER`| Multiplier for the sustainable catch | 5 |
|`RANDOM_MOVE_CHANCE`| Chance that a fisher moves to a random neighboring patch instead of the best neighboring patch | 0.2 |
| `SANCTIONER_KEEP_RATIO` | *Sanctioner*: Portion of confiscated catch that sanctioners keep for themselves (when `DISTRIBUTION_SWEEP` is active) | 0.5 |
|`DISTRIBUTION_SWEEP`| Activates the distribution mechanism for confiscated catch | False |

## Usage

Requires [UV](https://github.com/astral-sh/uv).\
<br>
Running the simulation opens a matplotlib window with the live simulation. On the left, the lake grid is shown with current biomass represented by color intensity, and the positions of the fishers marked as points (color corresponding to strategy). On the right biomass, current and cumulative catch as well as the strategy distribution of the fishers are plotted over time.

```bash
# Random strategy distribution
uv run main.py

# Specify strategy counts
# Example: 5 fishers per strategy
uv run main.py --egoists 5 --cooperators 5 --sanctioners 5 --imitators 5

# Example: 20 egoists
uv run main.py --egoists 20 --cooperators 0 --sanctioners 0 --imitators 0
```

The `--distribution-sweep` flag activates an optional mechanism where confiscated catch is not simply removed but redistributed proportionally to all sustainable fishers.

```bash
# With distribution sweep
uv run main.py --egoists 4 --cooperators 6 --sanctioners 6 --imitators 4 --distribution-sweep
```

Press **spacebar** to pause/resume.
