###### tags: `openEHR` `ZLG` `flatLoader` `implementation`

# PATHS from WebTemplate
Dieses Skript extrahiert FLAT-Pfade aus einem WebTemplate. Das WebTemplate basiert auf dem simSDT-WebTemplate Format der Firma Better, welches sowohl die Better Platform als auch die EHRBase unterstützt. 
 
Die EHRBase bietet FLAT-Funktionalitäten unter dem "ecis"-Endpunkt an. - Stand Version 0.16 (beta)
 
Die openEHR-Community plant die Übernahme des simSDT-Formats in den Standard. - https://specifications.openehr.org/releases/ITS-REST/Release-1.0.2/simplified_data_template.html

---

## FLAT-PFADE 
- FLAT-Pfade erhält man, indem die ID Felder der Elemente des WebTemplate verkettet werden.
Feld id enthaelt den Namen des Elements
- MIN und MAX geben an, wie oft das Element in einer Ressource vorhanden sein kann oder muss. -> Max: -1 = Element kann beliebig oft vorkommen
Suffixe werden an den Pfad am Ende angehängt. -> Element/Element2|suffix

## Output
Ausgabe ist ein Dictionary mit Pfadnamen als key ala dict['Pfadname']['rmType'] und dict['Pfadname']['mandatory']
- mandatory ist 0 oder 1, wobei 1 = Pflichtfeld bedeutet

---

# List of Types and their attributes 
(X indicates that this one is **definitely** handled in this script)
https://specifications.openehr.org/releases/RM/latest/data_types.html

![](https://pad.gwdg.de/uploads/upload_2e7b0e8af6a933453c33741e02914c64.png)

## 6. Quantity Package
- DV_ORDERED: Abstract -> CODE_PHRASE, DV_INTERVAL, List of REFERENCE_RANGE
    - [ ] DV_INTERVAL:        none
    - REFERENCE_RANGE:    DV_TEXT, DV_INTERVAL
    - [x] DV_ORDINAL:         DV_CODED_TEXT, value=Integer  (+|ordinal)
    - [ ] DV_SCALE:           DV_CODED_TEXT, value=Real
- DV_QUANTIFIED: Abstract -> magnitude_status, accuracy
    - [ ] DV_AMOUNT:          accuracy_is_percent=Boolean, accuracy=Real
    - [x] DV_QUANTITY:        magnitude, unit=CODED_TEXT
    - [x] DV_COUNT:           value=magnitude
    - DV_PROPORTION:      numerator, denominator, type
    - PROPORTION_KIND:    ...
    - DV_ABSOLUTE_QUANTITY: accuracy: DV_AMOUNT

## 4. Basic Package
- DATA_VALUE: Abstract
    - [ ] DV_BOOLEAN:         value=Boolean  (maybe like DV_COUNT which would mean "no suffix-Case")
    - [ ] DV_STATE:           value=DV_CODED_TEXT, is_terminal
    - [ ] DV_IDENTIFIER:      id, ...

## 5. Text Package
- [x] DV_TEXT             value:String
- [ ] TERM_MAPPING        match=char, target=CODE_PHRASE
- [x] CODE_PHRASE         code=code_string, terminology=terminology_id
- [x] DV_CODED_TEXT       value, CODE_PHRASE
- DV_PARAGRAPH        This one is DEPRECATED, DV_TEXT (which is markdown formatted) is used instead

## 7. Date Time Package
- DV_TEMPORAL         accuracy=DV_DURATION --> Specialised temporal variant of DV_ABSOLUTE_QUANTITY whose diff type is DV_DURATION.
- [ ] DV_DATE             value=String -> ISO8601 date string         (Structure like DV_COUNT?)
- [ ] DV_TIME             value=String -> ISO8601 time string         (Structure like DV_COUNT?)
- [x] DV_DATE_TIME        value=String -> ISO8601 date/time string
- [ ] DV_DURATION         value=String -> ISO8601 duration string, including described deviations to support negative values and weeks.   (Structure like DV_COUNT?)

## 8. Time_specification Package
- DV_TIME_SPECIFICATIONS  Abstract
    - DV_PERIODIC_TIME_SPECIFICATION  --> Specifies periodic points in time, linked to the calendar (phase-linked), or a real world repeating event, such as breakfast (event-linked). Based on the HL7v3 data types PIVL Type and EIVL Type. Used in therapeutic prescriptions, expressed as INSTRUCTIONs in the openEHR model.
    - DV_GENERAL_TIME_SPECIFICATION   --> Specifies points in time in a general syntax. Based on the HL7v3 GTS data type.

## 9. Encapsulated Package
- DV_ENCAPSULATED     Abstract -> Common Metadata -> CODE_PHRASE for charset and language
    - DV_MULTIMEDIA:      media_type=CODE_PHRASE, size: Integer
    - DV_PARSABLE:        value=String, formalism=String

## 10. Uri Package
- DV_URI              value=String        --> A reference to an object which structurally conforms to the Universal Resource Identifier (URI) RFC-3986 standard
- DV_EHR_URI                              --> A DV_EHR_URI is a DV_URI which has the scheme name 'ehr', and which can only reference items in EHRs.

---
    
# Test der Pfad-Extraktion
- Erstellen eines Archetypen "webtemplate_datatypes.v0"
- Erstellen eines Templates für den Test
- Test-Extraktion von Pfaden über Mapping mit Hilfe des Tools
    
Archetyp:
![](https://pad.gwdg.de/uploads/upload_d85a6f793fd147ba2711963670fca082.png)

- Mapping-Bau ergab 90 Pfade
    - 21 Pflichtpfade korrekt ausgegeben
    - rmTypes werden korrekt ausgegeben
- Prüfen ob alle Suffix enthalten sind
- Abgleichen mit Better-Ressource-Example
- Findings notieren!

![](https://pad.gwdg.de/uploads/upload_a0dac1f809c31be9c3361062e568afe4.png)

## Findings:
- DV_Proportion benötigt einen |type suffix 
- DV_MULTIMEDIA benötigt einen none + mediatype + alternatetext + size
- Alle Types prüfen, die Struktur vernachlässigen

- Sollten wir validation mit extrahieren? Ergibt Sinn..ja