# 1. Overview

## 1.1 Purpose
Das Modell soll untersuchen, unter welchen Bedingungen eine gemeinsam genutzte Ressource kollabiert mit den kontrahierenden Thesen von Garrett Hardin 
(unausweichliche Übernutzung) und Elinor Ostrom (lokale Nutzungsordnung durch lokale Gemeinschaft).
- Einfluss des Verhaltens auf die Ressourcendynamik
- Kooperation unter Konkurrenz?
- räumliche Muster der Übernutzung?
- institutionelle Mechanismen als Schutz vor Übernutzung?

## 1.2 Entities, State Variables, Scales
Das Modell besteht aus 2 Ebenen: ein Gitter von See-Patches (ökologische Ebene) & eine Population von Fischer-Agenten (die soziale Ebene).
Die See-Patches sind definiert durch ihre Fischmasse, die Umweltkapazität und die Wachstumsrate der Fischmasse.
Die Agenten, also die Fischer sind definiert durch ihre aktuelle Position im Patch-Gitter, ihre Strategie, (Gewinnmaximierung,
Imitation des erfolgreichsten Nachbarn, konditionelle Kooperation, oder Sanktionierung), ihren Ertrag, Betrafungskosten und ein Maß der Reputation.

- See (2D-Gitter aus Patches)
- Patch (Fischbestand):
	- Biomasse
	- Tragfähigkeit
	- Wachstumsrate
- Fischer (Agenten):
	- Position
	- Strategie
	- aktueller Fang
	- Bestrafungskosten
	- ev. Reputation (?)

- NxN GItter, diskrete Zeitschritte (wie lange?)

## 1.3 Process Overview & Scheduling
	1.	Fischbestand wächst und diffundiert
	2.	Fischer bewegt sich, wählt Strategie und fängt
	3.	Sanktionen
	4.	Strategieanpassung


# 2. Design Concepts

## 2.1  Basic Principles
Das Modell basiert auf zwei gegensätzlichen theoretischen Ansätzen:
- Hardin (1968): Individuelle Rationalität führt bei Gemeingut zur Ressourcenerschöpfung, da Nutzer den Ertrag privat einnehmen, 
die Kosten aber auf alle Nutzer verteilt werden.
- Ostrom (1990): Reale Gemeinschaften entwickeln Regeln, Grenzen, Sanktionen, Monitoring, die Kollaps verhindern können


## 2.2  Emergence
- Kollaps oder Stabilisierung des Fischbestands
- Räumliche Muster der Übernutzung
- Kooperationsnormen in Populationen 
- Emergente soziale Schichtung: Fischer mit Kooperationsstrategie können langfristig höhere Erträge erzielen als reine Defektierer

## 2.3  Adaptation
Fischer können ihre Strategie in Abhängigkeit vom eigenen Erfolg und dem beobachteten Verhalten der Nachbarn anpassen.
Die Anpassungsmechanismen je nach Strategie:
- Imitationsagenten wechseln zur Strategie des erfolgreichsten beobachteten Nachbarn, wenn dessen Ertrag den eigenen übersteigt.
- Kooperationsagenten passen ihre Kooperationsbereitschaft basierend auf den Reputationswerten anderer an.
- Sanktionsagenten justieren ihre Sanktionsschwellwerte auf Basis der wahrgenommenen Regelkonformität.

## 2.4  Objectives
Agenten verfolgen folgende Ziele, die sich je nach Strategie unterscheiden:
- Egoisten: Kurzfristige Maximierung des eigenen Fangertrags
- Imitatoren: Maximierung des eigenen Ertrags durch Beobachtung und Nachahmung
- Konditionale Kooperatoren: Langfristige Maximierung unter Berücksichtigung der Ressourcenverfügbarkeit
- Sanktionsagenten: Durchsetzung kollektiver Regeln, langfristige Nachhaltigkeit

