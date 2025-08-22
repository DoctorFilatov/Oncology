import streamlit as st
from datetime import datetime
import os

st.set_page_config(page_title="Онкологический план наблюдения", page_icon="🗓️")

# Проверяем наличие необходимых файлов
if not os.path.exists('observation_plan.json'):
    st.error("❌ Файл 'observation_plan.json' не найден! Убедитесь, что он загружен.")
    st.stop()

try:
    from calculator import OncologyFollowUpCalculator
except ImportError as e:
    st.error(f"❌ Ошибка импорта модуля: {e}")
    st.stop()

st.title('🗓️ План динамического наблюдения')
st.write('Расчет графика обследований после радикального лечения')

# Поля для ввода данных
col1, col2 = st.columns(2)
with col1:
    treatment_date = st.date_input('Дата радикального лечения', datetime(2024, 1, 15))
with col2:
    stage = st.selectbox('Стадия заболевания', ['I', 'II', 'III', 'IV'])

current_date = st.date_input('Текущая дата', datetime.now())

if st.button('Рассчитать план обследований', type="primary"):
    try:
        # Создаем экземпляр калькулятора
        calculator = OncologyFollowUpCalculator('observation_plan.json')
        
        # Преобразуем даты в нужный формат
        treat_str = treatment_date.strftime('%d.%m.%Y')
        curr_str = current_date.strftime('%d.%m.%Y')
        
        # Рассчитываем план
        plan = calculator.calculate_schedule(treat_str, stage, curr_str)
        
        # Выводим результаты
        if plan:
            st.success('✅ Найдены назначения:')
            for item in plan:
                with st.expander(f"Визит {item['visit_number']} - {item['scheduled_date']}"):
                    st.write(f"**Код услуги:** {item['code']}")
                    st.write(f"**Описание:** {item['description']}")
                    st.write(f"**Запланировано на:** {item['scheduled_date']}")
                    st.write(f"**Месяцев после лечения:** {item['months_after_treatment']}")
        else:
            st.info('ℹ️ На текущую дату назначений не найдено.')
            
    except Exception as e:
        st.error(f"❌ Произошла ошибка: {str(e)}")

# Добавляем информацию о приложении
st.sidebar.markdown("## О приложении")
st.sidebar.info("""
Это приложение автоматически рассчитывает план динамического наблюдения 
онкологических пациентов после радикального лечения на основе клинических рекомендаций.
""")
