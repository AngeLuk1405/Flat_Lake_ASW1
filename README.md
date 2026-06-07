Dieses Projekt untersucht die Nutzung einer gemeinsam genutzten Fischerei-Ressource (Common-Pool Resource) mithilfe eines agentenbasierten Modells. Ziel ist es zu analysieren, unter welchen Bedingungen ein Fischbestand langfristig erhalten bleibt oder durch Übernutzung kollabiert.

Die Simulation basiert auf den theoretischen Ansätzen von Garrett Hardin („Tragedy of the Commons“) und Elinor Ostrom (gemeinschaftliche Ressourcenverwaltung). Dabei wird untersucht, wie unterschiedliche Verhaltensstrategien von Fischern die Entwicklung einer gemeinsamen Ressource beeinflussen.

Der See wird als zweidimensionales Gitter von Patches modelliert, auf denen sich Fischbiomasse durch logistisches Wachstum regeneriert. Fischer bewegen sich auf diesem Gitter, entnehmen Fischbestände und interagieren mit anderen Fischern in ihrer Umgebung.

Das Modell beinhaltet vier Agententypen:

Egoisten, die möglichst viele Fische fangen,
Kooperatoren, die nachhaltig wirtschaften,
Imitatoren, die erfolgreiche Strategien anderer Fischer übernehmen,
Sanktionierer, die nachhaltiges Verhalten fördern, indem sie Regelverstöße überwachen und bestrafen.

Agenten:
  Sanktionierer:
    Fischt Nachhaltig
    überwacht Fischer
    Bestraft Regelverstöße
    Trägt selbst Kosten für die durchsetzung der Regeln
  
Sanktionierungsmechanismus:
Ein Fischer gilt als Regelbrecher, wenn seine Fangmenge die nachhaltige Fangmenge um einen fesgelegten Schwellenwert überschreitet.
Bei einem Regelverstoß:
  verliert der Regelbrecher ein Teil seines Ertrages
  dinkt seine Reputation
  zahlt der sanktionierer Kosten für die durchführung der Sanktion
Dieser Mechanismus basiert auf Ostroms Idee lokaler Kontrolle und sanktionierung gemeinschaftlicher Ressourcen.

Parameter:
  Gridgröße: 20x20
  Anzahl fischer: 10
  Tragfähigkeit pro Patch: 100
  Wachstumsrate: 0.3
  Sichtradius: 3 Felder

  
