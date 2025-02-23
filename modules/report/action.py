class ArchaeologicalActions:
    @staticmethod
    def SintesiIntroduttiva(context):
        """Gestisce l'analisi introduttiva del sito"""
        try:
            site_data = context.get("site_data", {})
            us_data = context.get("us_data", [])
            materials_data = context.get("materials_data", [])

            # Analisi dei dati
            risultati = {
                'site_info': {
                    'nome_sito': site_data.get('nome_sito'),
                    'comune': site_data.get('comune'),
                    'provincia': site_data.get('provincia')
                },
                'statistics': {
                    'total_us': len(us_data),
                    'total_materials': len(materials_data)
                }
            }
            return risultati
        except Exception as e:
            return f"Errore nell'analisi introduttiva: {str(e)}"

    @staticmethod
    def AnalisiAreaScavo(context):
        """Gestisce l'analisi dell'area di scavo"""
        try:
            us_data = context.get("us_data", [])
            if not us_data:
                return "Errore: Dati US non disponibili"

            aree_scavo = set(us.get('area') for us in us_data if us.get('area'))
            tecniche_scavo = set(us.get('tecnica_scavo') for us in us_data if us.get('tecnica_scavo'))

            return {
                'aree_identificate': list(aree_scavo),
                'tecniche_utilizzate': list(tecniche_scavo),
                'totale_us': len(us_data)
            }
        except Exception as e:
            return f"Errore nell'analisi dell'area: {str(e)}"

    @staticmethod
    def AnalisiStratigrafica(context):
        """
        Gestisce l'analisi stratigrafica completa dei dati US.
        Organizza e analizza:
        - Elenco delle US
        - Rapporti stratigrafici
        - Interpretazione delle fasi
        """
        try:
            us_data = context.get("us_data", [])
            if not us_data:
                return "Errore: Dati US non disponibili"

            # Organizza le US per fase/periodo
            us_by_phase = {}
            for us in us_data:
                phase = us.get('fase') or us.get('periodo') or 'Non specificata'
                if phase not in us_by_phase:
                    us_by_phase[phase] = []
                us_by_phase[phase].append(us)

            # Analizza i rapporti stratigrafici
            stratigraphy_relations = {}
            for us in us_data:
                us_id = us.get('id_us')
                if us_id:
                    relations = {
                        'copre': us.get('copre', '').split(','),
                        'coperto_da': us.get('coperto_da', '').split(','),
                        'taglia': us.get('taglia', '').split(','),
                        'tagliato_da': us.get('tagliato_da', '').split(','),
                        'riempie': us.get('riempie', '').split(','),
                        'riempito_da': us.get('riempito_da', '').split(','),
                        'uguale_a': us.get('uguale_a', '').split(',')
                    }
                    # Pulisce le liste vuote e spazi
                    relations = {k: [x.strip() for x in v if x.strip()] for k, v in relations.items()}
                    stratigraphy_relations[us_id] = relations

            # Analisi delle quote
            quote_analysis = {}
            for us in us_data:
                us_id = us.get('id_us')
                if us_id:
                    try:
                        quota_max = float(us.get('quota_max', 0))
                        quota_min = float(us.get('quota_min', 0))
                        quote_analysis[us_id] = {
                            'quota_max': quota_max,
                            'quota_min': quota_min,
                            'differenza_quota': round(quota_max - quota_min, 2)
                        }
                    except (ValueError, TypeError):
                        quote_analysis[us_id] = {
                            'quota_max': None,
                            'quota_min': None,
                            'differenza_quota': None
                        }

            # Organizza i risultati
            risultati = {
                'totale_us': len(us_data),
                'fasi_identificate': {
                    fase: {
                        'numero_us': len(us_list),
                        'us_ids': [us.get('id_us') for us in us_list],
                        'tipologie': list(set(us.get('tipo_us') for us in us_list if us.get('tipo_us')))
                    }
                    for fase, us_list in us_by_phase.items()
                },
                'rapporti_stratigrafici': stratigraphy_relations,
                'analisi_quote': quote_analysis,
                'interpretazione_fasi': {
                    fase: {
                        'descrizione': f"Fase {fase}",
                        'us_associate': [us.get('id_us') for us in us_list],
                        'interpretazione': next(
                            (us.get('interpretazione') for us in us_list if us.get('interpretazione')), None)
                    }
                    for fase, us_list in us_by_phase.items()
                }
            }

            return risultati

        except Exception as e:
            return f"Errore nell'analisi stratigrafica: {str(e)}"

    @staticmethod
    def AnalisiMaterialiComplessiva(context):
        """
        Gestisce l'analisi completa dei materiali archeologici.
        Analizza sia i materiali generici che la ceramica.
        """
        try:
            materials_data = context.get("materials_data", [])
            pottery_data = context.get("pottery_data", [])

            if not materials_data and not pottery_data:
                return "Errore: Nessun dato sui materiali disponibile"

            # Analisi materiali generici
            material_types = {}
            material_by_us = {}
            conservation_stats = {}

            for material in materials_data:
                # Analisi per tipo di materiale
                mat_type = material.get('tipo_materiale', 'Non specificato')
                if mat_type not in material_types:
                    material_types[mat_type] = {
                        'count': 0,
                        'items': []
                    }
                material_types[mat_type]['count'] += 1
                material_types[mat_type]['items'].append(material.get('id_materiale'))

                # Analisi per US
                us_id = material.get('id_us', 'Non specificato')
                if us_id not in material_by_us:
                    material_by_us[us_id] = []
                material_by_us[us_id].append({
                    'id_materiale': material.get('id_materiale'),
                    'tipo': mat_type,
                    'descrizione': material.get('descrizione')
                })

                # Statistiche conservazione
                conservation = material.get('stato_conservazione', 'Non specificato')
                if conservation not in conservation_stats:
                    conservation_stats[conservation] = 0
                conservation_stats[conservation] += 1

            # Analisi ceramica
            pottery_analysis = {
                'total_count': len(pottery_data),
                'by_type': {},
                'by_period': {},
                'by_preservation': {}
            }

            for pottery in pottery_data:
                # Analisi per tipo
                pot_type = pottery.get('tipo', 'Non specificato')
                if pot_type not in pottery_analysis['by_type']:
                    pottery_analysis['by_type'][pot_type] = 0
                pottery_analysis['by_type'][pot_type] += 1

                # Analisi per periodo
                period = pottery.get('periodo', 'Non specificato')
                if period not in pottery_analysis['by_period']:
                    pottery_analysis['by_period'][period] = 0
                pottery_analysis['by_period'][period] += 1

                # Analisi stato di conservazione
                preservation = pottery.get('conservazione', 'Non specificato')
                if preservation not in pottery_analysis['by_preservation']:
                    pottery_analysis['by_preservation'][preservation] = 0
                pottery_analysis['by_preservation'][preservation] += 1

            # Organizza i risultati
            risultati = {
                'statistiche_generali': {
                    'totale_materiali': len(materials_data),
                    'totale_ceramica': len(pottery_data),
                    'numero_us_con_materiali': len(material_by_us)
                },
                'analisi_materiali': {
                    'tipi_materiale': material_types,
                    'distribuzione_per_us': material_by_us,
                    'stato_conservazione': conservation_stats
                },
                'analisi_ceramica': pottery_analysis,
                'distribuzione_spaziale': {
                    us_id: {
                        'totale_materiali': len(materials),
                        'tipi_presenti': list(set(m['tipo'] for m in materials))
                    }
                    for us_id, materials in material_by_us.items()
                }
            }

            return risultati

        except Exception as e:
            return f"Errore nell'analisi dei materiali: {str(e)}"