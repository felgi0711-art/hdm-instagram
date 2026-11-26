# hdm-instagram

Automatisches Posten für @hausdesmannes_laser.

- Jeder freigegebene Post liegt in `posts/<datum>-<thema>/` mit `image.jpg` und `caption.txt`.
- Sobald ein Post hier landet, veröffentlicht ihn der Job `.github/workflows/publish.yml` über die Instagram-Schnittstelle von Meta.
- Der Zugangsschlüssel liegt verschlüsselt als Secret `IG_ACCESS_TOKEN`, nie im Code.
- Nach dem Posten schreibt der Job `published.json` mit dem Link zum Post in den Ordner.
