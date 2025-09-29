#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CIDOC-CRM mapping for S3DGraphy Extended Matrix
Maps archaeological data to CIDOC-CRM ontology for semantic interoperability
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class CIDOCCRMMapper:
    """
    Maps PyArchInit/Extended Matrix data to CIDOC-CRM classes and properties
    CIDOC-CRM is the standard ontology for cultural heritage documentation
    """

    # CIDOC-CRM class mappings for archaeological entities
    CRM_CLASSES = {
        'stratigraphic_unit': 'E18_Physical_Thing',  # Physical stratigraphic deposit
        'masonry_unit': 'E22_Human-Made_Object',  # Built structure
        'feature_unit': 'E25_Human-Made_Feature',  # Cut, pit, posthole
        'deposit_unit': 'E18_Physical_Thing',  # Natural or cultural deposit
        'structural_unit': 'E22_Human-Made_Object',  # Architectural element
        'virtual_reconstruction': 'D7_Digital_Machine_Event',  # CRMdig for digital reconstruction
        'construction_unit': 'E12_Production',  # Construction activity
        'special_find': 'E19_Physical_Object',  # Archaeological find
        'site': 'E53_Place',  # Archaeological site
        'area': 'E53_Place',  # Excavation area
        'period': 'E4_Period',  # Historical period
        'phase': 'E4_Period'  # Archaeological phase
    }

    # CIDOC-CRM property mappings for relationships
    CRM_PROPERTIES = {
        'is_before': 'P120_occurs_before',  # Temporal sequence
        'has_same_time': 'P119_meets_in_time_with',  # Contemporary
        'covers': 'P132_spatiotemporally_overlaps_with',  # Physical overlap
        'cuts': 'P113_removed',  # Cutting relationship
        'fills': 'P53_has_former_or_current_location',  # Fill relationship
        'bonds': 'P46_is_composed_of',  # Structural bond
        'abuts': 'P122_borders_with',  # Physical adjacency
        'equals': 'P130_shows_features_of',  # Same entity
        'generic_connection': 'P69_has_association_with'  # General relationship
    }

    def __init__(self):
        self.namespace = "http://www.cidoc-crm.org/cidoc-crm/"
        self.crmdig_namespace = "http://www.ics.forth.gr/isl/CRMdig/"
        self.pyarchinit_namespace = "http://pyarchinit.org/ontology/"

    def map_node_to_cidoc(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a stratigraphic unit node to CIDOC-CRM

        Args:
            node_data: Node data from Extended Matrix

        Returns:
            CIDOC-CRM mapped entity
        """
        node_type = node_data.get('node_type', 'stratigraphic_unit')
        crm_class = self.CRM_CLASSES.get(node_type, 'E18_Physical_Thing')

        # Build CIDOC-CRM entity
        crm_entity = {
            '@context': {
                'crm': self.namespace,
                'crmdig': self.crmdig_namespace,
                'pyarchinit': self.pyarchinit_namespace
            },
            '@id': f"{self.pyarchinit_namespace}unit/{node_data.get('node_id', '')}",
            '@type': f"crm:{crm_class}",
            'crm:P1_is_identified_by': {
                '@type': 'crm:E42_Identifier',
                'crm:P2_has_type': 'Stratigraphic Unit Number',
                'crm:P190_has_symbolic_content': node_data.get('us', '')
            },
            'crm:P3_has_note': node_data.get('description', ''),
            'crm:P55_has_current_location': {
                '@type': 'crm:E53_Place',
                'crm:P87_is_identified_by': f"{node_data.get('sito', '')} - {node_data.get('area', '')}"
            }
        }

        # Add temporal information if available
        if node_data.get('periodo') or node_data.get('fase'):
            crm_entity['crm:P10_falls_within'] = {
                '@type': 'crm:E4_Period',
                'crm:P1_is_identified_by': node_data.get('periodo', ''),
                'crm:P9_consists_of': node_data.get('fase', '')
            }

        # Add dating if available
        if node_data.get('datazione'):
            crm_entity['crm:P4_has_time-span'] = {
                '@type': 'crm:E52_Time-Span',
                'crm:P82_at_some_time_within': node_data.get('datazione', '')
            }

        # Special handling for virtual reconstructions
        if node_type == 'virtual_reconstruction':
            crm_entity['@type'] = f"crmdig:{self.CRM_CLASSES[node_type]}"
            crm_entity['crmdig:L11_had_output'] = {
                '@type': 'crmdig:D9_Data_Object',
                'crm:P2_has_type': 'Virtual Reconstruction',
                'confidence_level': node_data.get('confidence_level', 'medium'),
                'based_on': node_data.get('based_on', [])
            }

        # Add type-specific properties
        if node_data.get('d_stratigrafica'):
            crm_entity['crm:P2_has_type'] = {
                '@value': node_data.get('d_stratigrafica'),
                '@language': 'it'
            }

        if node_data.get('d_interpretativa'):
            crm_entity['crm:P3_has_note'].append({
                '@type': 'Interpretative Definition',
                '@value': node_data.get('d_interpretativa'),
                '@language': 'it'
            })

        return crm_entity

    def map_edge_to_cidoc(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a relationship edge to CIDOC-CRM property

        Args:
            edge_data: Edge data from Extended Matrix

        Returns:
            CIDOC-CRM mapped property
        """
        edge_type = edge_data.get('edge_type', 'generic_connection')
        crm_property = self.CRM_PROPERTIES.get(edge_type, 'P69_has_association_with')

        crm_relationship = {
            '@id': f"{self.pyarchinit_namespace}relationship/{edge_data.get('edge_id', '')}",
            '@type': f"crm:{crm_property}",
            'crm:P14_carried_out_by': edge_data.get('edge_source', ''),
            'crm:P15_was_influenced_by': edge_data.get('edge_target', ''),
            'relationship_type': edge_type
        }

        # Add Allen temporal relations for stratigraphic relationships
        if edge_type in ['is_before', 'has_same_time']:
            crm_relationship['allen_relation'] = self._get_allen_relation(edge_type)

        return crm_relationship

    def _get_allen_relation(self, edge_type: str) -> str:
        """
        Map to Allen temporal relations for formal temporal reasoning
        """
        allen_mapping = {
            'is_before': 'before',
            'has_same_time': 'equals',
            'covers': 'overlaps',
            'cuts': 'during',
            'fills': 'meets',
            'contemporaneo a': 'equals'
        }
        return allen_mapping.get(edge_type, 'related')

    def export_to_cidoc_jsonld(self, graph_data: Dict[str, Any], filepath: str) -> bool:
        """
        Export Extended Matrix graph to CIDOC-CRM JSON-LD format

        Args:
            graph_data: Extended Matrix graph data
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            # Build JSON-LD document
            jsonld_doc = {
                '@context': {
                    'crm': self.namespace,
                    'crmdig': self.crmdig_namespace,
                    'pyarchinit': self.pyarchinit_namespace,
                    'xsd': 'http://www.w3.org/2001/XMLSchema#',
                    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
                },
                '@graph': []
            }

            # Add site/excavation as main activity
            site_entity = {
                '@id': f"{self.pyarchinit_namespace}excavation/{graph_data.get('graph_id', '')}",
                '@type': 'crm:E7_Activity',
                'crm:P2_has_type': 'Archaeological Excavation',
                'crm:P1_is_identified_by': graph_data.get('name', ''),
                'crm:P3_has_note': graph_data.get('description', ''),
                'crm:P9_consists_of': []  # Will contain units
            }

            # Map nodes
            for node in graph_data.get('nodes', []):
                crm_node = self.map_node_to_cidoc(node)
                jsonld_doc['@graph'].append(crm_node)
                site_entity['crm:P9_consists_of'].append({'@id': crm_node['@id']})

            # Map edges
            for edge in graph_data.get('edges', []):
                crm_edge = self.map_edge_to_cidoc(edge)
                jsonld_doc['@graph'].append(crm_edge)

            # Add site entity
            jsonld_doc['@graph'].insert(0, site_entity)

            # Add metadata
            jsonld_doc['@graph'].append({
                '@id': f"{self.pyarchinit_namespace}metadata",
                '@type': 'crm:E73_Information_Object',
                'crm:P102_has_title': 'PyArchInit Extended Matrix CIDOC-CRM Export',
                'crm:P94_has_created': datetime.now().isoformat(),
                'crm:P70_documents': {'@id': site_entity['@id']}
            })

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(jsonld_doc, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error exporting to CIDOC-CRM: {str(e)}")
            return False

    def export_to_rdf_turtle(self, graph_data: Dict[str, Any], filepath: str) -> bool:
        """
        Export to RDF Turtle format for triple stores

        Args:
            graph_data: Extended Matrix graph data
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            lines = []

            # Add prefixes
            lines.append(f"@prefix crm: <{self.namespace}> .")
            lines.append(f"@prefix crmdig: <{self.crmdig_namespace}> .")
            lines.append(f"@prefix pyarchinit: <{self.pyarchinit_namespace}> .")
            lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
            lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")

            # Add nodes as RDF triples
            for node in graph_data.get('nodes', []):
                node_id = node.get('node_id', '')
                node_uri = f"pyarchinit:unit/{node_id}"
                node_type = self.CRM_CLASSES.get(node.get('node_type', ''), 'E18_Physical_Thing')

                lines.append(f"{node_uri} a crm:{node_type} ;")
                lines.append(f'    rdfs:label "{node.get("name", "")}" ;')

                if node.get('description'):
                    lines.append(f'    crm:P3_has_note """{node.get("description", "")}""" ;')

                if node.get('us'):
                    lines.append(f'    crm:P1_is_identified_by "{node.get("us", "")}" ;')

                lines.append(f'    crm:P55_has_current_location pyarchinit:place/{node.get("sito", "")}_{node.get("area", "")} .')
                lines.append("")

            # Add edges as RDF triples
            for edge in graph_data.get('edges', []):
                source = f"pyarchinit:unit/{edge.get('edge_source', '')}"
                target = f"pyarchinit:unit/{edge.get('edge_target', '')}"
                prop = self.CRM_PROPERTIES.get(edge.get('edge_type', ''), 'P69_has_association_with')

                lines.append(f"{source} crm:{prop} {target} .")

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            return True

        except Exception as e:
            print(f"Error exporting to RDF Turtle: {str(e)}")
            return False