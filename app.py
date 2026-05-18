import streamlit as st
import random
import time
import pandas as pd
from datetime import date
import os
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ===================================================
# TITRE + MODE
# ===================================================

st.title("Prototype IA Neurovisuelle - Saccades")

mode = st.radio(
    "Choisir le mode",
    ["Jeu patient", "Dashboard orthoptiste"]
)

# ===================================================
# DASHBOARD ORTHOPTISTE
# ===================================================

if mode == "Dashboard orthoptiste":

    st.header("Analyse des patients")

    file_path = "data/results.csv"

    if os.path.exists(file_path):

        df = pd.read_csv(file_path)
        df = df.reset_index(drop=True)
        df["session"] = df.index + 1

        st.subheader("Données")
        st.dataframe(df)

        # -------------------------
        # SCORE
        # -------------------------

        st.subheader("Score")

        fig, ax = plt.subplots()
        ax.plot(df["session"], df["score"], marker="o")
        st.pyplot(fig)

        # -------------------------
        # TEMPS REACTION
        # -------------------------

        st.subheader("Temps de réaction")

        fig, ax = plt.subplots()
        ax.plot(df["session"], df["avg_reaction_time"], marker="o")
        st.pyplot(fig)

        # -------------------------
        # IMPULSIVITÉ
        # -------------------------

        st.subheader("Impulsivité")

        fig, ax = plt.subplots()
        ax.plot(df["session"], df["impulsivity"], marker="o")
        st.pyplot(fig)

        # -------------------------
        # COMPARAISON
        # -------------------------

        st.subheader("TDAH vs non-TDAH")

        tdah = df[df["tdah"] == "Oui"]
        no_tdah = df[df["tdah"] == "Non"]

        st.write("Score TDAH :", tdah["score"].mean())
        st.write("Score non-TDAH :", no_tdah["score"].mean())

    else:
        st.warning("Aucune donnée disponible.")

# ===================================================
# JEU PATIENT
# ===================================================

