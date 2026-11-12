"""Vult datum-placeholders van Nictiz in, zoals ${DATE, T, D, -13}, ten opzichte van een vaste datum.

Gebruik: python vul_datums.py <peildatum JJJJ-MM-DD> <uitvoermap> <bestand.xml> ...
"""
import calendar
import datetime as dt
import pathlib
import re
import sys

PATROON = re.compile(r"\$\{DATE,\s*T,\s*([DMY]),\s*(-?\d+)\}")


def verschuif(peil: dt.date, eenheid: str, n: int) -> dt.date:
    if eenheid == "D":
        return peil + dt.timedelta(days=n)
    maanden = n if eenheid == "M" else 12 * n
    totaal = peil.year * 12 + (peil.month - 1) + maanden
    jaar, maand = divmod(totaal, 12)
    maand += 1
    dag = min(peil.day, calendar.monthrange(jaar, maand)[1])
    return dt.date(jaar, maand, dag)


def main() -> None:
    peil = dt.date.fromisoformat(sys.argv[1])
    uit = pathlib.Path(sys.argv[2])
    uit.mkdir(parents=True, exist_ok=True)
    for pad in map(pathlib.Path, sys.argv[3:]):
        tekst = pad.read_text(encoding="utf-8")
        nieuw, aantal = PATROON.subn(
            lambda m: verschuif(peil, m.group(1), int(m.group(2))).isoformat(), tekst
        )
        if "${" in nieuw:
            sys.exit(f"Onbekende placeholder over in {pad.name}")
        (uit / pad.name).write_text(nieuw, encoding="utf-8")
        print(f"{pad.name}: {aantal} vervangen")


if __name__ == "__main__":
    main()
