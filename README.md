# Automatic Invoice Labeling

## Introduzione al progetto

Questo progetto offre un sistema automatico per l'assegnazione del conto in cui registrare una transazione presente in una fattura. In particolare, il focus è sulle fatture elettroniche in formato XML ed è stato sviluppato un modello classificatore che prende come input le informazioni contenute in una riga della fattura XML e restituisce come output il conto di riferimento. 
Questa implementazione si concentra sulle fatture ricevute da un'unica attività commerciale (un bar), perciò il numero di conti rilevanti è limitato ai soli conti di spese attinenti al business di un bar. Future implementazioni generalizzeranno il modello a nuove attività commerciali.
