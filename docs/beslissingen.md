# Ontwerpbeslissingen

De keuzes in dit project, met aanleiding en gevolgen. Elke beslissing heeft een vast nummer; een vervallen beslissing blijft staan met status "vervallen" en een verwijzing naar de opvolger. Een beslissing die maar voor één conversierichting geldt, noemt die richting.

Status: **besloten**, **voorstel** (nog niet bevestigd) of **vervallen**.

| # | Beslissing | Status |
| --- | --- | --- |
| [B01](#b01) | Conversie met FML, uitgevoerd door de HL7 FHIR Validator | besloten |
| [B02](#b02) | Eén map per conversierichting | besloten |
| [B03](#b03) | Canonicals: `http://medmij.nl/fhir/StructureMap/<bron>-<doel>-<map>` | voorstel |
| [B04](#b04) | Altijd de meest recente Validator | besloten |
| [B05](#b05) | De Validator draait in de FHIR-versie van de bron | besloten |
| [B06](#b06) | HTTP-service zonder terminologieserver | besloten |
| [B07](#b07) | Eigen maps; de interversion-maps van HL7 als referentie | voorstel |
| [B08](#b08) | Mappings eerst documenteren, dan bouwen | besloten |
| [B09](#b09) | Testmateriaal: ongewijzigde bron plus afgeleide testberichten | besloten |
| [B10](#b10) | R4 → STU3, LaboratoryResults: Lab2patient als bron, ServiceRequest valt voorlopig weg | besloten |

---

## B01

**Conversie met FML, uitgevoerd door de HL7 FHIR Validator** · besloten · 2026-11-11

- **Aanleiding.** De conversie moet herbruikbaar zijn voor anderen en controleerbaar voor wie geen code leest.
- **Keuze.** De mappings staan in de [FHIR Mapping Language](https://hl7.org/fhir/R4/mapping-language.html). De HL7 FHIR Validator voert ze uit, als command line of als HTTP-service.
- **Alternatieven.** Eigen code (Java, .NET, Python): flexibeler, maar de logica is dan niet in een FHIR-standaard vastgelegd en niet herbruikbaar door anderen.
- **Gevolg.** De maps zijn standaard FHIR-artefacten (StructureMaps). We zijn afhankelijk van het gedrag van de Validator, zie [B04](#b04).

## B02

**Eén map per conversierichting** · besloten · 2026-11-12

- **Aanleiding.** De eerste richting is R4 → STU3, maar de repository moet uitgebreid kunnen worden met andere richtingen en versies.
- **Keuze.** Elke richting staat in `conversies/<bron>-<doel>/`, met eigen maps, mappingdocumenten en tests. Scripts, beslissingen en werkwijze zijn gedeeld. `<bron>` en `<doel>` zijn de korte namen van de FHIR-versies: `stu3`, `r4`, `r4b`, `r5`.
- **Alternatieven.** Eén verzameling maps voor alle richtingen: minder mappen, maar namen en tests van richtingen lopen door elkaar.
- **Gevolg.** Richtingen delen geen maps. Een gedeelde datatype-map voor twee richtingen kan pas als die echt identiek is, en dan als aparte beslissing.

## B03

**Canonicals: `http://medmij.nl/fhir/StructureMap/<bron>-<doel>-<map>`** · voorstel · 2026-11-12

- **Aanleiding.** Elke StructureMap heeft een unieke, stabiele URL nodig. Aanroepers gebruiken die URL; met meerdere richtingen moeten de namen niet botsen.
- **Keuze.**
  - Canonical: `http://medmij.nl/fhir/StructureMap/<richting>-<map>`, bijvoorbeeld `.../r4-stu3-LaboratoryTestResult`. Dit volgt het patroon van MedMij (`http://medmij.nl/fhir/<Resourcetype>/<id>`). Het voorvoegsel is gelijk aan de mapnaam in `conversies/`, zodat de scripts de canonical uit het pad kunnen afleiden.
  - `StructureMap.name` en de groepsnamen: `<Richting><Map>` in PascalCase, bijvoorbeeld `R4Stu3LaboratoryTestResult`. FHIR staat in `name` geen streepjes toe, en het voorvoegsel voorkomt botsingen met de groepen van HL7 (zoals `Observation`) en van andere richtingen.
  - De versie van een map staat in `StructureMap.version`, niet in de URL. Een aanroeper kan een versie vastzetten met `<canonical>|<versie>`.
  - Andere artefacten, zoals ConceptMaps, volgen hetzelfde patroon: `http://medmij.nl/fhir/ConceptMap/<richting>-<naam>`.
- **Uitbreiding.** Krijgt één richting meer dan één set profielen (bijvoorbeeld Nictiz en internationaal), dan komt de set na de richting: `<richting>-<set>-<map>`. Dat is pas nodig als het zich voordoet.
- **Alternatieven.** De richting in het pad (`http://medmij.nl/fhir/r4-stu3/StructureMap/...`): wijkt af van het patroon van MedMij en van de FHIR-conventie `<basis>/<Resourcetype>/<id>`.
- **Open.** Nagaan binnen MedMij: niemand anders gebruikt `http://medmij.nl/fhir/StructureMap/`. Een id mag maximaal 64 tekens hebben; `r4-stu3-HealthProfessional-PractitionerRole` heeft er 43.

## B04

**Altijd de meest recente Validator** · besloten · 2026-11-11

- **Keuze.** Geen vaste versie; download via `releases/latest`. Na een update draait de testset.
- **Gevolg.** Een nieuwe release kan gedrag veranderen. De testset in CI vangt dat op. De command line wijzigt soms; de ingebouwde hulp (`help <commando>`) is leidend.

## B05

**De Validator draait in de FHIR-versie van de bron** · besloten · 2026-11-12

- **Aanleiding.** De invoer moet gelezen worden als de versie die hij is, ook met elementen die in de doelversie niet bestaan.
- **Keuze.** De Validator converteert met `-version` van de bron. De maps verwijzen voor de bron naar de definities zonder versie (`http://hl7.org/fhir/StructureDefinition/...`) en voor het doel naar de definities met versie (`http://hl7.org/fhir/3.0/StructureDefinition/...`) uit `hl7.fhir.xver.<bron>`.
- **Bevindingen** (Validator 7.0.5):
  - R4 → STU3: compileren en converteren in een R4-context werken, met `hl7.fhir.xver.r4` 1.2.0.
  - STU3 → R4 (eerder uitgeprobeerd): een STU3-context kan geen FML lezen. Compileren moet dan in een R4-context, gevolgd door `to-version 3.0`. Daarna werkt de conversie ook als HTTP-service.
- **Gevolg.** De bouwstap hangt af van de bronversie. Eén HTTP-service kan alleen maps laden van richtingen met dezelfde bronversie.

## B06

**HTTP-service zonder terminologieserver** · besloten · 2026-11-11

- **Aanleiding.** Zonder `-tx n/a` start de service niet als `tx.fhir.org` onbereikbaar is. Dat gebeurde tijdens het testen (HTTP 502).
- **Keuze.** De service draait met `-tx n/a`. De conversie gebruikt geen terminologieserver.
- **Gevolg.** De maps mogen geen terminologieserver nodig hebben, dus geen `translate()` met een externe ConceptMap. Omzettingen van codes staan in de maps zelf, of in ConceptMaps die met de maps worden meegeladen. Op de command line weigert `transform` zonder terminologieserver; voor bouwen en testen blijft die dus nodig.

## B07

**Eigen maps; de interversion-maps van HL7 als referentie** · voorstel · 2026-11-12

- **Aanleiding.** HL7 publiceert maps tussen de FHIR-versies (zoals `http://hl7.org/fhir/StructureMap/Observation4to3`), in de packages `hl7.fhir.xver.*`.
- **Bevindingen.**
  - De maps zijn geschreven voor de context van de bron: de bron zonder versie, het doel met versie. Voor R4 → STU3 past dat bij [B05](#b05).
  - `Bundle4to3` werkt niet zoals hij is: het aanmaken van de resource in een entry faalt (`sd is null`).
  - In de richting STU3 → R4 bleek dat de HL7-maps codesystemen ongewijzigd overnemen (bijvoorbeeld `http://hl7.org/fhir/v2/0078`), en dat de uitvoer dan niet geldig is in de doelversie.
- **Keuze.** We schrijven eigen maps. De HL7-maps zijn de referentie voor de basisconversie: wat een mappingdocument niet noemt, gaat zoals HL7 het doet. Een afwijking van HL7 staat expliciet in het mappingdocument.
- **Open.** Nagaan of de HL7-maps voor afzonderlijke resources en datatypes (zoals `Observation4to3`) wel te importeren zijn. Dan hoeven we de basisconversie niet zelf te schrijven.

## B08

**Mappings eerst documenteren, dan bouwen** · besloten · 2026-11-11

- **Aanleiding.** FML lezen weinig mensen. Inhoudelijke keuzes moeten te beoordelen zijn door inhoudsdeskundigen.
- **Keuze.** Per map een document in `conversies/<richting>/mappings/<map>.md`, geschreven vóór de FML. Het beschrijft alleen wat afwijkt van de basisconversie ([B07](#b07)). Elke regel heeft een nummer (bijvoorbeeld `LTR-01`); de FML verwijst er met commentaar naar.
- **Gevolg.** De verwachte uitvoer in `tests/<gegevensdienst>/expected/` is de toets dat documentatie en FML overeenkomen.

## B09

**Testmateriaal: ongewijzigde bron plus afgeleide testberichten** · besloten · 2026-11-12

- **Keuze.** Per gegevensdienst staat het uitgangsmateriaal ongewijzigd in `tests/<gegevensdienst>/bron/`, met herkomst en licentie. De testberichten in `input/` zijn daaruit afgeleid en mogen worden aangepast; elke aanpassing staat in de README van de testset. Alleen synthetische data.
- **Gevolg.** De mappingdocumenten geven per regel aan of de testset hem dekt. Wat het materiaal niet dekt, vraagt eigen synthetische voorbeelden.

## B10

**R4 → STU3, LaboratoryResults: Lab2patient als bron, ServiceRequest valt voorlopig weg** · besloten · 2026-11-12

- **Aanleiding.** De bron levert R4; de MedMij-gegevensdienst [LaboratoryResults 2020.01](https://informatiestandaarden.nictiz.nl/wiki/MedMij:V2020.01/FHIR_LaboratoryResults) verlangt STU3. Voor de bronkant is een R4-standaard nodig die dezelfde transactie beschrijft.
- **Keuze.**
  - Bron: [Lab2patient](https://informatiestandaarden.nictiz.nl/wiki/L2p:V2_FHIR_lab2patient) (`nictiz.fhir.nl.r4.labexchange` 4.0.0-beta.2), het beschikbaarstellen van laboratoriumresultaten aan de patiënt. Het testmateriaal komt uit de voorbeelden van Nictiz in [HL7-mappings](https://github.com/Nictiz/HL7-mappings/tree/master/ada_2_fhir-r4/lab/l2p-1.0.0).
  - ServiceRequest (`lu-OrderData`) heeft geen tegenhanger in MedMij 2020.01 en valt bij de conversie weg, met de referenties ernaar.
- **Alternatieven.** Het R4-materiaal in [Nictiz-testscripts](https://github.com/Nictiz/Nictiz-testscripts/tree/main/src/LaboratoryResults-3-0): niet gepubliceerd (alleen in `dev/`), testscripts uitgeschakeld, en de fixtures gebruiken extensies van een oudere beta.
- **Open.** Of gegevens uit de aanvraag (zoals de aanvrager) toch in de Observation of het DiagnosticReport in STU3 moeten komen. Lab2patient is nog beta; een nieuwe versie kan het bronmateriaal veranderen.
