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
        visits = calculator.calculate_schedule(treat_str, stage, curr_str)
        
        if visits:
            # Разделяем на прошедшие и будущие визиты
            past_visits = [v for v in visits if v['is_past']]
            future_visits = [v for v in visits if not v['is_past']]
            
            # Показываем будущие визиты
            if future_visits:
                st.success(f'✅ Запланировано {len(future_visits)} визитов:')
                
                for visit in future_visits:
                    with st.expander(f"🗓️ Визит {visit['visit_number']} - {visit['scheduled_date']} ({visit['months_after_treatment']} мес.) - {visit['visit_type']}", expanded=True):
                        # Формируем компактный список обследований
                        exam_list = []
                        for exam in visit['examinations']:
                            # Сокращаем длинные описания
                            short_desc = exam['description']
                            if "Диспансерный прием" in short_desc:
                                short_desc = "Осмотр онколога"
                            elif "Компьютерная томография" in short_desc:
                                short_desc = "КТ грудной клетки"
                            elif "УЗИ регионарных лимфоузлов" in short_desc:
                                short_desc = "УЗИ лимфоузлов"
                            
                            exam_list.append(short_desc)
                        
                        # Выводим обследования в компактном формате
                        st.write("**Обследования:**")
                        for exam in exam_list:
                            st.write(f"- {exam}")
            
            # Показываем прошедшие визиты
            if past_visits:
                st.info(f'📋 Завершено {len(past_visits)} визитов:')
                
                for visit in past_visits:
                    with st.expander(f"✅ Визит {visit['visit_number']} - {visit['scheduled_date']} ({visit['months_after_treatment']} мес.) - {visit['visit_type']}", expanded=False):
                        # Формируем компактный список обследований
                        exam_list = []
                        for exam in visit['examinations']:
                            # Сокращаем длинные описания
                            short_desc = exam['description']
                            if "Диспансерный прием" in short_desc:
                                short_desc = "Осмотр онколога"
                            elif "Компьютерная томография" in short_desc:
                                short_desc = "КТ грудной клетки"
                            elif "УЗИ регионарных лимфоузлов" in short_desc:
                                short_desc = "УЗИ лимфоузлов"
                            
                            exam_list.append(short_desc)
                        
                        # Выводим обследования в компактном формате
                        st.write("**Выполненные обследования:**")
                        for exam in exam_list:
                            st.write(f"- {exam}")
            
            # Сводная информация
            st.success(f"📊 Всего в плане: {len(visits)} визитов. Предстоящих: {len(future_visits)}, завершенных: {len(past_visits)}")
            
            # Визуальная временная шкала
            st.markdown("### 📅 Временная шкала наблюдения")
            timeline_cols = st.columns(min(6, len(visits)))
            
            for i, visit in enumerate(visits):
                if i < 6:  # Ограничиваем количество колонок для визуализации
                    with timeline_cols[i]:
                        status = "✅" if visit['is_past'] else "🟢"
                        st.markdown(f"{status} **Визит {visit['visit_number']}**")
                        st.caption(visit['scheduled_date'])
            
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
with st.sidebar.expander("ℹ️ Сокращения обследований"):
    st.write("""
    - **Осмотр онколога:** Диспансерный прием врача-онколога
    - **КТ грудной клетки:** Компьютерная томография органов грудной клетки
    - **УЗИ лимфоузлов:** УЗИ регионарных лимфоузлов
    - **МРТ мозга:** МРТ головного мозга
    - **Онкомаркеры:** Анализ крови на онкомаркеры
    """)
