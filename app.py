import streamlit as st
from datetime import datetime

# Заголовок
st.title('🗓️ План динамического наблюдения')
st.write('Расчет графика обследований после радикального лечения')

# Поля для ввода данных
treatment_date = st.date_input('Дата радикального лечения', datetime(2024, 1, 15))
stage = st.selectbox('Стадия заболевания', ['I', 'II', 'III', 'IV'])
current_date = st.date_input('Текущая дата', datetime.now())

# Кнопка расчета
if st.button('Рассчитать план обследований'):
    # Преобразуем даты в нужный формат
    treat_str = treatment_date.strftime('%d.%m.%Y')
    curr_str = current_date.strftime('%d.%m.%Y')
    
    # Используем наш класс-калькулятор
    calculator = OncologyFollowUpCalculator('observation_plan.json')
    plan = calculator.calculate_schedule(treat_str, stage, curr_str)
    
    # Выводим результаты
    if plan:
        st.success('Найдены назначения:')
        for item in plan:
            st.write(f"**{item['scheduled_date']}** (Визит {item['visit_number']})")
            st.write(f"{item['code']} - {item['description']}")
            st.write('---')
    else:
        st.info('На текущую дату назначений не найдено.')