# Fischerei und Allmende - Flat Lake

Dieses Projekt untersucht die Nutzung einer gemeinsam genutzten Fischerei-Ressource (Common-Pool Resource) mithilfe eines agentenbasierten Modells. Ziel ist es zu analysieren, unter welchen Bedingungen ein Fischbestand langfristig erhalten bleibt oder durch Übernutzung kollabiert.

Die Simulation basiert auf den theoretischen Ansätzen von **Garrett Hardin** („Tragedy of the Commons“) und **Elinor Ostrom** (gemeinschaftliche Ressourcenverwaltung). Dabei wird untersucht, wie unterschiedliche Verhaltensstrategien von Fischern die Entwicklung einer gemeinsamen Ressource beeinflussen.

Der See wird als zweidimensionales Gitter von Patches modelliert, auf denen sich Fischbiomasse durch logistisches Wachstum regeneriert und zwischen benachbarten Patches diffundiert. Fischer bewegen sich auf diesem Gitter, entnehmen Fischbestände und interagieren mit anderen Fischern in ihrem Sichtradius.

Das Modell beinhaltet vier **Agententypen**:
- **Egoisten** fangen so viel wie möglich vom aktuellen Patch.
- **Kooperatoren** fischen nachhaltig wenn ihre Nachbarn das auch mehrheitlich tun, andernfalls handeln sie wie Egoisten.
- **Imitatoren** betrachten alle Fischer im Sichtradius und übernehmen die Fang-Strategie desjenigen mit dem höchsten kumulativen Fang.
- **Sanktionierer** fischen nachhaltig und bestrafen Fischer im Sichtradius, deren Fang einen Schwellenwert überschreitet, indem sie einen Teil des Fangs konfiszieren.

**Parameter:**
| Parameter | Wert |
|---|---|
| Gridgröße | 20x20 |
| Anzahl Fischer | 20 |
| Tragfähigkeit pro Patch | 100 |
| Wachstumsrate | 0.08 |
| Sichtradius | 3 |

## Verwendung

Benötigt [UV](https://github.com/astral-sh/uv).

```bash
# Zufällige Strategieverteilung
uv run main.py


# Strategieanzahlen festlegen
# Beispiel: 5 Fischer je Strategie
uv run main.py --egoists 5 --cooperators 5 --sanctioners 5 --imitators 5

# Beispiel: 20 Egoisten
uv run main.py --egoists 20 --cooperators 0 --sanctioners 0 --imitators 0
```

Der ```--distribution-sweep``` Parameter aktiviert einen optionalen Mechanismus, bei dem konfiszierter Fang nicht einfach verschwindet, sondern anteilig an alle nachhaltigen Fischer verteilt wird.

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

The lake is modeled as a two-dimensional grid of patches, where fish biomass regenerates through logistic growth and diffuses between neighboring patches. Fishers move across the grid, harvest fish stocks, and interact with other fishers within their sight radius.

The model includes four **agent types**:
- **Egoists** catch as much as possible from the current patch.
- **Cooperators** fish sustainably as long as the majority of their neighbors do the same, otherwise they act like egoists.
- **Imitators** observe all fishers within their sight radius and adopt the strategy of the one with the highest cumulative catch.
- **Sanctioners** fish sustainably and penalize fishers within their sight radius whose catch exceeds a threshold by confiscating part of their haul.

**Parameters:**
| Parameter | Value |
|---|---|
| Grid size | 20x20 |
| Number of fishers | 20 |
| Carrying capacity per patch | 100 |
| Growth rate | 0.08 |
| Sight radius | 3 |

## Usage

Requires [UV](https://github.com/astral-sh/uv).

```bash
# Random strategy distribution
uv run main.py

# Specify strategy counts
# Example: 5 fishers per strategy
uv run main.py --egoists 5 --cooperators 5 --sanctioners 5 --imitators 5

# Example: 20 egoists
uv run main.py --egoists 20 --cooperators 0 --sanctioners 0 --imitators 0
```

The ```--distribution-sweep``` flag activates an optional mechanism where confiscated catch is not simply removed but redistributed proportionally to all sustainable fishers.

```bash
# With distribution sweep
uv run main.py --egoists 4 --cooperators 6 --sanctioners 6 --imitators 4 --distribution-sweep
```

Press **spacebar** to pause/resume.
