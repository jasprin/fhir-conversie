# Testset LaboratoryResults (R4 → STU3)

Testmateriaal voor de conversie van laboratoriumresultaten: Lab2patient (R4) als bron, de MedMij-gegevensdienst [LaboratoryResults 2020.01](https://informatiestandaarden.nictiz.nl/wiki/MedMij:V2020.01/FHIR_LaboratoryResults) (STU3) als doel.

## Herkomst

| | |
| --- | --- |
| Bron | [Nictiz/HL7-mappings](https://github.com/Nictiz/HL7-mappings), map `ada_2_fhir-r4/lab/l2p-1.0.0/beschikbaarstellen_laboratoriumresultaten/fhir_instance_bundles/` |
| Commit | [`7e7696c`](https://github.com/Nictiz/HL7-mappings/tree/7e7696cd6889815cf766caa57a1e9e42d6921e05/ada_2_fhir-r4/lab/l2p-1.0.0/beschikbaarstellen_laboratoriumresultaten/fhir_instance_bundles), opgehaald op 2026-11-12 |
| Standaard | [Lab2patient](https://informatiestandaarden.nictiz.nl/wiki/L2p:V2_FHIR_lab2patient), technisch ontwerp v2.0.0-beta.1 |
| Profielen | `nictiz.fhir.nl.r4.labexchange` 4.0.0-beta.2, `nictiz.fhir.nl.r4.nl-core` en `nictiz.fhir.nl.r4.zib2020` 0.12.0-labtrial.1 |
| Licentie | Geen licentiebestand in de repository; materiaal van Nictiz is in principe CC0 |
| Data | Synthetisch |

Waarom deze bron: Lab2patient is in R4 de opvolger van dezelfde transactie, het beschikbaarstellen van laboratoriumresultaten aan de patiënt. Het materiaal in [Nictiz-testscripts](https://github.com/Nictiz/Nictiz-testscripts/tree/main/src/LaboratoryResults-3-0) is afgevallen: het staat in `dev/` in plaats van `output/`, de testscripts zijn uitgeschakeld en de fixtures gebruiken extensies van een oudere beta.

## Inhoud van `bron/`

14 searchset-Bundles in XML, ongewijzigd. Elk scenario staat er twee keer in, als KWAL en als TEST. De varianten verschillen alleen in ids en identifiers.

| Scenario | Codering | Observations | Specimens |
| --- | --- | --- | --- |
| 0 Minimaal, vertaling | LOINC | 1 | 0 |
| 1 Maximaal bericht | LOINC, NHG | 1 | 1 |
| 2 Minimaal bericht | LOINC, NHG | 1 | 0 |
| 3 Maximaal, correctie | LOINC | 1 | 1 |
| 4 AB | LOINC | 5 | 5 |

Elke Bundle bevat verder 1 DiagnosticReport, 1 ServiceRequest, 1 Patient, 1 Practitioner, 1 PractitionerRole en 2 Organizations.

## Afgeleide testberichten in `input/`

De 7 KWAL-Bundles uit `bron/`, in JSON. De TEST-varianten voegen niets toe en zijn niet overgenomen. Het doel van `input/` is een set geldige R4-resources om de conversie mee te testen.

Aanpassingen ten opzichte van de bron:

- **Datums ingevuld.** De datum-placeholders van Nictiz, zoals `${DATE, T, D, -13}` (peildatum min 13 dagen), zijn vervangen door een datum ten opzichte van de vaste peildatum **2026-11-12**. Bij maanden en jaren blijft de dag gelijk. De placeholders staan alleen in velden met een datum (`effectiveDateTime`, `collectedDateTime`, `authoredOn`, `Period.start` en `.end`), dus de uitkomst is een geldige FHIR-datum.
- **XML naar JSON** met `validator_cli.jar convert -version 4.0`.
- **Laboratorium aangevuld.** In elke Bundle heeft het laboratorium (Organization met alleen type `L1`, waar `Observation.performer` en `DiagnosticReport.performer` met RESP naar verwijzen) geen naam en geen identifier. Dat is in strijd met `org-1`. Het heeft de synthetische naam "Klinisch Chemisch Laboratorium 't Proefje" gekregen.
- **Identifier van DiagnosticReport aangevuld** in scenario 4AB, waar hij ontbrak: `urn:oid:2.16.840.1.113883.2.4.3.11.60.25.1.1` / `AG04`, naar het patroon van de andere scenario's.

Verder is de inhoud ongewijzigd.

Opnieuw afleiden, vanuit de hoofdmap van de repository:

```bash
T=conversies/r4-stu3/tests/LaboratoryResults
python scripts/vul_datums.py 2026-11-12 /tmp/lab $T/bron/lu-blr-KWAL-*.xml
for f in /tmp/lab/*.xml; do
  java -Xmx1536m -jar validator_cli.jar convert "$f" -version 4.0 -tx n/a \
    -output $T/input/$(basename "$f" .xml).json
done
python scripts/lab_r4_aanvullen.py $T/input/*.json
```

## Validatie van `input/`

```bash
java -Xmx1536m -jar validator_cli.jar $T/input/*.json -version 4.0 \
  -ig nictiz.fhir.nl.r4.labexchange#4.0.0-beta.2 -sct nl -display-issues-are-warnings
```

- `-sct nl` is nodig voor de Nederlandse SNOMED-refsets in de waardelijsten. Zonder deze optie geeft tx.fhir.org de fout `The filter "concept in 2581000146104" is not understood`.
- `-display-issues-are-warnings`: de Nederlandse displays, zoals "Man", "Werkadres" en "Bloed", zijn correct, maar tx.fhir.org kent ze niet of anders.

Stand op 2026-11-12, met Validator 7.0.5: geen fouten in de inhoud meer. Wel resteren de volgende fouten, die buiten de testberichten liggen:

| Fout | Oorzaak |
| --- | --- |
| `Observation.performer` past op twee slices (performingHealthcareProvider en responsibleLaboratory) | Fout in `nl-core-LaboratoryTestResult` 0.12.0-labtrial.1: de discriminator wijst naar de extensie `event-performerFunction`, het patroon PPRF/RESP staat op de `value[x]` daarvan. |
| Gevolgfouten: "Kan geen match vinden voor profiel" bij Observation en Specimen | Volgen uit de fouten in deze tabel. |
| NHG-codes (tabel 45) niet in `TestCode-en-Onderzoek-Codelijsten` | tx.fhir.org kent het codesysteem van NHG niet. |
| `276833005` (24-uursurine) niet in `Monstermateriaal-en-Microorganisme-Codelijsten` | Nog niet uitgezocht; mogelijk een verschil in de SNOMED NL-editie op tx.fhir.org. |

ServiceRequest (`lu-OrderData`) blijft in de invoer staan; de conversie laat hem weg ([B10](../../../../docs/beslissingen.md#b10)).
