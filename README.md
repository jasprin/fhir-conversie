# fhir-conversie-stu3-r4

Converteert FHIR-resources van **STU3 volgens zib2017** naar **R4 volgens zib2020**, met mappings in de [FHIR Mapping Language](https://hl7.org/fhir/R4/mapping-language.html) (FML). Uitgevoerd door de [HL7 FHIR Validator](https://github.com/hapifhir/org.hl7.fhir.core).

De mappings zijn per zib opgezet en herbruikbaar voor iedereen die van STU3/zib2017 naar R4/zib2020 moet, bijvoorbeeld voor MedMij-gegevensdiensten die nog STU3 leveren.

> **Status:** concept. De eerste toepassing is de gegevensdienst LaboratoryResults; andere zibs volgen.

## Ondersteunde zibs

| zib | Van (STU3, zib2017) | Naar (R4, zib2020) | Status |
|---|---|---|---|
| Patient | `nl-core-patient` | `nl-core-Patient` | in ontwikkeling |
| Zorgverlener | `nl-core-practitioner` | `nl-core-HealthProfessional-Practitioner` | in ontwikkeling |
| Zorgaanbieder | `nl-core-organization` | `nl-core-HealthcareProvider-Organization` | in ontwikkeling |
| LaboratoriumUitslag | `zib-LaboratoryTestResult-Observation` | `nl-core-LaboratoryTestResult` | in ontwikkeling |
| LaboratoriumUitslag (monster) | `zib-LaboratoryTestResult-Specimen` | `nl-core-LaboratoryTestResult.Specimen` | in ontwikkeling |

## Ontwerp

![Architectuur](docs/architectuur.svg)

**Runtime.** De converter is een black box: een STU3-Bundle erin, een R4-Bundle eruit, in één aanroep.

```
POST http://<host>:8090/transform?map=<canonical van de Bundle-map>
Content-Type: application/fhir+json   (of application/fhir+xml)
Accept:       application/fhir+json

Body:     STU3-Bundle
Antwoord: R4-Bundle
```

Resource-id's, `fullUrl`'s en `search.mode` blijven behouden, zodat referenties binnen de Bundle geldig blijven. Dezelfde conversie kan ook als command line-aanroep, met bestanden.

**Mappings in drie lagen.**

| Laag | Map | Doet |
|---|---|---|
| Bundle | `maps/bundle/Bundle.map` | Neemt Bundle-velden over en stuurt elke entry naar de juiste zib-map: op resourcetype, en waar één resourcetype meerdere zibs bedient (zoals Observation) ook op profiel. |
| zib | `maps/zibs/<Zib>.map` | Eén map per zib-profiel: profiel-URL's, extensies en zib-specifieke regels. |
| Datatypes | `maps/datatypes/<Datatype>.map` | Gedeelde regels, bijvoorbeeld voor codesystemen, namen, adressen en identifiers. Geïmporteerd door de zib-maps. |

Een nieuwe zib toevoegen is een nieuwe map in `maps/zibs/` plus een regel in de Bundle-map. Wat er inhoudelijk verandert tussen zib2017 en zib2020 staat per zib in de translatietabellen van Nictiz: [Zibtranslate](https://github.com/Nictiz/Zibtranslate).

**Waarom een STU3-context.** De Validator draait met `-version 3.0`, zodat de invoer als echte STU3 wordt gelezen. Voor de doeltypes verwijzen de maps naar de R4-definities met versienummer (`http://hl7.org/fhir/4.0/StructureDefinition/...`). Die komen uit het HL7-package `hl7.fhir.xver.r3`.

**Bouwstap.** Een STU3-context kan geen FML-tekst lezen. Elke map wordt daarom eenmalig gecompileerd in een R4-context en daarna omgezet naar STU3-formaat. De `.map`-bestanden zijn de bron; de gecompileerde StructureMaps worden gegenereerd. Per conversie wordt niets gecompileerd.

## Repository-indeling

```
maps/
  bundle/            Bundle.map: routeert entries naar zib-maps
  zibs/              één map per zib-profiel (Patient.map, LaboratoryTestResult.map, ...)
  datatypes/         gedeelde regels (Coding.map, HumanName.map, Address.map, ...)
tests/
  <gegevensdienst>/  per gegevensdienst, bijv. tests/LaboratoryResults/
    input/           STU3-testberichten
    expected/        verwachte R4-uitvoer
scripts/             bouwen, testen en valideren
docker/              container voor de converter in servermodus
docs/                ontwerp en architectuurplaat
.github/workflows/   CI: bouwen, testen, valideren bij elke wijziging
build/               gegenereerde StructureMaps (niet in Git)
```

Naamgeving: zib-maps heten naar het R4-profiel zonder voorvoegsel (`nl-core-LaboratoryTestResult` → `LaboratoryTestResult.map`). De canonical van een map is `<basis>/StructureMap/<bestandsnaam zonder .map>`. Groepsnamen zijn uniek over alle maps.

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

for f in maps/*/*.map; do
  m=$(basename "$f" .map)
  $V compile $BASE/$m -version 4.0 -ig "$f" -output build/r4/$m.json
  $V to-version 3.0 build/r4/$m.json -version 4.0 -do-native -output build/r3/$m.json
done
```

Na een wijziging hoeven alleen de gewijzigde maps opnieuw gebouwd te worden.

### Converteren als bestand

```bash
$V transform $BASE/Bundle tests/LaboratoryResults/input/bundle.json \
   -version 3.0 -ig hl7.fhir.xver.r3#1.2.1 -ig build/r3 \
   -output bundle-r4.json
```

### Converteren als HTTP-service

```bash
$V server 8090 -version 3.0 -ig hl7.fhir.xver.r3#1.2.1 -ig build/r3
```

De service is na ongeveer 45 seconden beschikbaar. Een conversie duurt daarna ongeveer 0,1 seconde per Bundle. Na een nieuwe build de service herstarten om de nieuwe maps te laden.

## Let op

- **Niet-gemapte elementen verdwijnen zonder melding.** Valideer de uitvoer altijd tegen de profielen, bijvoorbeeld met `$V bundle-r4.json -version 4.0 -ig nictiz.fhir.nl.r4.zib2020`, en vergelijk met `tests/<gegevensdienst>/expected/`.
- **Controleer of er uitvoer is.** De command line meldt "Successfully transformed", ook als een geïmporteerde map ontbreekt; er wordt dan geen uitvoerbestand geschreven.
- **De servermodus heeft geen authenticatie,** en beheerendpoints als `/stop` en `/loadIG` staan open. Alleen gebruiken op een afgeschermd netwerk.
- **Alleen synthetische testdata** in deze repository, geen patiëntgegevens.

## Bronnen

- [FHIR Mapping Language](https://hl7.org/fhir/R4/mapping-language.html)
- [HL7 FHIR Validator](https://github.com/hapifhir/org.hl7.fhir.core)
- [Nictiz STU3 zib2017](https://simplifier.net/nictizstu3-zib2017) en [Nictiz R4 zib2020](https://simplifier.net/nictiz-r4-zib2020)
- [Zibtranslate: translatiespecificaties zib2017 → zib2020](https://github.com/Nictiz/Zibtranslate)
