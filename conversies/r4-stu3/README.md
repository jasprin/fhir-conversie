# Conversie R4 → STU3

Zet R4-resources op de Nictiz-profielen voor zib2020 om naar STU3-resources op de Nictiz-profielen voor zib2017.

> **Status:** in opzet. Het bronmateriaal voor LaboratoryResults staat klaar; er zijn nog geen maps, mappingdocumenten of afgeleide testberichten.

| | Bron | Doel |
| --- | --- | --- |
| FHIR-versie | R4 (4.0.1) | STU3 (3.0.2) |
| Profielen | `nictiz.fhir.nl.r4.nl-core` 0.12.0-labtrial.1, `nictiz.fhir.nl.r4.labexchange` 4.0.0-beta.2 (Lab2patient) | `nictiz.fhir.nl.stu3.zib2017` 2.4.0 (MedMij LaboratoryResults 2020.01) |
| Context van de Validator | `-version 4.0` | doeltypes uit `hl7.fhir.xver.r4` 1.2.0 |
| Canonical van de Bundle-map | | `http://medmij.nl/fhir/StructureMap/r4-stu3-Bundle` |

## Gegevensdiensten

| Gegevensdienst | Status |
| --- | --- |
| LaboratoryResults | in opzet, bronmateriaal staat klaar ([tests/LaboratoryResults](tests/LaboratoryResults/README.md)) |

## Profielen voor LaboratoryResults

Voorlopig; afgeleid uit het bronmateriaal van Lab2patient.

| Resource | Van (R4) | Naar (STU3) | Map |
| --- | --- | --- | --- |
| Observation | `nl-core-LaboratoryTestResult` | `zib-LaboratoryTestResult-Observation` | `LaboratoryTestResult` |
| DiagnosticReport | `lu-LaboratoryTestResult-DiagnosticReport` | `zib-LaboratoryTestResult-DiagnosticReport` | `LaboratoryTestResult-DiagnosticReport` |
| ServiceRequest | `lu-OrderData` | valt voorlopig weg ([B10](../../docs/beslissingen.md#b10)) | |
| Specimen | `nl-core-LaboratoryTestResult.Specimen` | `zib-LaboratoryTestResult-Specimen` | `LaboratoryTestResult.Specimen` |
| Patient | `nl-core-Patient` | `nl-core-patient` | `Patient` |
| Practitioner | `nl-core-HealthProfessional-Practitioner` | `nl-core-practitioner` | `HealthProfessional-Practitioner` |
| PractitionerRole | `nl-core-HealthProfessional-PractitionerRole` | `nl-core-practitionerrole` | `HealthProfessional-PractitionerRole` |
| Organization | `nl-core-HealthcareProvider-Organization` | `nl-core-organization` | `HealthcareProvider-Organization` |

## Indeling

```text
maps/          FML-maps (Bundle.map, resources/, datatypes/)
mappings/      per map de regels en keuzes (.md)
tests/         per gegevensdienst: bron/, input/, expected/
```
