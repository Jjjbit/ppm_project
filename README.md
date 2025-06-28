# E-commerce Full Website

## descrizione
Questo progetto è un sito web di e-commerce completo che integra frontend e backend. Gli utenti sono divisi in tre ruoli principali: sellers, buyers e visitors.

### visitors
- possono visualizzare tutti i prodotti caricati sul sito, inclusi immagine, prezzi, sconti, descrizioni e il negozio di appartenenza.
- non possono avere wishlist, carrello e ordini.

### buyers
- devono registrarsi e accedere come buyers.
- non hanno un proprio negozio.
- possono:
    - visualizzare tutti i prodotti come i visitors.
    - modificare le informazioni personali, che comprendono username, email, password e address. 
    - avere carrello e wishlist.
    - aggiungere prodotti al carrello e alla wishlist.
    - rimuovere prodotti dal carrello e dalla wishlist
    - modificare la quantità dei prodotti aggiunti nel carrello.
    - visualizzare il totale del carrello.
    - effettuare il checkout: il carrello si svuota e i prodotti diventano un nuovo ordine.
    - visualizzare tutti gli ordini completati. Il dettaglio di un ordine completato contiene data e ore di creazione, ID ordine, nome dei prodotti, quantità, prezzo unitario e importo totale.
    - richiedere un reso specificando una motivazione.
    - controllare lo stato delle richieste di reso che può essere in attesa, approvata o rifiutata.

### sellers
- devono registrarsi e accedere come buyers.
- non hanno né carrello né wishlist.
- possono visualizzare tutti i prodotti del sito come visitors e buyers.
- modificare le informazioni personali, che comprendono username, email, password e address.
- hanno un negozio, dove possono:
    - aggiungere, modificare ed eliminare prodotti.
    - gestire le Store Category che sono categorie private del negozio, create solo dal proprietario del negozio e visibili solo nella pagina del negozio.
    - specificare nome di prodotto, immagine, prezzo, sconto, descrizione, stock, category e store category.
    - visualizzare tutti gli ordini ricevuti, username dei clienti che effettua l'ordine, prodotti ordinati, quantità, prezzi totali e lo stato delle richieste di reso.
    - visualizzare tutte le richieste di reso in attesa, con motivazione, data della richiesta e opzioni per accettare o rifiutare. Una volta gestita, la richiesta scompare dalla lista dei Return Requests. 

### Admin
- può creare categorie globali (category), visibili solo nella homepage. Queste categorie sono usate dai sellers per classificare i propri prodotti e permettono agli utenti di filtrare i prodotti per categoria.
- può creare ed eliminare un utente di tipo sellers e buyers.

## Tech Stack
- python 3.12.4
- Django 4.2.11
- PostgreSQL database
- HTML (Django templates)

## Deployment
- deployed on Railway: []

## Setup & Run
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


