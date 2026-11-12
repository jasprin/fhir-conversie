"""Vult ontbrekende verplichte gegevens aan in de R4-testberichten van LaboratoryResults (Lab2patient).

Het bronmateriaal van Nictiz is op twee punten niet geldig tegen de profielen:
- het laboratorium (Organization met alleen type L1) heeft geen naam en geen identifier (org-1);
- het DiagnosticReport in scenario 4AB heeft geen identifier (minimaal 1 verplicht).

Gebruik: python lab_r4_aanvullen.py <bestand.json> ...
"""
import json
import pathlib
import sys

LAB_NAAM = "Klinisch Chemisch Laboratorium 't Proefje"
DR_SYSTEEM = "urn:oid:2.16.840.1.113883.2.4.3.11.60.25.1.1"


def is_lab(org: dict) -> bool:
    return any(
        c.get("code") == "L1"
        for t in org.get("type", [])
        for c in t.get("coding", [])
    )


def main() -> None:
    for pad in map(pathlib.Path, sys.argv[1:]):
        bundle = json.loads(pad.read_text(encoding="utf-8"))
        wijzigingen = []
        for entry in bundle["entry"]:
            r = entry["resource"]
            if r["resourceType"] == "Organization" and is_lab(r) and not r.get("name") and not r.get("identifier"):
                # name direct na type, zodat de volgorde van de elementen klopt
                nieuw = {}
                for k, v in r.items():
                    nieuw[k] = v
                    if k == "type":
                        nieuw["name"] = LAB_NAAM
                r.clear()
                r.update(nieuw)
                wijzigingen.append("Organization.name")
            if r["resourceType"] == "DiagnosticReport" and not r.get("identifier"):
                nieuw = {}
                for k, v in r.items():
                    if k in ("basedOn", "status") and "identifier" not in nieuw:
                        nieuw["identifier"] = [{"system": DR_SYSTEEM, "value": "AG04"}]
                    nieuw[k] = v
                r.clear()
                r.update(nieuw)
                wijzigingen.append("DiagnosticReport.identifier")
        pad.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{pad.name}: {', '.join(wijzigingen) or 'geen wijzigingen'}")


if __name__ == "__main__":
    main()
