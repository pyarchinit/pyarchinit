
class ArchaeologicalValidators:
    @staticmethod
    def validate_site_info(context):
        """Valida le informazioni del sito"""
        # Verifica che context non sia None
        if not context:
            return {
                'success': False,
                'missing_fields': ['entire context'],
                'warnings': ['Context is missing'],
                'message': 'No context data provided'
            }

        validation_results = {
            'success': True,
            'missing_fields': [],
            'warnings': []
        }

        site_data = context.get("site_data", {})
        if not site_data:
            validation_results['success'] = False
            validation_results['warnings'].append("Site data is missing")
            return validation_results

        required_fields = ['nome_sito', 'comune', 'provincia']
        missing = [field for field in required_fields if not site_data.get(field)]
        if missing:
            validation_results['success'] = False
            validation_results['missing_fields'].extend(missing)
            validation_results['message'] = f"Missing required fields: {', '.join(missing)}"

        return validation_results

    @staticmethod
    def validate_us(context):
        """Validate US descriptions and provide detailed feedback"""
        if not context:
            return {
                'valid': False,
                'missing_fields': ['entire context'],
                'incomplete': [],
                'message': 'No context data provided'
            }

        us_data = context.get("us_data", [])
        if not us_data:
            return {
                'valid': False,
                'missing_fields': ['us_data'],
                'incomplete': [],
                'message': 'No US data available'
            }

        missing_us = []
        incomplete_us = []

        for us in us_data:
            if not us:  # Skip if us is None
                continue

            us_num = us.get('us', 'Unknown')
            area = us.get('area', 'Unknown')
            missing_fields = []

            if not us.get('descrizione'):
                missing_fields.append('descrizione')
            elif len(str(us.get('descrizione', '')).strip()) < 10:
                incomplete_us.append({
                    'us': us_num,
                    'area': area,
                    'field': 'descrizione',
                    'content': us.get('descrizione')
                })

            if not us.get('interpretazione'):
                missing_fields.append('interpretazione')
            elif len(str(us.get('interpretazione', '')).strip()) < 10:
                incomplete_us.append({
                    'us': us_num,
                    'area': area,
                    'field': 'interpretazione',
                    'content': us.get('interpretazione')
                })

            if missing_fields:
                missing_us.append({
                    'us': us_num,
                    'area': area,
                    'missing': missing_fields
                })

        message = ""
        if missing_us:
            message += "US con campi mancanti:\n"
            for us in missing_us:
                message += f"US {us['us']} (Area {us['area']}): mancano {', '.join(us['missing'])}.\n"

        if incomplete_us:
            if message:
                message += "\n"
            message += "US con descrizioni potenzialmente incomplete:\n"
            for us in incomplete_us:
                message += f"US {us['us']} (Area {us['area']}): {us['field']} sembra incompleta.\n"

        return {
            'valid': not (missing_us or incomplete_us),
            'missing_fields': [us['missing'] for us in missing_us],
            'incomplete': [f"US {us['us']}" for us in incomplete_us],
            'message': message if (missing_us or incomplete_us) else "All US properly documented"
        }

    @staticmethod
    def validate_materials(context):
        """Validate materials descriptions with enhanced feedback"""
        # Verifica che context e materials_data non siano None
        if not context:
            return {
                'valid': False,
                'missing': ['entire context'],
                'incomplete': [],
                'message': 'No context data provided'
            }

        materials_data = context.get("materials_data", [])
        if not materials_data:
            return {
                'valid': False,
                'missing': ['materials data'],
                'incomplete': [],
                'message': 'No materials data available'
            }

        missing_materials = []
        incomplete_materials = []

        for material in materials_data:
            if not material:  # Skip if material is None
                continue

            inv_num = material.get('numero_inventario', 'Unknown')
            missing_fields = []
            incomplete_fields = []

            fields_to_check = {
                'descrizione': 10,
                'tipo_reperto': 3,
                'definizione': 5,
                'stato_conservazione': 5
            }

            for field, min_length in fields_to_check.items():
                value = material.get(field, '')
                if not value:
                    missing_fields.append(field)
                elif len(str(value).strip()) < min_length:
                    incomplete_fields.append(field)

            if missing_fields:
                missing_materials.append({
                    'id': inv_num,
                    'us': material.get('us', 'Unknown'),
                    'area': material.get('area', 'Unknown'),
                    'missing': missing_fields
                })

            if incomplete_fields:
                incomplete_materials.append({
                    'id': inv_num,
                    'us': material.get('us', 'Unknown'),
                    'area': material.get('area', 'Unknown'),
                    'incomplete': incomplete_fields
                })

        message = ""
        if missing_materials:
            message += "Materiali con campi mancanti:\n"
            for material in missing_materials:
                message += f"Inv. {material['id']} (Area {material['area']}, US {material['us']}): mancano {', '.join(material['missing'])}.\n"

        if incomplete_materials:
            if message:
                message += "\n"
            message += "Materiali con descrizioni potenzialmente incomplete:\n"
            for material in incomplete_materials:
                message += f"Inv. {material['id']} (Area {material['area']}, US {material['us']}): campi incompleti: {', '.join(material['incomplete'])}.\n"

        return {
            'valid': not (missing_materials or incomplete_materials),
            'missing': [mat['id'] for mat in missing_materials],
            'incomplete': [mat['id'] for mat in incomplete_materials],
            'message': message if (missing_materials or incomplete_materials) else "All materials properly documented"
        }

    @staticmethod
    def validate_pottery(context):
        """Validate pottery descriptions with enhanced feedback"""
        # Verifica che context e pottery_data non siano None
        if not context:
            return {
                'valid': False,
                'missing': ['entire context'],
                'incomplete': [],
                'message': 'No context data provided'
            }

        pottery_data = context.get("pottery_data", [])
        if not pottery_data:
            return {
                'valid': False,
                'missing': ['pottery data'],
                'incomplete': [],
                'message': 'No pottery data available'
            }

        missing_pottery = []
        incomplete_pottery = []

        for pottery in pottery_data:
            if not pottery:  # Skip if pottery is None
                continue

            pottery_id = pottery.get('id_number', 'Unknown')
            missing_fields = []
            incomplete_fields = []

            if not pottery.get('fabric'):
                missing_fields.append('fabric')
            elif len(str(pottery.get('fabric', '')).strip()) < 5:
                incomplete_fields.append('fabric')

            if not pottery.get('form'):
                missing_fields.append('form')
            elif len(str(pottery.get('form', '')).strip()) < 5:
                incomplete_fields.append('form')

            if missing_fields:
                missing_pottery.append({
                    'id': pottery_id,
                    'us': pottery.get('us', 'Unknown'),
                    'missing': missing_fields
                })

            if incomplete_fields:
                incomplete_pottery.append({
                    'id': pottery_id,
                    'us': pottery.get('us', 'Unknown'),
                    'incomplete': incomplete_fields
                })

        message = ""
        if missing_pottery:
            message += "Reperti ceramici con campi mancanti:\n"
            for pottery in missing_pottery:
                message += f"ID {pottery['id']} (US {pottery['us']}): mancano {', '.join(pottery['missing'])}.\n"

        if incomplete_pottery:
            if message:
                message += "\n"
            message += "Reperti ceramici con descrizioni potenzialmente incomplete:\n"
            for pottery in incomplete_pottery:
                message += f"ID {pottery['id']} (US {pottery['us']}): campi incompleti: {', '.join(pottery['incomplete'])}.\n"

        return {
            'valid': not (missing_pottery or incomplete_pottery),
            'missing': [pottery['id'] for pottery in missing_pottery],
            'incomplete': [pottery['id'] for pottery in incomplete_pottery],
            'message': message if (missing_pottery or incomplete_pottery) else "All pottery properly documented"
        }