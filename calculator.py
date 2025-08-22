from datetime import datetime, timedelta
import json

class OncologyFollowUpCalculator:
    def __init__(self, plan_json_path):
        try:
            with open(plan_json_path, 'r', encoding='utf-8') as f:
                self.plan = json.load(f)
        except FileNotFoundError:
            raise Exception(f"Файл {plan_json_path} не найден")
        except json.JSONDecodeError:
            raise Exception("Ошибка в формате JSON файла")
    
    def calculate_schedule(self, treatment_date, stage, current_date=None):
        try:
            if current_date is None:
                current_date = datetime.now().strftime('%d.%m.%Y')
            
            treat_date = datetime.strptime(treatment_date, '%d.%m.%Y')
            curr_date = datetime.strptime(current_date, '%d.%m.%Y')
            
            delta_months = (curr_date.year - treat_date.year) * 12 + (curr_date.month - treat_date.month)
            
            results = []
            
            for visit in self.plan['observation_plan']['visits']:
                if delta_months >= visit['months_after_treatment']:
                    for exam in visit['examinations']:
                        if self._should_prescribe(exam, stage):
                            results.append({
                                'visit_number': visit['visit_number'],
                                'months_after_treatment': visit['months_after_treatment'],
                                'code': exam['code'],
                                'description': exam['description'],
                                'scheduled_date': (treat_date + timedelta(days=30*visit['months_after_treatment'])).strftime('%d.%m.%Y')
                            })
            
            return results
        except Exception as e:
            raise Exception(f"Ошибка расчета графика: {str(e)}")
    
    def _should_prescribe(self, exam, stage):
        if exam['is_mandatory']:
            return True
        
        if 'condition' in exam:
            if exam['condition']['type'] == 'stage_in':
                return stage in exam['condition']['value']
        
        return False
