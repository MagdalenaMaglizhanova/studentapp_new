import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Инициализация
if "firms" not in st.session_state:
    st.session_state.firms = []
if "students" not in st.session_state:
    st.session_state.students = []
if "imported_students" not in st.session_state:
    st.session_state.imported_students = []
if "classified" not in st.session_state:
    st.session_state.classified = []

st.title("Ученик-Фирма Приложение")

# --- Импортиране на фирми от Excel ---
st.header("Импортиране на фирми от Excel")
firms_file = st.file_uploader("Качи Excel файл с фирми (2 колони: 'Име', 'Квота')", type=["xlsx"], key="firms_upload")

if firms_file:
    try:
        df_firms = pd.read_excel(firms_file)
        if "Име" in df_firms.columns and "Квота" in df_firms.columns:
            imported_firms = []
            for _, row in df_firms.iterrows():
                name = str(row["Име"]).strip()
                quota = int(row["Квота"])
                if name and quota > 0:
                    imported_firms.append({"name": name, "quota": quota})
            existing_names = {firm['name'] for firm in st.session_state.firms}
            new_unique_firms = [firm for firm in imported_firms if firm['name'] not in existing_names]
            st.session_state.firms.extend(new_unique_firms)
            st.success(f"Импортирани успешно {len(new_unique_firms)} нови фирми.")
        else:
            st.error("Файлът трябва да съдържа колони 'Име' и 'Квота'.")
    except Exception as e:
        st.error(f"Грешка при импортиране: {e}")

# --- Добавяне на фирма ръчно ---
st.header("Добави фирма ръчно")
firm_name = st.text_input("Име на фирмата", key="firm_name_input")
firm_quota = st.number_input("Квота", min_value=1, step=1, key="firm_quota_input")

col1, col2 = st.columns(2)
with col1:
    if st.button("Добави фирма"):
        if firm_name.strip() and firm_quota > 0:
            if not any(f['name'] == firm_name.strip() for f in st.session_state.firms):
                st.session_state.firms.append({"name": firm_name.strip(), "quota": firm_quota})
                st.success(f"Фирма '{firm_name.strip()}' добавена успешно!")
            else:
                st.warning("Тази фирма вече е добавена.")
        else:
            st.error("Моля, въведете име на фирма и валидна квота.")

with col2:
    if st.button("🗑 Изчисти всички фирми"):
        st.session_state.firms = []
        st.success("Всички фирми са изтрити.")

# --- Покажи уникални фирми ---
if st.session_state.firms:
    st.subheader("Добавени фирми")
    unique_firms = {}
    for firm in st.session_state.firms:
        unique_firms[firm["name"]] = firm["quota"]
    for name, quota in unique_firms.items():
        st.write(f"{name} - Квота: {quota}")

st.markdown("---")