else:

    st.header("Exercice adaptatif de saccades")

    st.write("Clique uniquement sur les boules vertes.")

    # -------------------------
    # PATIENT
    # -------------------------

    patient_id = st.text_input("Code patient")

    birth_date = st.date_input(
        "Date de naissance",
        min_value=date(2000, 1, 1),
        max_value=date.today()
    )

    tdah = st.selectbox("TDAH ?", ["Oui", "Non"])

    start = st.button("Commencer séance")

    if start:
        st.session_state.started = True

    if "started" not in st.session_state:
        st.session_state.started = False

    # ===================================================
    # VARIABLES SESSION
    # ===================================================

    if st.session_state.started:

        if "score" not in st.session_state:
            st.session_state.score = 0

        if "errors" not in st.session_state:
            st.session_state.errors = 0

        if "reaction_times" not in st.session_state:
            st.session_state.reaction_times = []

        if "num_columns" not in st.session_state:
            st.session_state.num_columns = 3

        if "target_position" not in st.session_state:
            st.session_state.target_position = random.randint(0, 2)

        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()

        # IA variables
        if "impulsivity" not in st.session_state:
            st.session_state.impulsivity = 0

        if "fatigue_score" not in st.session_state:
            st.session_state.fatigue_score = 0

        if "focus_mode" not in st.session_state:
            st.session_state.focus_mode = False

        # ===================================================
        # JEU
        # ===================================================

        cols = st.columns(st.session_state.num_columns)

        for i in range(st.session_state.num_columns):

            with cols[i]:

                if i == st.session_state.target_position:

                    if st.button("🟢", key=f"g{i}"):

                        reaction_time = time.time() - st.session_state.start_time
                        st.session_state.reaction_times.append(reaction_time)

                        st.session_state.score += 1

                        st.session_state.target_position = random.randint(
                            0,
                            st.session_state.num_columns - 1
                        )

                        st.session_state.start_time = time.time()

                        st.rerun()

                else:

                    if st.button("🔴", key=f"r{i}"):

                        st.session_state.errors += 1

                        click_time = time.time() - st.session_state.start_time

                        if click_time < 0.5:
                            st.session_state.impulsivity += 1

        # ===================================================
        # IA ADAPTATIVE (FATIGUE)
        # ===================================================

        if st.session_state.reaction_times:

            avg_time = sum(st.session_state.reaction_times) / len(st.session_state.reaction_times)

            if avg_time > 2 or st.session_state.errors > 5:
                st.session_state.fatigue_score += 1
            else:
                st.session_state.fatigue_score = max(0, st.session_state.fatigue_score - 1)

        # adaptation difficulté
        if st.session_state.fatigue_score >= 3:
            st.session_state.num_columns = 3
            st.warning("Fatigue détectée → simplification")

        elif st.session_state.score >= 10:
            st.session_state.num_columns = 7

        elif st.session_state.score >= 5:
            st.session_state.num_columns = 5

        # ===================================================
        # RESULTATS
        # ===================================================

        st.subheader("Résultats")

        st.write("Score :", st.session_state.score)
        st.write("Erreurs :", st.session_state.errors)
        st.write("Impulsivité :", st.session_state.impulsivity)
        st.write("Fatigue :", st.session_state.fatigue_score)

        if st.session_state.reaction_times:
            st.write("Temps moyen :", round(avg_time, 2), "s")

        # ===================================================
        # PROFIL AUTOMATIQUE PATIENT
        # ===================================================

        st.subheader("Profil attentionnel automatique")

        profile = []

        if st.session_state.score >= 10:
            profile.append("🟢 Bonne performance attentionnelle")
        elif st.session_state.score >= 5:
            profile.append("🟡 Performance moyenne")
        else:
            profile.append("🔴 Difficultés attentionnelles")

        if st.session_state.errors >= 5:
            profile.append("🔴 Contrôle inhibiteur faible")
        elif st.session_state.errors >= 2:
            profile.append("🟡 Erreurs modérées")
        else:
            profile.append("🟢 Bonne inhibition")

        if st.session_state.impulsivity >= 5:
            profile.append("🔴 Forte impulsivité")
        elif st.session_state.impulsivity >= 3:
            profile.append("🟡 Impulsivité modérée")
        else:
            profile.append("🟢 Bon contrôle moteur")

        if st.session_state.fatigue_score >= 3:
            profile.append("🔵 Fatigabilité élevée")
        elif st.session_state.fatigue_score >= 1:
            profile.append("🟡 Légère fatigue")
        else:
            profile.append("🟢 Bonne endurance")

        if st.session_state.reaction_times:
            if avg_time > 2:
                profile.append("🔴 Temps de réaction lent")
            elif avg_time > 1:
                profile.append("🟡 Temps moyen")
            else:
                profile.append("🟢 Bonne vitesse")

        for p in profile:
            st.write(p)

        # ===================================================
        # FEEDBACK
        # ===================================================

        if st.session_state.impulsivity >= 3:
            st.warning("Prends ton temps avant de cliquer.")

        if st.session_state.fatigue_score >= 3:
            st.warning("Fatigue détectée → pause recommandée.")

        # ===================================================
        # PDF
        # ===================================================

        if st.button("Exporter PDF"):

            file_name = f"data/rapport_{patient_id}.pdf"
            doc = SimpleDocTemplate(file_name)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph("Rapport orthoptique", styles["Title"]))
            story.append(Spacer(1, 12))

            story.append(Paragraph(f"Patient : {patient_id}", styles["Normal"]))
            story.append(Paragraph(f"TDAH : {tdah}", styles["Normal"]))
            story.append(Paragraph(f"Score : {st.session_state.score}", styles["Normal"]))
            story.append(Paragraph(f"Erreurs : {st.session_state.errors}", styles["Normal"]))
            story.append(Paragraph(f"Impulsivité : {st.session_state.impulsivity}", styles["Normal"]))
            story.append(Paragraph(f"Fatigue : {st.session_state.fatigue_score}", styles["Normal"]))

            if st.session_state.reaction_times:
                story.append(Paragraph(f"Temps moyen : {round(avg_time,2)} s", styles["Normal"]))

            doc.build(story)

            st.success("PDF généré ✔")

        # ===================================================
        # SAUVEGARDE CSV
        # ===================================================

        if st.button("Terminer séance"):

            avg_time = 0

            if st.session_state.reaction_times:
                avg_time = sum(st.session_state.reaction_times) / len(st.session_state.reaction_times)

            session = pd.DataFrame([{
                "patient_id": patient_id,
                "birth_date": birth_date,
                "tdah": tdah,
                "score": st.session_state.score,
                "errors": st.session_state.errors,
                "impulsivity": st.session_state.impulsivity,
                "fatigue": st.session_state.fatigue_score,
                "num_columns": st.session_state.num_columns,
                "avg_reaction_time": round(avg_time, 2)
            }])

            file_path = "data/results.csv"

            if os.path.exists(file_path):
                old = pd.read_csv(file_path)
                new = pd.concat([old, session], ignore_index=True)
                new.to_csv(file_path, index=False)
            else:
                session.to_csv(file_path, index=False)

            st.success("Séance sauvegardée ✔")