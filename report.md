# Fischerei und Allmende: Eine agentenbasierte Simulation

## Abstract



## 1. Introduction
Das Problem der Fischerei und Allmende ist ein repräsentatives Beispiel der "Tragedy of the commons". Diese Theorie geht auf den britischen Wirtschaftsschriftsteller William Forster Lloyd zurück, der 1833 in seinen "Two lectures on the checks to population" postulierte, dass die Lebensmittelproduktion über kurz oder lang nicht mit der durch den stetigen Bevölkerungswachstum getriebene Nachfrage nach Lebensmittel nicht mehr mithalten können wird [Q1]. Der Mikrobiologe und Ökologe Garret James Hardin griff die Theorie von Lloyd wieder auf und erweiterte die Thematik zur Bevölkerungsentwicklung mit der Problematik der Ressourcen(über)nutzung und der damit verbundenen Umweltzerstörung. Hardin hielt in seinem Artikel "The Tragedy of the commons" fest, dass, sobald einer Gesellschaft der uneingeschränkt Zugang zu einer Ressource gewährleistet würde, dies unausweichlich zu einem Ruin der Gemeinschaft führe, da jeder einzelne versuchen würde, seinen eigenen Ertrag zu maximieren [Q2]. Howard Scott Gordon griff dieses Thema ebenso auf und verknüpfte es mit dem repräsentativen und auch hier behandeltenm, anschaulichem Beispiel der Fischerei, da Fische im Meer annähernd als Allgemeingut betrachtet werden können [Q3].
Die US-amerikansiche Politikwissenschaftlerin Elinor Ostrom beleuchtet das Problem der Allmende jedoch unter einem anderen Blickwinkel und postuliert, dass Formen der Selbstorganisation und Kooperation der einzelnen Akteure einen Kollaps des Systems verhindern können. Instutitionelle Arrangements und Abkommen können dabei durch den Nutzen von lokalem Wissen eine potentielle Lösung des Allmendeproblems darstellen [Q4].
Das vorliegende agentenbasierte Modell soll nun die beiden nun vorgelegten Theorien von Hardin beziehungsweise Ostrom auf ihre Validität untersuchen. Es wird also ein besonderes Augenmerk darauf gelegt, unter welchen gesellschaftlichen Bedingungen sich ein Gleichgewicht durch lokale Kooperation einstellt oder das System kollabiert. Weiters wird überprüft, wie groß der Einfluss eines institutionellen Mechanismus in Form einer Bestrafung bei egoistischem Handeln ist beziehungsweise, in welcher Form Änderungen in der Systemdynamik durch einen regulativen Eingriff zu beobachten sind.


## 2. Method

### 2.1 Räumliche Struktur und ökologische Dynamik
Der See wird als 20x20 Gitter von Patch-Agenten modelliert, die durch ihre Biomasse, Kapazität und Wachstumsrate charakterisiert sind. Der See hat feste Grenzen, das heißt, dass der Gitterrand nicht mit dem gegenüberliegenden Rand benachbart ist. Das Gitter stellt demnach keinen Torus dar. Ein solches See-Gitter ließe sich beispielsweise als stark vereinfachte Darstellung der Nordsee als Quadrat mit einer Seitenlänge von ~500 km und einer daraus resultierenden Patch-Größe von 25 km x 25 km interpretieren.\
<br>
Die Biomasse in jedem Patch wird zu Beginn als Zufallswert zwischen 0 und der Kapazitätsgrenze von 100 initialisiert. In jedem Zeitschritt diffundiert die Biomasse in der Moore-Nachbarschaft (die 8 angrenzenden Patches) und regeneriert sich durch logistisches Wachstum. Die Diffusion erfolgt in drei Schritten. Im ersten Schritt wird ein Gitter für die neuen Biomassewerte erstellt, in dem vorerst die aktuellen Werte gespeichert werden.\
Im zweiten Schritt wird für jeden Patch im See-Gitter der Mittelwert der Biomasse in der Moore-Nachbarschaft berechnet, wobei Randpatches aufgrund der festen Grenzen weniger Nachbarn haben. Die eigene Biomasse des Patches wird bei der Berechnung der Mittelwerts nicht berücksichtigt. Der neue Biomassewert wird schließlich mit folgender Formel berechnet und in das neue Biomasse-Gitter übernommen:

```python
new_biomass = current_biomass + DIFFUSION_COEFFICIENT * (neighbor_average - current_biomass)

new_biomass_grid[y][x] = max(0.0, min(CAPACITY, new_biomass))
```

