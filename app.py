import streamlit as st
from datetime import datetime
import os
from calculator import OncologyFollowUpCalculator

st.set_page_config(page_title="Онкологический план наблюдения", page_icon="🗓️", layout="wide")

# Проверяем наличие необходимых файлов
if not os.path.exists('observation_plan.json'):
    st.error("❌ Файл 'observation_plan.json' не найден! Убедитесь, что он загружен.")
    st.stop()

st.title('🗓️ План динамического наблюдения')
st.markdown("### Расчет графика обследований после радикального лечения (первые 3 года)")

# Поля для ввода данных
col1, col2, col3 = st.columns(3)
with col1:
    treatment_date = st.date_input('Дата радикального лечения', datetime(2024, 1, 15))
with col2:
    stage = st.selectbox('Стадия заболевания', ['I', 'II', 'III', 'IV'])
with col3:
    current_date = st.date_input('Текущая дата', datetime.now())

if st.button('Сформировать план наблюдения', type="primary"):
    try:
        calculator = OncologyFollowUpCalculator('observation_plan.json')
        treat_str = treatment_date.strftime('%d.%m.%Y')
        curr_str = current_date.strftime('%d.%m.%Y')
        plan = calculator.calculate_schedule(treat_str, stage, curr_str)
        
        if plan:
            # Разделяем на прошедшие и будущие визиты
            past_visits = [v for v in plan if v['is_past']]
            future_visits = [v for v in plan if not v['is_past']]
            
            # Показываем будущие визиты
            if future_visits:
                st.success(f'✅ Запланировано {len(future_visits)} визитов:')
                
                # Группируем по годам
                future_by_years = {}
                for visit in future_visits:
                    year = (visit['months_after_treatment'] // 12) + 1
                    if year not in future_by_years:
                        future_by_years[year] = []
                    future_by_years[year].append(visit)
                
                # Выводим будущие визиты по годам
                for year, visits in future_by_years.items():
                    st.markdown(f"### {year}-й год наблюдения (будущие визиты)")
                    
                    for visit in visits:
                        with st.expander(f"🗓️ Визит {visit['visit_number']} - {visit['scheduled_date']} ({visit['months_after_treatment']} мес.)"):
                            st.write(f"**Тип визита:** {visit['visit_type']}")
                            st.write(f"**Код услуги:** {visit['code']}")
                            st.write(f"**Обследование:** {visit['description']}")
                            if visit.get('condition'):
                                st.write(f"**Условие:** для стадий {visit['condition']['value']}")
            
            # Показываем прошедшие визиты (свернуто по умолчанию)
            if past_visits:
                with st.expander(f"📋 Показать прошедшие визиты ({len(past_visits)})"):
                    st.info(f'Завершено {len(past_visits)} визитов:')
                    for visit in past_visits:
                        st.write(f"~~{visit['scheduled_date']} - {visit['description']}~~")
            
            # Сводная информация
            st.success(f"📊 Всего в плане: {len(plan)} визитов. Предстоящих: {len(future_visits)}")
            
        else:
            st.info('ℹ️ На текущую дату назначений не найдено.')
            
    except Exception as e:
        st.error(f"❌ Произошла ошибка: {str(e)}")

# Боковая панель с информацией
st.sidebar.markdown("## 📊 Охват наблюдения")
st.sidebar.info("""
Этот план охватывает первые 3 года динамического наблюдения:

- **1-й год:** ежеквартальные осмотры
- **2-й год:** осмотры каждые 6 месяцев  
- **3-й год:** ежегодный контроль

Даты визитов автоматически корректируются на рабочие дни.
""")

# Отладочная информация
with st.sidebar.expander("ℹ️ О приложении"):
    st.write("""
    Это приложение автоматически рассчитывает план динамического наблюдения 
    онкологических пациентов после радикального лечения на основе клинических рекомендаций.
    
    Особенности:
    - Показывает только будущие визиты
    - Автоматически корректирует даты на рабочие дни
    - Учитывает стадию заболевания при назначениях
    """)
