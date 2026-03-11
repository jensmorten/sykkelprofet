# Bli sykkelprofet i egen by!
Bygg din egen prophet-modell!

* Ta gjerne utgangspunkt i notebooken "prophet_starter": https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/konkurranse/prophet_starter.ipynb

* Juster modellen etter eget ønske

* Last opp prediksjonen på https://sykkelprofet-konkurranse.streamlit.app/

fila må inneholde to kollonner: ds og yhat, separert med komma
ds må innholde tidstempel fra 2025-05-01 03:00:00 til 2025-09-30 21:00:00 (3-timers intervall). Se eksempel på gyldig fil er: https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/konkurranse/submission_testing_w.csv


---- 
### Event: https://event.bouvet.no/event/2acde1ac-e6e7-4ea0-b1fc-dc47e25e4471
----
### Oppsett av python på windows (valgfritt):

* Last ned WinPython og pakk ut filene til en mappe du velger: https://winpython.github.io/
* Åpne den utpakkede mappen og kjør WinPython Command Prompt.exe.
* Naviger til GitHub-mappen med oppgaven ved å skrive cd C:\[....]\GitHub\GitHub\sykkelprofet\konkurranse\
* Skriv jupyter notebook for å starte Jupyter Notebook.
* Velg notatboken «prophet_starter» i nettleservinduet som åpnes.
* Velg Run → Run all cells i toppmenyen for å forsikre deg om at eksempelet fungerer.
* Om kall til prophet feiler, må du sannsynligvis installere prophet ved å opprette ny celle og skrive %pip install prophet i denne cella