# --- Импортиране на ученици ---
st.header("Импортиране на ученици от Excel")
uploaded_file = st.file_uploader("Качи Excel файл (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Колони в Excel файла:", list(df.columns))

        required_columns = ["Име", "Точки"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Excel файлът трябва да съдържа поне колоните: {', '.join(required_columns)}.")
        else:
            temp_students = []
            for _, row in df.iterrows():
                name = row["Име"]
                points = row["Точки"]
                choices = [row[col] for col in df.columns if col.startswith("Желание") and pd.notna(row[col])]
                if name and pd.notna(points) and choices:
                    temp_students.append({
                        "name": name,
                        "points": points,
                        "choices": choices
                    })
            st.session_state.imported_students = temp_students
            st.success(f"Файлът е прочетен успешно! Намерени ученици: {len(temp_students)}")

            if st.button("Добави импортираните ученици към списъка"):
                before = len(st.session_state.students)
                st.session_state.students.extend(st.session_state.imported_students)
                st.session_state.imported_students = []
                st.success(f"Добавени {len(st.session_state.students) - before} ученици.")
    except Exception as e:
        st.error(f"Грешка при обработка на файла: {e}")

st.markdown("---")

# --- Ръчно добавяне на ученик ---
st.header("Добави ученик")
student_name = st.text_input("Име на ученика", key="student_name_input")
student_points = st.number_input("Точки", min_value=0, step=1, key="student_points_input")

if st.session_state.firms:
    student_choices = []

    # Броят желания = броят фирми
    number_of_choices = len(st.session_state.firms)

    for i in range(number_of_choices):
        choice = st.selectbox(
            f"Избери фирма - предпочитание {i+1}",
            options=[firm["name"] for firm in st.session_state.firms],
            key=f"choice_{i}"
        )

        student_choices.append(choice)

else:
    st.info("Моля, добавете поне една фирма, за да можете да избирате фирми за учениците.")

col3, col4 = st.columns(2)
with col3:
    if st.button("Добави ученик"):
        if student_name.strip() and student_points >= 0 and student_choices:
            st.session_state.students.append({
                "name": student_name.strip(),
                "points": student_points,
                "choices": student_choices
            })
            st.success(f"Ученикът '{student_name.strip()}' добавен успешно!")
        else:
            st.error("Моля, въведете име, точки и изберете фирми за всички желания.")

with col4:
    if st.button("🗑 Изчисти всички ученици"):
        st.session_state.students = []
        st.success("Всички ученици са изтрити.")

# --- Списък на учениците ---
if st.session_state.students:
    st.subheader("Добавени ученици")
    for student in st.session_state.students:
        st.write(f"{student['name']} - Точки: {student['points']}")
        st.write(f"Желания: {', '.join(student['choices'])}")

st.markdown("---")

# --- Класиране ---
if st.button("Класирай учениците"):
    if not st.session_state.firms:
        st.error("Няма добавени фирми за класиране.")
    elif not st.session_state.students:
        st.error("Няма добавени ученици за класиране.")
    else:
        students_sorted = sorted(st.session_state.students, key=lambda x: x["points"], reverse=True)
        firm_slots = {firm["name"]: firm["quota"] for firm in st.session_state.firms}
        classified = []

        for student in students_sorted:
            placed = False
            for choice in student["choices"]:
                if firm_slots.get(choice, 0) > 0:
                    classified.append({"Име": student["name"], "Фирма": choice, "Точки": student["points"]})
                    firm_slots[choice] -= 1
                    placed = True
                    break
            if not placed:
                classified.append({"Име": student["name"], "Фирма": "Не е класиран", "Точки": student["points"]})

        st.session_state.classified = classified

        st.subheader("Резултати от класирането")
        for c in classified:
            st.write(f"{c['Име']} - Класиран във фирма: {c['Фирма']}")

        # --- Диаграми ---
        st.subheader("📊 Визуализации")

        firm_distribution = {}
        for c in classified:
            firm_distribution[c["Фирма"]] = firm_distribution.get(c["Фирма"], 0) + 1

        labels = list(firm_distribution.keys())
        sizes = list(firm_distribution.values())

        st.markdown("**Кръгова диаграма: Разпределение по фирми**")
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax1.axis("equal")
        st.pyplot(fig1)

        st.markdown("**Стълбовидна диаграма: Брой ученици по фирма**")
        fig2, ax2 = plt.subplots()
        ax2.bar(labels, sizes, color="skyblue")
        ax2.set_ylabel("Брой ученици")
        ax2.set_xlabel("Фирма")
        ax2.set_title("Разпределение по фирми")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        st.markdown("**Линейна диаграма: Точки на учениците**")
        fig3, ax3 = plt.subplots()
        ax3.plot([c["Име"] for c in classified], [c["Точки"] for c in classified], marker="o")
        ax3.set_ylabel("Точки")
        ax3.set_xlabel("Ученик")
        ax3.set_title("Точки по ред на класиране")
        plt.xticks(rotation=45)
        st.pyplot(fig3)

st.markdown("---")

# --- Генериране на отчет ---
st.header("Генериране на отчет")

specialty = st.text_input("Специалност")
school_class = st.text_input("Клас")
teacher = st.text_input("Класен ръководител")

if st.button("Генерирай отчет"):
    if not st.session_state.classified:
        st.warning("Няма налични резултати за отчет.")
    else:
        df_report = pd.DataFrame(st.session_state.classified)
        df_report.insert(0, "Клас", school_class)
        df_report.insert(0, "Специалност", specialty)
        df_report.insert(0, "Класен ръководител", teacher)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_report.to_excel(writer, index=False, sheet_name="Отчет")
        output.seek(0)

        st.success("Отчетът е генериран успешно!")
        st.download_button(
            label="📥 Изтегли Excel отчет",
            data=output,
            file_name="otchet_uchenici.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
