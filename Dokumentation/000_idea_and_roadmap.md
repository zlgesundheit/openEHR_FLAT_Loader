# Update 02.06.2021
Es hat einen Namen: openEHR_FLAT_Loader

Skripte derzeit per Kommandozeile steuerbar.
Auswahl eines Prozessschritts: 
1. Pfade auslesen und Mapping-Liste bauen
1.5 Manuell das Mapping ausfüllen
2. Compositions bauen
2.5 Profit

Repo-Infos und Pfade werden aus ".config.ini" gelesen.

- Kommanodzeilen Version per "python cmd_run_Main.py" starten
- GUI-Version kommt noch

===============================================

# Update 31.05.2021

Die Projekte COFONI, ELISE, ZLG benötigen alle für Endanwender/Forscher verwendbare Datenrepositorien.
Hierfür müssen zu beliebigen Templates mit geringem Aufwand ETL-Jobs gebaut werden können.
Der HaMSTR-Builder bietet eine solche Funktion über ein Mapping von Daten(SQL-Abfrage) auf FLAT-Pfade einer Beispiel-Composition der Better-/EHRScape-Plattform.

Die Nutzung der Beispiel-Composition ist nicht standardkonform (Example-REST-Endpunkt nicht im Standard)
Das FLAT-Format wird demnächst als SDT - Simplified Data Format in den Standard übernommen.

Roadmap:
- Ab Herbst hat ELISE Kapazitäten für die Entwicklung
- COFONI und ZLG machen bis dahin Vorarbeit
- Gegenseitige Updates über JF

Wir brauchen einen Weg, um Pfade und Constraints aus dem OPT zu extrahieren. (Z.B. OPT -> WebTemplate -> Mapping-Liste mit FLAT-Pfaden)
Mit den Pfaden baut uns der Nutzer ein Mapping auf seine Daten (CSV, DB, SQL-Abfrage)
Damit generieren wir die Daten.

Kurzfristige manuelle Umsetzung (mit FLAT-Example) am Beispiel von NATARS-Daten.

======================================
# Python statt C#? --> Java falls für das deserialisieren des OPT die openEHR_SDK benötigt wird...

## GUI für die Nutzung -> Py-FLASK-Webserver?
- Eingabe von Daten (openEHR-Plattform-Adressen + Logins)
- (Initial) Anpassen von Beispiel-Composition + Übersichtliche Anzeige des WebTemplates
- Eingabe des Mappings (CSV / DB / Tabellenform-Input auf FLAT-Pfade)
- (Initial) Buttons zum Ausführen der drei .py-Skripte

## Big ToDo:
- FLAT-Pfade aus OPT statt aus Beispielkomposition -> Damit erledigt sich der manuelle Schritt der Anpassung der Beispiel-Composition!