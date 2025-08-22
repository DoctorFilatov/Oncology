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

if st.button('Рассчитать полный план наблюдения', type="primary"):
    try:
        calculator = OncologyFollowUpCalculator('observation_plan.json')
        treat_str = treatment_date.strftime('%d.%m.%Y')
        curr_str = current_date.strftime('%d.%m.%Y')
        plan = calculator.calculate_schedule(treat_str, stage, curr_str)
        
        if plan:
            # Группируем по годам
            years = {}
            for item in plan:
                year = (item['months_after_treatment'] // 12) + 1
                if year not in years:
                    years[year] = []
                years[year].append(item)
            
            # Выводим результаты с группировкой по годам
            for year, visits in years.items():
                st.markdown(f"### {year}-й год наблюдения")
                
                for visit in visits:
                    with st.expander(f"Визит {visit['visit_number']} - {visit['scheduled_date']} ({visit['months_after_treatment']} мес.)"):
                        st.write(f"**Тип визита:** {visit.get('visit_type', 'Плановый осмотр')}")
                        st.write(f"**Код услуги:** {visit['code']}")
                        st.write(f"**Обследование:** {visit['description']}")
                        if visit.get('condition'):
                            st.write(f"**Условие:** для стадий {visit['condition']['value']}")
            
            # Сводная статистика
            st.success(f"✅ Найдено {len(plan)} назначений на период 3 года")
            
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

Расширенные обследования назначаются по показаниям в зависимости от стадии заболевания.
""")

# Отображение сырых данных для отладки
with st.sidebar.expander("📁 Просмотр данных плана"):
    try:
        import json
        with open('observation_plan.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        st.json(data)
    except:
        st.error("Ошибка загрузки файла данных")
