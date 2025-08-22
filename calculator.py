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
            
            visits = []
            
            for visit_plan in self.plan['observation_plan']['visits']:
                # Рассчитываем дату визита
                visit_date = treat_date + timedelta(days=30*visit_plan['months_after_treatment'])
                
                # Корректируем на рабочий день если визит в будущем
                if visit_date > curr_date:
                    visit_date = self.adjust_to_workday(visit_date)
                
                # Определяем статус визита (прошедший/будущий)
                is_past = visit_date < curr_date
                
                # Формируем список обследований для этого визита
                examinations = []
                for exam in visit_plan['examinations']:
                    if self._should_prescribe(exam, stage):
                        examinations.append({
                            'code': exam['code'],
                            'description': exam['description']
                        })
                
                # Добавляем визит в результаты
                visits.append({
                    'visit_number': visit_plan['visit_number'],
                    'months_after_treatment': visit_plan['months_after_treatment'],
                    'scheduled_date': visit_date.strftime('%d.%m.%Y'),
                    'is_past': is_past,
                    'visit_type': visit_plan.get('visit_type', 'Плановый осмотр'),
                    'examinations': examinations
                })
            
            # Сортируем по времени назначения
            visits.sort(key=lambda x: x['months_after_treatment'])
            return visits
        except Exception as e:
            raise Exception(f"Ошибка расчета графика: {str(e)}")
    
    def _should_prescribe(self, exam, stage):
        if exam['is_mandatory']:
            return True
        
        if 'condition' in exam:
            if exam['condition']['type'] == 'stage_in':
                return stage in exam['condition']['value']
        
        return False
