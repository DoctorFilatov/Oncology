import streamlit as st
from datetime import datetime
import os
import base64
from calculator import OncologyFollowUpCalculator
from fpdf import FPDF
import tempfile

# Настройка страницы
st.set_page_config(page_title="Oncology Follow-Up Planner", page_icon="🗓️", layout="wide")

# Добавляем водяные знаки через CSS
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("data:image/svg+xml,%3Csvg width='200' height='200' xmlns='http://www.w3.org/2000/svg'%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='14' fill='rgba(128,128,128,0.1)' text-anchor='middle' dominant-baseline='middle' transform='rotate(-45, 100, 100)'%3EFilatov%3C/text%3E%3C/svg%3E");
        background-repeat: repeat;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Функция для создания PDF
def create_pdf(visits, treatment_date, stage, current_date):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    
    # Заголовок
    pdf.set_font_size(16)
    pdf.cell(0, 10, 'План динамического наблюдения', 0, 1, 'C')
    pdf.set_font_size(12)
    pdf.cell(0, 10, f'Дата лечения: {treatment_date}', 0, 1)
    pdf.cell(0, 10, f'Стадия: {stage}', 0, 1)
    pdf.cell(0, 10, f'Сформирован: {current_date}', 0, 1)
    pdf.ln(10)
    
    # Таблица с визитами
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(20, 10, 'Визит', 1, 0, 'C', True)
    pdf.cell(30, 10, 'Дата', 1, 0, 'C', True)
    pdf.cell(140, 10, 'Обследования (с кодами услуг)', 1, 1, 'C', True)
    
    pdf.set_fill_color(255, 255, 255)
    for visit in visits:
        # Формируем текст с кодами и описаниями обследований
        exam_text = ""
        for exam in visit['examinations']:
            exam_text += f"{exam['code']} - {exam['description']}\n"
        
        # Добавляем строку в таблицу
        status = "✅ " if visit['is_past'] else "🟢 "
        pdf.cell(20, 10, status + str(visit['visit_number']), 1, 0)
        pdf.cell(30, 10, visit['scheduled_date'], 1, 0)
        pdf.multi_cell(140, 10, exam_text, 1, 1)
    
    # Водяной знак в PDF
    pdf.set_font_size(40)
    pdf.set_text_color(220, 220, 220)
    pdf.rotate(45)
    pdf.text(60, 100, "Filatov")
    pdf.rotate(0)
    pdf.set_text_color(0, 0, 0)
    
    return pdf

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
                        # Выводим обследования с кодами
                        st.write("**Обследования:**")
                        for exam in visit['examinations']:
                            st.write(f"- {exam['code']} - {exam['description']}")
            
            # Показываем прошедшие визиты
            if past_visits:
                st.info(f'📋 Завершено {len(past_visits)} визитов:')
                
                for visit in past_visits:
                    with st.expander(f"✅ Визит {visit['visit_number']} - {visit['scheduled_date']} ({visit['months_after_treatment']} мес.) - {visit['visit_type']}", expanded=False):
                        # Выводим обследования с кодами
                        st.write("**Выполненные обследования:**")
                        for exam in visit['examinations']:
                            st.write(f"- {exam['code']} - {exam['description']}")
            
            # Сводная информация
            st.success(f"📊 Всего в плане: {len(visits)} визитов. Предстоящих: {len(future_visits)}, завершенных: {len(past_visits)}")
            
            # Кнопка для выгрузки в PDF
            if st.button('📄 Выгрузить в PDF'):
                try:
                    pdf = create_pdf(visits, treat_str, stage, curr_str)
                    
                    # Сохраняем временный файл
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        pdf.output(tmp_file.name)
                        
                        # Читаем файл и создаем кнопку для скачивания
                        with open(tmp_file.name, "rb") as f:
                            pdf_bytes = f.read()
                        
                        st.download_button(
                            label="⬇️ Скачать PDF",
                            data=pdf_bytes,
                            file_name=f"oncology_plan_{treatment_date.strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Удаляем временный файл
                    os.unlink(tmp_file.name)
                    
                except Exception as e:
                    st.error(f"Ошибка при создании PDF: {str(e)}")
            
        else:
            st.info('ℹ️ На текущую дату назначений не найдено.')
            
    except Exception as e:
        st.error(f"❌ Произошла ошибка: {str(e)}")

# Боковая панель с информацией
st.sidebar.markdown("## 📊 Охват наблюдения")
st.sidebar.info("""
Этот план охватывает первые 3 года динамического наблюдения:

- **КТ органов грудной клетки** выполняется каждые 3 месяца
- **УЗИ лимфоузлов** выполняется каждые 3 месяца
- **Расширенные обследования** (МРТ головного мозга, остеосцинтиграфия) 
  выполняются на 12, 24 и 36 месяцах для стадий III и IV

Даты визитов автоматически корректируются на рабочие дни.
""")

# Информация о водяных знаках
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="opacity: 0.7; font-size: 0.8em;">
<p>Приложение разработано с использованием технологии Filatov</p>
</div>
""", unsafe_allow_html=True)
