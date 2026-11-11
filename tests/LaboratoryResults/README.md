# Testset LaboratoryResults

Gebaseerd op het kwalificatiemateriaal van Nictiz voor [Laboratoriumresultaten Raadplegen (MedMij 2020.01)](https://informatiestandaarden.nictiz.nl/wiki/MedMij:V2020.01/Laboratoriumresultaten_Raadplegen), scenario 1.1.

| Map | Inhoud |
|---|---|
| `nictiz/` | Ongewijzigde kopie van de STU3-resources van Nictiz (CC0). Bron: [Nictiz-testscripts](https://github.com/Nictiz/Nictiz-testscripts/tree/ee5b99ba23fde2eb2a383df3a99c52c28cc84f7d/src/LaboratoryResults-2-0/Cert/_reference), commit `ee5b99b`. |
| `input/bundle.json` | STU3-searchset-Bundle in JSON, samengesteld uit `nictiz/`. |
| `expected/` | Verwachte R4-uitvoer. |

## Afwijkingen van het origineel in `input/bundle.json`

- De losse resources staan samen in één Bundle. De drie Observations hebben `search.mode` `match`, de Patient, PractitionerRole, Practitioner en Organization hebben `include`. In het echte antwoord op `Observation?category=http://snomed.info/sct|49581000146104` zitten alleen de Observations; de andere resources staan erin om ook hun maps te testen.
- `fullUrl` gebruikt de fictieve basis `https://xis.example.nl/fhir`.
- De plaatshouder `${DATE, T, D, -90}` in `effectiveDateTime` is vervangen door de vaste datum `2026-08-13`.
- Omgezet van XML naar JSON met `validator_cli.jar convert`.
- Geen Specimen: het kwalificatiemateriaal bevat er geen.

## Validatie van de invoer

Tegen `nictiz.fhir.nl.stu3.zib2017#2.4.0` geeft de Bundle geen structuurfouten. Wel meldt de Validator fouten in de terminologie, die al in het origineel zitten:

- De categorie `49581000146104` komt uit de Nederlandse editie van SNOMED en is onbekend in de internationale editie.
- Weergavenamen wijken af van de terminologieserver, bijvoorbeeld bij LOINC en bij `AdministrativeGender` (`Vrouw` in plaats van `Female`).
- Door die fouten matchen de referenties naar Patient, PractitionerRole en Practitioner niet met hun profiel.
