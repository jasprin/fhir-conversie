# Conversie van FHIR STU3 naar R4

Converteert FHIR-resources van **STU3** naar **R4**, met mappings in de [FHIR Mapping Language](https://hl7.org/fhir/R4/mapping-language.html) (FML). Uitgevoerd door de [HL7 FHIR Validator](https://github.com/hapifhir/org.hl7.fhir.core).

Naast de FHIR-versie zetten de mappings waar nodig ook het profiel om, bijvoorbeeld van de Nictiz-profielen op zib2017 naar die op zib2020. De mappings zijn herbruikbaar voor iedereen die STU3-data als R4 nodig heeft, bijvoorbeeld van MedMij-gegevensdiensten die nog STU3 leveren.

> **Status:** concept. De eerste toepassing is de gegevensdienst LaboratoryResults; andere resources en profielen volgen.

## Ondersteunde profielen

| Resource | Van (STU3) | Naar (R4) | Status |
|---|---|---|---|
| Patient | `nl-core-patient` | `nl-core-Patient` | in ontwikkeling |
| Practitioner | `nl-core-practitioner` | `nl-core-HealthProfessional-Practitioner` | in ontwikkeling |
| PractitionerRole | `nl-core-practitionerrole` | `nl-core-HealthProfessional-PractitionerRole` | in ontwikkeling |
| Organization | `nl-core-organization` | `nl-core-HealthcareProvider-Organization` | in ontwikkeling |
| Observation | `zib-LaboratoryTestResult-Observation` | `nl-core-LaboratoryTestResult` | in ontwikkeling |
| Specimen | `zib-LaboratoryTestResult-Specimen` | `nl-core-LaboratoryTestResult.Specimen` | in ontwikkeling |

## Ontwerp

![Architectuur](docs/architectuur.svg)

**Runtime.** De converter is een black box: een STU3-Bundle erin, een R4-Bundle eruit, in één aanroep.

```
POST http://<host>:8090/transform?map=http://medmij.nl/fhir/StructureMap/stu3-r4-Bundle
Content-Type: application/fhir+json   (of application/fhir+xml)
Accept:       application/fhir+json

Body:     STU3-Bundle
Antwoord: R4-Bundle
```

Resource-id's, `fullUrl`'s en `search.mode` blijven behouden, zodat referenties binnen de Bundle geldig blijven. Dezelfde conversie kan ook als command line-aanroep, met bestanden.

**Mappings in drie lagen.**

| Laag | Map | Doet |
|---|---|---|
| Bundle | `maps/Bundle.map` | Neemt Bundle-velden over en stuurt elke entry naar de juiste map: op resourcetype, en waar één resourcetype meerdere profielen kent (zoals Observation) ook op profiel. |
| Resource | `maps/resources/<Resourcetype>/<Map>.map` | Eén map per resourcetype zonder profiel, of per profiel: de versieconversie plus profiel-URL's, extensies en profielspecifieke regels. |
| Datatypes | `maps/datatypes/<Datatype>.map` | Gedeelde regels, bijvoorbeeld voor codesystemen, namen, adressen en identifiers. Geïmporteerd door de resource-maps. |

Een resource of profiel toevoegen is een nieuwe map in `maps/resources/` plus een regel in de Bundle-map. Voor profielen op basis van zibs staat wat er inhoudelijk verandert tussen zib2017 en zib2020 in de translatietabellen van Nictiz: [Zibtranslate](https://github.com/Nictiz/Zibtranslate).

**Waarom een STU3-context.** De Validator draait met `-version 3.0`, zodat de invoer als echte STU3 wordt gelezen. Voor de doeltypes verwijzen de maps naar de R4-definities met versienummer (`http://hl7.org/fhir/4.0/StructureDefinition/...`). Die komen uit het HL7-package `hl7.fhir.xver.r3`.

**Bouwstap.** Een STU3-context kan geen FML-tekst lezen. Elke map wordt daarom eenmalig gecompileerd in een R4-context en daarna omgezet naar STU3-formaat. De `.map`-bestanden zijn de bron; de gecompileerde StructureMaps worden gegenereerd. Per conversie wordt niets gecompileerd.

## Repository-indeling

```
maps/
  Bundle.map         routeert entries naar de resource-maps
  resources/         per resourcetype een map, met één map per profiel
    Observation/     LaboratoryTestResult.map, ...
    Patient/         Patient.map
    ...
  datatypes/         gedeelde regels (Coding.map, HumanName.map, Address.map, ...)
tests/
  <gegevensdienst>/  per gegevensdienst, bijv. tests/LaboratoryResults/
    nictiz/          ongewijzigd uitgangsmateriaal (kwalificatiemateriaal van Nictiz)
    input/           STU3-testberichten
    expected/        verwachte R4-uitvoer
scripts/             bouwen, testen en valideren
docker/              container voor de converter in servermodus
docs/                ontwerp en architectuurplaat
.github/workflows/   CI: bouwen, testen, valideren bij elke wijziging
build/               gegenereerde StructureMaps (niet in Git)
```

Naamgeving: een map voor een profiel heet naar het R4-profiel zonder voorvoegsel (`nl-core-LaboratoryTestResult` → `LaboratoryTestResult.map`); een map zonder profiel naar het resourcetype. Bestandsnamen en groepsnamen zijn uniek over alle maps.

Canonical: `http://medmij.nl/fhir/StructureMap/stu3-r4-<bestandsnaam zonder .map>`, bijvoorbeeld `http://medmij.nl/fhir/StructureMap/stu3-r4-LaboratoryTestResult`. Dit volgt het MedMij-patroon `http://medmij.nl/fhir/<Resourcetype>/<id>`. Het voorvoegsel `stu3-r4-` houdt de namen uniek naast andere StructureMaps van MedMij.

## Gebruik

### Vereisten

- Java 17 of hoger
- Ongeveer 1 GB geheugen voor de Validator. Begrens de heap met `-Xmx1536m`; zonder die grens kan Java bij weinig vrij geheugen vastlopen.
- Netwerktoegang tot `packages.fhir.org` bij de eerste start. Daarna komen de packages uit de lokale cache (`~/.fhir/packages`).
- Voor bouwen en converteren op de command line: een terminologieserver (standaard `tx.fhir.org`). `transform` weigert te starten zonder. De HTTP-service heeft er geen nodig (`-tx n/a`).

Gebruik de meest recente versie van de Validator. Draai na een update de testset.

```bash
curl -L -o validator_cli.jar \
  https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar
```

### Maps bouwen

Per map: compileren in een R4-context en omzetten naar STU3-formaat.

```bash
PREFIX=http://medmij.nl/fhir/StructureMap/stu3-r4-   # canonical = voorvoegsel + mapnaam
V="java -Xmx1536m -jar validator_cli.jar"

for f in $(find maps -name '*.map'); do
  m=$(basename "$f" .map)
  $V compile $PREFIX$m -version 4.0 -ig "$f" -output build/r4/$m.json
  $V to-version 3.0 build/r4/$m.json -version 4.0 -do-native -output build/r3/$m.json
done
```

Bij `compile` is het eerste argument de canonical van de map; het `.map`-bestand gaat mee via `-ig`. Een STU3-context kan het bestand niet lezen (`Unsupported format`), daarom gebeurt het compileren met `-version 4.0`.

Na een wijziging hoeven alleen de gewijzigde maps opnieuw gebouwd te worden.

### Converteren als bestand

```bash
$V transform ${PREFIX}Bundle tests/LaboratoryResults/input/bundle.json \
   -version 3.0 -ig hl7.fhir.xver.r3#1.2.1 -ig build/r3 \
   -output bundle-r4.json
```

### Converteren als HTTP-service

```bash
$V server 8090 -version 3.0 -tx n/a -ig hl7.fhir.xver.r3#1.2.1 -ig build/r3
```

- `-tx n/a` maakt de service onafhankelijk van een terminologieserver. Zonder deze optie start de service niet als `tx.fhir.org` onbereikbaar is.
- De service luistert standaard alleen op `localhost`. Voor toegang van buiten de machine, bijvoorbeeld in een container, is `-allowNetworkAccess` nodig.
- Met een warme package-cache is de service na ongeveer 10 seconden beschikbaar; de eerste start duurt langer omdat de packages dan worden gedownload. Een conversie duurt daarna minder dan 0,1 seconde per Bundle.
- Na een nieuwe build de service herstarten om de nieuwe maps te laden. Stoppen kan met `POST /stop`.
- Documentatie van alle endpoints staat op `/docs` (OpenAPI: `/openapi.json`).

Een aanroep zonder `map` geeft een OperationOutcome met de melding `Missing required query parameter: map`.

## Let op

- **Niet-gemapte elementen verdwijnen zonder melding.** Dat geldt ook voor hele resources: een entry waarvoor de Bundle-map geen regel heeft, komt in de uitvoer terug met alleen `fullUrl` en `search`, zonder `resource`. Valideer de uitvoer altijd tegen de profielen, bijvoorbeeld met `$V bundle-r4.json -version 4.0 -ig nictiz.fhir.nl.r4.zib2020`, en vergelijk met `tests/<gegevensdienst>/expected/`.
- **Controleer of er uitvoer is.** `compile` en `transform` melden "Successfully compiled" of "Successfully transformed", ook als er iets misging, bijvoorbeeld als een map niet gevonden wordt. Er wordt dan geen uitvoerbestand geschreven. De echte fout staat eerder in de uitvoer (`...Failure:`).
- **De servermodus heeft geen authenticatie,** en beheerendpoints als `/stop` en `/loadIG` staan open voor iedereen die de service kan bereiken. Gebruik `-allowNetworkAccess` alleen op een afgeschermd netwerk.
- **Alleen synthetische testdata** in deze repository, geen patiëntgegevens.

## Bronnen

- [FHIR Mapping Language](https://hl7.org/fhir/R4/mapping-language.html)
- [HL7 FHIR Validator](https://github.com/hapifhir/org.hl7.fhir.core) en [Using the FHIR Validator](https://confluence.hl7.org/spaces/FHIR/pages/35718580/Using+the+FHIR+Validator). De ingebouwde hulp is actueler: `java -jar validator_cli.jar help <commando>`.
- [Nictiz STU3 zib2017](https://simplifier.net/nictizstu3-zib2017) en [Nictiz R4 zib2020](https://simplifier.net/nictiz-r4-zib2020)
- [Zibtranslate: translatiespecificaties zib2017 → zib2020](https://github.com/Nictiz/Zibtranslate)