## 2.5  Learning
Strategieadaption erfolgt durch Imitation (Beobachtung des Nachbarn) und bedingtes Reagieren auf Sanktionen. 

## 2.6  Prediction
Egoisten und Imitatoren handeln reaktiv ohne explizite Prognose. 

## 2.7  Sensing
Jeder Fischer nimmt folgende Informationen wahr:
- Fischbiomasse der aktuellen und benachbarten Zellen
- Strategie und letzter Fangertrag direkt benachbarter Fischer
- Eigene Ertragshistorie
- Perfekte globale Information über den Gesamtbestand hat nur der Observer, nicht die Agenten.

## 2.8  Interaction
- Fischer–Patch: Fischentnahme durch Fischer reduziert die Biomasse des Patches direkt.
- Fischer–Fischer: Imitation & Sanktionierung (ökonomische Kosten auferlegen). 

## 2.9  Stochasticity
	1.	Platzierung der Fischer auf dem Gitter
	2.	Strategiezuweisung der Agenten
	3.	Reihenfolge der Agentenaktivierung pro Schritt
	4.	Stochastische Komponente in Imitations- und Sanktionsentscheidungen

## 2.10  Collective
Es werden keine expliziten Gruppen oder Kollektive modelliert. 

## 2.11  Observation
- Gesamtfischbestand und Verteilung der Biomasse (räumlich)
- Strategieverteilung der Fischer (Anteil jeder Strategie)
- Gesamtertrag und durchschnittlicher Ertrag je Strategie
- Anzahl ausgesprochener Sanktionen
- Gini-Koeffizient der Ertragsverteilung
- Kollaps-Indikator: Gesamtbestand unter kritischem Schwellwert



# 3. Details

## 3.1  Initialization
Fisch-Patches:
Jede Zelle erhält eine initiale Biomasse mit Streuung um einen Mittelwert,
dieser kann homogen oder räumlich heterogen (z.B. höher in der Mitte des Sees) verteilt sein.
Die Wachstumsrate r ist für alle Patches identisch.\
\
Fischer:
- Fischer werden zufällig auf dem Gitter platziert (Mehrfachbelegung erlaubt)
- Strategien werden zugewiesen
- Initiale kumulative Erträge: 0
- Reputation: neutral
- Sanktionszähler: 0

## 3.2  Eingabedaten
Das Modell benötigt keine externen Eingabedaten.


## 3.3 Submodels

### 3.3.1  Ökologisches Teilmodell: Logistisches Wachstum und Diffusion
Pro Zeitschritt wird die Biomasse jedes Patches gemäß der logistischen Wachstumsfunktion aktualisiert. 
Ein Diffusionsterm modelliert das passive Einwandern von Fischen aus benachbarten Patches: bestehend aus 
einem Diffusionskoeffizienten (z.B. 0,1) und dem Mittelwert der Biomasse der 8 Moore-Nachbarzellen
 
### 3.3.2  Übersicht der Strategien
- Egoist: Fischt bis zur lokalen Kapazitätsgrenze. Keine Berücksichtigung kollektiver Konsequenzen.
- Imitator: Beobachtet alle Fischer im Sichtradius, bestimmt den erfolgreichsten (höchster letzter Ertrag) 
und übernimmt mit gewisser Wahrscheinlichkeit dessen Strategie und Fangmenge.
- Konditionaler Kooperator: Berechnet eine nachhaltige Fangmenge basierend auf dem beobachteten Gesamtbestand und reduziert den Fang,
wenn der Bestand unter einen Schwellwert S_krit fällt. Kooperation ist an die wahrgenommene Kooperationsbereitschaft der Nachbarn geknüpft
- Sanktionierer: Fischt nachhaltig und bestraft Fischer, die signifikant über der nachhaltigen Menge fangen.
Sanktionen erzeugen Kosten für den Sanktionierten (Bonusreduktion) und geringe Kosten für den Sanktionierer (altruistische Bestrafung nach Fehr & Gächter 2000).
 
