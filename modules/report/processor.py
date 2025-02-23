from modules.report.action import ArchaeologicalActions
from modules.report.validation_tools import ArchaeologicalValidators


class ArchaeologicalStepProcessor:
    def __init__(self):
        self.actions = ArchaeologicalActions()
        self.validators = ArchaeologicalValidators()

    def process_step(self, step, context):
        """Processa uno step dell'analisi"""
        results = {
            'validation_results': [],
            'action_result': None
        }

        # Esegui validazioni
        validation_tools = step.get('validation_tool', [])
        if validation_tools:
            if isinstance(validation_tools, str):
                validation_tools = [validation_tools]

            for tool in validation_tools:
                if hasattr(self.validators, tool):
                    validation_func = getattr(self.validators, tool)
                    validation_result = validation_func(context)
                    results['validation_results'].append({
                        'tool': tool,
                        'result': validation_result
                    })

        # Esegui action
        action = step.get('action')
        if action and hasattr(self.actions, action):
            action_func = getattr(self.actions, action)
            results['action_result'] = action_func(context)

        return results