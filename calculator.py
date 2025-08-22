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
    
    def adjust_to_workday(self, date):
        """Корректирует дату на ближайший рабочий день (понедельник-пятница)"""
        # Если суббота (5) - переносим на понедельник (+2 дня)
        if date.weekday() == 5:
            return date + timedelta(days=2)
        # Если воскресенье (6) - переносим на понедельник (+1 день)
        elif date.weekday() == 6:
            return date + timedelta(days=1)
        return date
    
    def calculate_schedule(self, treatment_date, stage, current_date=None):
        try:
            if current_date is None:
                current_date = datetime.now().strftime('%d.%m.%Y')
            
            treat_date = datetime.strptime(treatment_date, '%d.%m.%Y')
            curr_date = datetime.strptime(current_date, '%d.%m.%Y')
            
            results = []
            
            for visit in self.plan['observation_plan']['visits']:
                # Рассчитываем дату визита
                visit_date = treat_date + timedelta(days=30*visit['months_after_treatment'])
                
                # Корректируем на рабочий день если визит в будущем
                if visit_date > curr_date:
                    visit_date = self.adjust_to_workday(visit_date)
                
                # Добавляем визит в результаты, даже если он в будущем
                for exam in visit['examinations']:
                    if self._should_prescribe(exam, stage):
                        result_item = {
                            'visit_number': visit['visit_number'],
                            'months_after_treatment': visit['months_after_treatment'],
                            'code': exam['code'],
                            'description': exam['description'],
                            'scheduled_date': visit_date.strftime('%d.%m.%Y'),
                            'is_past': visit_date < curr_date,
                            'visit_type': visit.get('visit_type', 'Плановый осмотр')
                        }
                        
                        if 'condition' in exam:
                            result_item['condition'] = exam['condition']
                        
                        results.append(result_item)
            
            # Сортируем по времени назначения
            results.sort(key=lambda x: x['months_after_treatment'])
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
