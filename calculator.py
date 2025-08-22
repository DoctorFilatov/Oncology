from datetime import datetime, timedelta
import json

class OncologyFollowUpCalculator:
    def __init__(self, plan_json_path):
        with open(plan_json_path, 'r', encoding='utf-8') as f:
            self.plan = json.load(f)
    
    def calculate_schedule(self, treatment_date, stage, current_date=None):
        """
        Рассчитывает актуальный план обследований на текущую дату.
        
        Args:
            treatment_date (str): Дата лечения в формате 'dd.mm.yyyy'
            stage (str): Стадия заболевания (например, 'II')
            current_date (str, optional): Текущая дата. Если None, используется сегодня.
        
        Returns:
            list: Список обследований, которые необходимо выполнить.
        """
        if current_date is None:
            current_date = datetime.now().strftime('%d.%m.%Y')
        
        # Преобразуем даты в объекты
        treat_date = datetime.strptime(treatment_date, '%d.%m.%Y')
        curr_date = datetime.strptime(current_date, '%d.%m.%Y')
        
        # Вычисляем разницу в месяцах
        delta_months = (curr_date.year - treat_date.year) * 12 + (curr_date.month - treat_date.month)
        
        results = []
        
        for visit in self.plan['observation_plan']['visits']:
            # Проверяем, настало ли время для этого визита
            if delta_months >= visit['months_after_treatment']:
                for exam in visit['examinations']:
                    # Проверяем условия для назначения обследования
                    if self._should_prescribe(exam, stage):
                        results.append({
                            'visit_number': visit['visit_number'],
                            'months_after_treatment': visit['months_after_treatment'],
                            'code': exam['code'],
                            'description': exam['description'],
                            'scheduled_date': (treat_date + timedelta(days=30*visit['months_after_treatment'])).strftime('%d.%m.%Y')
                        })
        
        return results
    
    def _should_prescribe(self, exam, stage):
        """Внутренняя функция для проверки условий назначения."""
        if exam['is_mandatory']:
            return True
        
        if 'condition' in exam:
            if exam['condition']['type'] == 'stage_in':
                return stage in exam['condition']['value']
        
        return False

# Пример использования
if __name__ == "__main__":
    calculator = OncologyFollowUpCalculator('observation_plan.json')
    
    plan = calculator.calculate_schedule(
        treatment_date='01.09.2023',
        stage='III',
        current_date='01.03.2025'
    )
    
    for item in plan:
        print(f"Визит {item['visit_number']} ({item['scheduled_date']}): {item['code']} - {item['description']}")