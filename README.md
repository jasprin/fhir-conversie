# fhir-conversie-stu3-r4

Converteert MedMij-laboratoriumuitslagen van **FHIR STU3 (zib2017)** naar **FHIR R4 (zib2020)**, met mappings in de [FHIR Mapping Language](https://hl7.org/fhir/R4/mapping-language.html) (FML). Uitgevoerd door de [HL7 FHIR Validator](https://github.com/hapifhir/org.hl7.fhir.core).

Gemaakt als tijdelijke converter voor de pilot *Weergave laboratoriumuitslagen in de PGO*. De mappings zijn open en herbruikbaar voor iedereen die van STU3/zib2017 naar R4/zib2020 moet.

> **Status:** concept. De mappings dekken nog niet alle elementen van de profielen.

## Wat wordt er geconverteerd

Een searchset-Bundle zoals de MedMij-gegevensdienst [LaboratoryResults](https://informatiestandaarden.nictiz.nl/wiki/MedMij:V2020.01/FHIR_LaboratoryResults) die levert:

| Resource | Van (STU3, zib2017) | Naar (R4, zib2020) |
|---|---|---|
| Observation | `zib-LaboratoryTestResult-Observation` | `nl-core-LaboratoryTestResult` |
| Specimen | `zib-LaboratoryTestResult-Specimen` | `nl-core-LaboratoryTestResult.Specimen` |
| Patient | `nl-core-patient` | `nl-core-Patient` |
| Practitioner | `nl-core-practitioner` | `nl-core-HealthProfessional-Practitioner` |
| Organization | `nl-core-organization` | `nl-core-HealthcareProvider-Organization` |

Resource-id's, `fullUrl`'s en `search.mode` blijven behouden, zodat referenties binnen de Bundle geldig blijven.

## Ontwerp

![Architectuur](docs/architectuur.svg)

**Runtime.** De converter is een black box: een STU3-Bundle erin, een R4-Bundle eruit, in één aanroep.

```
POST http://<host>:8090/transform?map=<canonical van de Bundle-map>
Content-Type: application/fhir+json   (of application/fhir+xml)
Accept:       application/fhir+json

Body:     STU3 searchset-Bundle
Antwoord: R4 searchset-Bundle
```

Dezelfde conversie kan ook als command line-aanroep, met bestanden (zie [Gebruik](#gebruik)).

**Mappings.** Er is één map per resourcetype, plus een gedeelde map voor terugkerende regels. De Bundle-map importeert ze met `imports` en geeft elke entry door aan de map voor dat type.

**Waarom een STU3-context.** De Validator draait met `-version 3.0`, zodat de invoer als echte STU3 wordt gelezen. Voor de doeltypes verwijzen de maps naar de R4-definities met versienummer (`http://hl7.org/fhir/4.0/StructureDefinition/...`). Die komen uit het HL7-package `hl7.fhir.xver.r3`.

**Bouwstap.** Een STU3-context kan geen FML-tekst lezen. Elke map wordt daarom eenmalig gecompileerd in een R4-context en daarna omgezet naar STU3-formaat. De `.map`-bestanden zijn de bron; de gecompileerde StructureMaps worden gegenereerd. Per conversie wordt niets gecompileerd.

## Repository

```
maps/              FML-bron: LabBundle.map, LabObservation.map, LabPatient.map, ... en LabCommon.map
tests/input/       STU3-testberichten
tests/expected/    verwachte R4-uitvoer
docs/              ontwerpdocumentatie en architectuurplaat
build/             gegenereerde StructureMaps (niet in Git)
```

## Gebruik

### Vereisten

- Java 17 of hoger
- Ongeveer 1,5 GB geheugen in servermodus
- Netwerktoegang tot `packages.fhir.org` (bij de eerste start) en een terminologieserver (standaard `tx.fhir.org`); de Validator start geen transformatie zonder.

Getest met Validator 7.0.2. Zet de versie vast; bij een update eerst de testset draaien.

```bash
curl -L -o validator_cli.jar \
  https://github.com/hapifhir/org.hl7.fhir.core/releases/download/7.0.2/validator_cli.jar
```

### Maps bouwen

Per map: compileren in een R4-context en omzetten naar STU3-formaat.

```bash
BASE=http://example.org/fhir/StructureMap   # canonical-basis van de maps
V="java -jar validator_cli.jar"

for m in LabBundle LabCommon LabObservation LabPatient LabPractitioner LabOrganization LabSpecimen; do
  $V compile $BASE/$m -version 4.0 -ig maps/$m.map -output build/r4/$m.json
  $V to-version 3.0 build/r4/$m.json -version 4.0 -do-native -output build/r3/$m.json
done
```

Na een wijziging hoeven alleen de gewijzigde maps opnieuw gebouwd te worden.

### Converteren als bestand

```bash
$V transform $BASE/LabBundle tests/input/bundle-stu3.json \
   -version 3.0 -ig hl7.fhir.xver.r3#1.2.1 -ig build/r3 \
   -output bundle-r4.json
```

### Converteren als HTTP-service

```bash
$V server 8090 -version 3.0 -ig hl7.fhir.xver.r3#1.2.1 -ig build/r3
```

De service is na ongeveer 45 seconden beschikbaar. Een conversie duurt daarna ongeveer 0,1 seconde per Bundle. Na een nieuwe build de service herstarten om de nieuwe maps te laden.

## Een map wijzigen of toevoegen

- **Bestaand resourcetype:** pas het bijbehorende bestand in `maps/` aan.
- **Nieuw resourcetype:** maak `maps/Lab<Type>.map` met een groep `<Type>`, en voeg in `LabBundle.map` een `uses` voor het R4-doeltype, een `imports` en een regel in de groep `Entry` toe. Groepsnamen moeten uniek zijn over alle maps.
- **Wat er inhoudelijk verandert** tussen zib2017 en zib2020 staat per zib in de translatietabellen van Nictiz: [Zibtranslate](https://github.com/Nictiz/Zibtranslate).

## Let op

- **Niet-gemapte elementen verdwijnen zonder melding.** Valideer de uitvoer altijd tegen de profielen, bijvoorbeeld met `$V bundle-r4.json -version 4.0 -ig nictiz.fhir.nl.r4.zib2020`, en vergelijk met `tests/expected/`.
- **Controleer of er uitvoer is.** De command line meldt "Successfully transformed", ook als een geïmporteerde map ontbreekt; er wordt dan geen uitvoerbestand geschreven.
- **De servermodus heeft geen authenticatie,** en beheerendpoints als `/stop` en `/loadIG` staan open. Alleen gebruiken op een afgeschermd netwerk.
- **Alleen synthetische testdata** in deze repository, geen patiëntgegevens.

## Bronnen

- [FHIR Mapping Language](https://hl7.org/fhir/R4/mapping-language.html)
- [HL7 FHIR Validator](https://github.com/hapifhir/org.hl7.fhir.core)
- [Nictiz STU3 zib2017](https://simplifier.net/nictizstu3-zib2017) en [Nictiz R4 zib2020](https://simplifier.net/nictiz-r4-zib2020)
- [Zibtranslate: translatiespecificaties zib2017 → zib2020](https://github.com/Nictiz/Zibtranslate)
- [MedMij-gegevensdienst LaboratoryResults (STU3)](https://informatiestandaarden.nictiz.nl/wiki/MedMij:V2020.01/FHIR_LaboratoryResults)