Die verwendete Formel bewirkt, dass die Biomasse von biomassereichen Patches zu biomassearmen Patches diffundiert. Der Diffusionskoeffizient von 0.1 bestimmt wie stark die Biomasse an das Mittel der Nachbarschaft angenähert wird. Anschließend wird sichergestellt, dass die Biomasse nicht negativ wird und die Kapazitätsgrenze nicht überschreitet. Im dritten Schritt wird die Biomasse aller Patches mit den neuen Biomassewerten aktualisiert. Dieser stufenweise Ansatz verhindert, dass die Reihenfolge der Patches die Diffusionsberechnung beeinflusst, da für alle Patches zunächst der neue Wert berechnet und zwischengespeichert wird, bevor die neuen Werte für alle Patches übernommen werden.\
<br>
Nach der Diffusion regeneriert sich die Biomasse in jedem Patch durch logistisches Wachstum gemäß der folgenden Formel: `biomass += growth_rate * biomass * (1 - (biomass / capacity))`.


### 2.2 Fischer-Agenten und Strategien
Die Fischer werden als Agenten modelliert, die durch ihre Position, Strategie, ihren aktuellen und kumulativen Fang sowie die Sanktionskosten charakterisiert sind. Die Fischer bewegen auf dem See-Gitter mit einer Wahrscheinlichkeit von 80 % auf den Patch in der Moore-Nachbarschaft, der die höchste Biomasse aufweist. Mit einer Wahrscheinlichkeit von 20% bewegen sie sich auf einen zufälligen benachbarten Patch. Die Fischer haben vier mögliche Strategien: Egiost, Kooperator, Sanktionierer und Imitator.\
<br>
Der **Egoist** fängt immer die gesamte Biomasse des Patches, auf dem er sich befindet. Die weiteren Stragien interagieren mit Fischern in ihrer Nachberschaft, um ihr Fangverhalten zu bestimmen. Die Nachbarschaft ist als Sichtradius von 3 definiert.\
Der **Kooperator** fängt nachhaltig, nachhaltiger Fang ist in diesem Modell dynamisch über das logistische Wachstum der Biomasse definiert. So wird beim nachhaltigen Fangen die Biomasse berechnet, die im nächsten Schritt nachwachsen kann und mit einem Faktor `SUSTAINABLE_CATCH_MULTIPLIER` von 5 multipliziert um die nachhaltige Fangmenge zu bestimmen. Sind jedoch mehr als 50% der Fischer im Sichtradius des Kooperators Egoisten, so fängt er ebenfalls wie ein Egoist die gesamte Biomasse des Patches.\
Der **Sanktionierer** fängt in jedem Schritt nachhaltig. Nachdem alle Fischer gefangen haben, sanktionieren die Sanktionierer alle Nachbarn im Sichtradius, die um einen Faktor `SANCTION_THRESHOLD` von 1.2 den nachhaltigen Fang überschreiten. Der genaue Sanktionsmechanismus wird in Abschnitt 2.3 beschrieben.\
Der **Imitator** passt seine Strategie in jedem Schritt an den erfolgreichsten Fischer im Sichradius an, wenn dieser erfolgreicher ist als der Imitator. Der erfolgreichste Fischer ist derjenige mit dem höchsten kumulativen Fang. Dabei ändern Imitatoren nur ihre aktuelle Strategie `current_strategy`, nicht ihre ursprüngliche Strategie `strategy`. Beim initialisieren der Fischer wird die aktuelle Strategie der Imitatoren zufällig gewählt, die aktuelle Strategie der Kooperatoren, Sanktionierer und Egoisten entspricht immer ihrer ursprünglichen Strategie. Dadurch können Imitatoren immer als solche identifiziert werden und gleichzeitig dynamisch ihre Strategie anpassen.

### 2.5 Sanktionsmechanismus





## 3. Results



## 4. Discussion, Conclusion and Limitations



## References
Q1: Vgl. William Forster Lloyd: Two lectures on the checks to population. University of Oxford. 1833. S.7ff.
Q2: Vgl. Garret James Hardin: The tragedy of the commons. Erschienen in: Science, New Series, Vol. 162, No. 3859. Dezember 1968. S.1243-1248.
Q3: Vgl. Howard Scott Gordon: The Economic Theory of a Common-Property Resource: The Fishery. Erschienen in: The Journal of Political Economy,   Vol. 62, No. 2. April 1954. S.124ff.
Q4: Vgl. Elinor Ostrom: Govering the commons: The evolution of institutions for collective action. Cambridge University Press. 1990. S.14f.




## Appendix A: ODD
