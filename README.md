# Automatic Invoice Labeling

## Project Overview

Questo progetto offre un sistema automatico per l'assegnazione del conto in cui registrare una transazione presente in una fattura. In particolare, il focus è sulle fatture elettroniche in formato XML ed è stato sviluppato un modello classificatore che prende come input le informazioni contenute in una riga della fattura XML e restituisce come output il conto di riferimento. 
Questa implementazione si concentra sulle fatture ricevute da un'unica attività commerciale (un bar), perciò il numero di conti rilevanti è limitato ai soli conti di spese attinenti al business di un bar. Future implementazioni generalizzeranno il modello a nuove attività commerciali.

## Project Organization

L'intero progetto, in questa prima implementazione, parte dal presupposto di aver già formato una tabella Excel in cui ogni riga descrive una spesa (una riga di fattura XML) e sia già stato fatto il matching con le corrispondenti scritture in prima nota. L'organizzazione è la seguente:
1) Notebook 1 contiene tutta la fase di data-cleaning e pre-processing usando la libreria pandas in modo da trasformare l'iniziale tabella Excel in un DataFrame adatto al training di un modello ML di sklearn. Dopodichè, in Notebook 1 sono presenti anche le celle per il training e il test dei più comuni modelli di classificazione e l'analisi degli errori commessi, con particolare attenzione sui modelli Random Forest e AdaBoost che forniscono le prestazioni migliori. Ulteriori commenti sono riportati cella per cella nel notebook.
2) Notebook 2 parte dal dataset pre-processato in Notebook 1 (df_preprocessed) e dal modello Random Forest già fittato (finalized_model.sav) e presenta le celle per eseguire la Cross-Validazione e la Grid Search dei migliori iper-parametri. Successivamente, è implementato lo pseudo-labeling dei dati non supervisionati in un approccio semi-supervised learning, usando il modello Random Forest ottenuto in Notebook 1.
3) Le labels proposte dal classificatore sono validate grazie all'algoritmo di ricerca A* che è implementato in un file a parte e confronta le pseudo-labels proposte (nel file pseudo_labels) con le rispettive quantità registrate in prima nota (df_rows), per ampliare il set di dati supervisionati. Il risultato è un insieme di labels validate (nel file pseudo_labels_validated) con cui ampliare il training set.

Infine, Diagram.jpeg schematizza e illustra i benefici derivanti dall'applicazione dell'algoritmo A* all'intera pipeline, rispetto al caso base in cui si segue un approccio puramente supervised.
