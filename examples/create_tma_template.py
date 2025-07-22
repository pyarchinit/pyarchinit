#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per creare un template Excel per l'importazione TMA
"""

import pandas as pd
import os

def create_tma_template():
    """Crea un file Excel template con tutti i campi TMA"""
    
    # Definisci le colonne con descrizioni
    columns_info = [
        # Campi obbligatori
        ('Sito', 'Nome del sito archeologico (OBBLIGATORIO)'),
        ('Area', 'Area di scavo (OBBLIGATORIO)'),
        ('US', 'Unità stratigrafica (OBBLIGATORIO)'),
        ('Materiale', 'Tipo di materiale: CERAMICA, INDUSTRIA LITICA, LITICA, METALLO (OBBLIGATORIO)'),
        ('Denominazione collocazione', 'Dove è conservato il materiale (OBBLIGATORIO)'),
        ('Cassetta', 'Numero della cassetta (OBBLIGATORIO)'),
        ('Località', 'Località del ritrovamento (OBBLIGATORIO)'),
        ('Fascia cronologica', 'Periodo cronologico (OBBLIGATORIO)'),
        ('Categoria', 'Categoria del materiale (OBBLIGATORIO)'),
        
        # Campi opzionali - Localizzazione
        ('Tipologia collocazione', 'Tipo: Magazzino, Materiali all\'aperto, Museo'),
        ('Vecchia collocazione', 'Precedente collocazione del materiale'),
        ('Denominazione scavo', 'Nome dello scavo'),
        ('Saggio', 'Saggio di scavo'),
        ('Vano/Locus', 'Vano o Locus'),
        ('Data scavo', 'Data dello scavo'),
        
        # Campi opzionali - Ricognizione
        ('Data ricognizione', 'Data della ricognizione'),
        ('Specifiche ricognizione', 'Note sulla ricognizione'),
        ('Tipo acquisizione', 'Modalità di acquisizione'),
        ('Data acquisizione', 'Data di acquisizione'),
        
        # Campi opzionali - Datazione e Quantità
        ('Frazione cronologica', 'Suddivisione del periodo'),
        ('Cronologie', 'Cronologie specifiche'),
        ('N. reperti', 'Numero di reperti'),
        ('Peso', 'Peso totale'),
        
        # Campi opzionali - Dati tecnici
        ('Indicazione oggetti', 'Descrizione degli oggetti'),
        ('Inventario', 'Numero di inventario'),
        ('Classe', 'Classe del materiale'),
        ('Precisazione tipologica', 'Tipo specifico'),
        ('Definizione', 'Definizione del materiale'),
        ('Cronologia MAC', 'Cronologia specifica MAC'),
        ('Quantità', 'Quantità MAC'),
        
        # Campi opzionali - Documentazione
        ('Tipo fotografia', 'Tipi di foto (separare con ;)'),
        ('Codice foto', 'Codici delle foto (separare con ;)'),
        ('Tipo disegno', 'Tipi di disegni (separare con ;)'),
        ('Codice disegno', 'Codici dei disegni (separare con ;)'),
        ('Autore disegno', 'Autori dei disegni (separare con ;)')
    ]
    
    # Crea DataFrame con esempi
    data = {
        'Sito': ['Roma', 'Pompei', 'Ostia'],
        'Area': ['A', 'B', 'C'],
        'US': ['101', '202', '303'],
        'Materiale': ['CERAMICA', 'METALLO', 'LITICA'],
        'Denominazione collocazione': ['Magazzino Centrale', 'Deposito 1', 'Magazzino 2'],
        'Cassetta': ['C001', 'C002', 'C003'],
        'Località': ['Roma - Foro Romano', 'Pompei - Casa del Fauno', 'Ostia - Terme'],
        'Fascia cronologica': ['I sec. d.C.', 'I sec. a.C. - I sec. d.C.', 'II sec. d.C.'],
        'Categoria': ['Ceramica comune', 'Bronzo', 'Industria litica'],
        'Tipologia collocazione': ['Magazzino', 'Magazzino', 'Museo'],
        'Vecchia collocazione': ['', '', 'Vecchio deposito'],
        'Denominazione scavo': ['Scavo 2023', 'Scavo 2022', 'Scavo 2021'],
        'Saggio': ['S1', 'S2', 'S3'],
        'Vano/Locus': ['Vano A', 'Locus 12', 'Vano C'],
        'Data scavo': ['15/05/2023', '20/06/2022', '10/09/2021'],
        'Data ricognizione': ['', '01/03/2022', ''],
        'Specifiche ricognizione': ['', 'Ricognizione sistematica area nord', ''],
        'Tipo acquisizione': ['Scavo stratigrafico', 'Scavo stratigrafico', 'Recupero'],
        'Data acquisizione': ['15/05/2023', '20/06/2022', '10/09/2021'],
        'Frazione cronologica': ['Prima metà', 'Passaggio', 'Piena età'],
        'Cronologie': ['Età giulio-claudia', 'Tarda repubblica - primo impero', 'Età adrianea'],
        'N. reperti': ['15', '3', '7'],
        'Peso': ['250 g', '120 g', '500 g'],
        'Indicazione oggetti': ['Frammenti di terra sigillata italica', 'Fibula in bronzo', 'Lame e schegge'],
        'Inventario': ['INV2023/001', 'INV2022/045', 'INV2021/123'],
        'Classe': ['Terra sigillata', 'Ornamento personale', 'Strumenti'],
        'Precisazione tipologica': ['Coppa Conspectus 22', 'Fibula Aucissa', 'Lama ritoccata'],
        'Definizione': ['Coppa', 'Fibula', 'Lama'],
        'Cronologia MAC': ['30-70 d.C.', '25 a.C. - 50 d.C.', '100-150 d.C.'],
        'Quantità': ['1', '1', '3'],
        'Tipo fotografia': ['Generale;Dettaglio', 'Fronte;Retro', 'Generale'],
        'Codice foto': ['IMG_001;IMG_002', 'IMG_003;IMG_004', 'IMG_005'],
        'Tipo disegno': ['Profilo', 'Vista frontale', ''],
        'Codice disegno': ['DIS_001', 'DIS_002', ''],
        'Autore disegno': ['M. Rossi', 'L. Bianchi', '']
    }
    
    # Crea DataFrame
    df = pd.DataFrame(data)
    
    # Crea un secondo sheet con le istruzioni
    instructions = {
        'Campo': [col[0] for col in columns_info],
        'Descrizione': [col[1] for col in columns_info],
        'Obbligatorio': ['SI' if 'OBBLIGATORIO' in col[1] else 'NO' for col in columns_info]
    }
    
    df_instructions = pd.DataFrame(instructions)
    
    # Salva in Excel con due fogli
    output_file = 'TMA_Template.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Foglio dati
        df.to_excel(writer, sheet_name='Dati_TMA', index=False)
        
        # Foglio istruzioni
        df_instructions.to_excel(writer, sheet_name='Istruzioni', index=False)
        
        # Formatta il file
        workbook = writer.book
        
        # Formatta foglio dati
        worksheet_data = writer.sheets['Dati_TMA']
        
        # Imposta larghezza colonne
        for idx, col in enumerate(df.columns):
            column_letter = chr(65 + idx)  # A, B, C, etc.
            if idx < 26:  # Gestisce solo le prime 26 colonne
                worksheet_data.column_dimensions[column_letter].width = 20
        
        # Formatta foglio istruzioni
        worksheet_instructions = writer.sheets['Istruzioni']
        worksheet_instructions.column_dimensions['A'].width = 30
        worksheet_instructions.column_dimensions['B'].width = 80
        worksheet_instructions.column_dimensions['C'].width = 15
    
    print(f"Template creato: {output_file}")
    print("\nIl file contiene:")
    print("- Foglio 'Dati_TMA': template con 3 record di esempio")
    print("- Foglio 'Istruzioni': descrizione di tutti i campi")
    print("\nPuoi modificare i dati di esempio o aggiungere nuove righe.")
    print("Assicurati di mantenere i nomi delle colonne nella prima riga!")

    # Crea anche un file CSV vuoto solo con le intestazioni
    empty_df = pd.DataFrame(columns=df.columns)
    empty_df.to_csv('TMA_Template_vuoto.csv', index=False)
    print(f"\nCreato anche template vuoto: TMA_Template_vuoto.csv")


if __name__ == "__main__":
    create_tma_template()
