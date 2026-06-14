# Fischerei und Allmende: Eine agentenbasierte Simulation

## Abstract



## 1. Introduction



## 2. Method

### 2.1 Räumliche Struktur und ökologische Dynamik
Der See wird als 20x20 Gitter von Patch-Agenten modelliert, die durch ihre Biomasse, Kapazität und Wachstumsrate charakterisiert sind. Der See hat feste Grenzen, das heißt, dass der Gitterrand nicht mit dem gegenüberliegenden Rand benachbart ist. Das Gitter stellt demnach keinen Torus dar. Ein solches See-Gitter ließe sich beispielsweise als stark vereinfachte Darstellung der Nordee als Quadrat mit einer Seitenlänge von ~500 km und einer daraus resultierenden Patch-Größe von 25 km x 25 km interpretieren.\
<br>
Die Biomasse in jedem Patch wird zu Beginn als Zufallswert zwischen 0 und der Kapazitätsgrenze von 100 initialisiert. In jedem Zeitschritt diffundiert die Biomasse in der Moore-Nachbarschaft (die 8 angrenzenden Patches) und regeneriert sich durch logistisches Wachstum. Die Diffusion erfolgt in drei Schritten. Im ersten Schritt wird ein Gitter für die neuen Biomassewerte erstellt, in dem vorerst die aktuellen Werte gespeichert werden.\
Im zweiten Schritt wird für jeden Patch im See-Gitter der Mittelwert der Biomasse in der Moore-Nachbarschaft berechnet, wobei Randpatches aufgrund der festen Grenzen weniger Nachbarn haben. Die eigene Biomasse des Patches wird bei der Berechnung der Mittelwerts nicht berücksichtigt. Der neue Biomassewert wird schließlich mit folgender Formel berechnet und in das neue Biomasse-Gitter übernommen:

```python
new_biomass = current_biomass + DIFFUSION_COEFFICIENT * (neighbor_average - current_biomass)

new_biomass_grid[y][x] = max(0.0, min(CAPACITY, new_biomass))
```

Die verwendete Formel bewirkt, dass die Biomasse von biomassereichen Patches zu biomassearmen Patches diffundiert. Der Diffusionskoeffizient von 0.1 bestimmt wie stark die Biomasse an das Mittel der Nachbarschaft angenähert wird. Anschließend wird sichergestellt, dass die Biomasse nicht negativ wird und die Kapazitätsgrenze nicht überschreitet. Im dritten Schritt wird die Biomasse aller Patches mit den neuen Biomassewerten aktualisiert. Dieser stufenweise Ansatz verhindert, dass die Reihenfolge der Patches die Diffusionsberechnung beeinflusst, da für alle Patches zunächst der neue Wert berechnet und zwischengespeichert wird, bevor die neuen Werte für alle Patches übernommen werden.\
<br>
Nach der Diffusion regeneriert sich die Biomasse in jedem Patch durch logistisches Wachstum gemäß der folgenden Formel:
```python
self.biomass += self.growth_rate * self.biomass * (1 - (self.biomass / self.capacity))
```

## 3. Results



## 4. Discussion, Conclusion and Limitations



## References



## Appendix A: ODD