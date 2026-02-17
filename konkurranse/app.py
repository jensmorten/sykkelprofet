import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import root_mean_squared_error
import os
import io
import time
from cryptography.fernet import Fernet
from pathlib import Path


# --------------------------------------------------
# KONFIG
# --------------------------------------------------

#TARGET_FILE = "test_target_secret.csv"
BASE_DIR = Path(__file__).parent
LEADERBOARD_FILE = BASE_DIR / "leaderboard.csv"
PLOT_DIR = BASE_DIR / "plots"
PLOT_DIR.mkdir(exist_ok=True)


st.title("🚲 Bli sykkelprofet i egen by! ")

# --------------------------------------------------
# VIS LEADERBOARD ALLTID
# --------------------------------------------------

st.subheader("🏆 Leaderboard ")
st.markdown("Laveste RMSE vinnner")

if os.path.exists(LEADERBOARD_FILE):
    leaderboard = pd.read_csv(LEADERBOARD_FILE)
    leaderboard = leaderboard.sort_values("RMSE").reset_index(drop=True)

    medals = []
    for i in range(len(leaderboard)):
        if i == 0:
            medals.append("🥇")
        elif i == 1:
            medals.append("🥈")
        elif i == 2:
            medals.append("🥉")
        else:
            medals.append(f"{i+1}.")

    leaderboard_display = leaderboard.copy()
    leaderboard_display.insert(0, "Rank", medals)

    st.dataframe(
        leaderboard_display[["Rank", "Lagnavn", "RMSE"]],
        use_container_width=True, hide_index=True
    )

    st.markdown("### 📊 Last ned plot")

    for _, row in leaderboard.iterrows():
        plot_path = PLOT_DIR / row["plot_file"]
        if plot_path.exists():
            with open(plot_path, "rb") as f:
                st.download_button(
                    label=f"Last ned plot – {row['Lagnavn']}",
                    data=f,
                    file_name=row["plot_file"],
                    mime="image/png"
                )

    # ---------------------------------------------
    # 🔽 Last ned leaderboard-knapp
    # ---------------------------------------------

    csv_data = leaderboard.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Last ned leaderboard.csv",
        data=csv_data,
        file_name="leaderboard.csv",
        mime="text/csv"
    )

else:
    st.info("Ingen innleveringer enda.")

# --------------------------------------------------
# LAST FASIT
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
SECRET_FILE = BASE_DIR / "test_target_secret_encrypted.bin"

key = st.secrets["ENC_KEY"].encode()
cipher = Fernet(key)

with open(SECRET_FILE, "rb") as f:
    encrypted = f.read()

decrypted = cipher.decrypt(encrypted)

y_true = pd.read_csv(io.BytesIO(decrypted), parse_dates=["ds"])

# --------------------------------------------------
# OPPLASTING (MED SUBMIT-KNAPP)
# --------------------------------------------------

st.subheader("📤 Last opp innlevering")

with st.form("submission_form"):

    uploaded_file = st.file_uploader(
        "Last opp submission.csv",
        type=["csv"]
    )

    team_name = st.text_input("Lagnavn")

    submit_button = st.form_submit_button("🚀 Submit")

# Kjør berre når knapp trykkes
if submit_button:

    if not uploaded_file:
        st.error("Du må laste opp en fil.")
        st.stop()

    if not team_name:
        st.error("Du må skrive lagnavn.")
        st.stop()

    y_pred = pd.read_csv(uploaded_file, parse_dates=["ds"])

    # --------------------------------------------------
    # VALIDER FORMAT
    # --------------------------------------------------

    if not {"ds", "yhat"}.issubset(y_pred.columns):
        st.error("Filen må inneholde kolonnene: ds, yhat")
        st.stop()

    df = y_true.merge(y_pred, on="ds")

    if len(df) != len(y_true):
        st.error("Feil antall rader eller mismatch på ds")
        st.stop()

    # --------------------------------------------------
    # BEREGN RMSE
    # --------------------------------------------------

    rmse = root_mean_squared_error(df["y"], df["yhat"])

    st.success(f"RMSE: {rmse:.2f}")

    # --------------------------------------------------
    # PLOTT
    # --------------------------------------------------

    timestamp = int(time.time())
    safe_team = team_name.replace(" ", "_")

    plot_filename = f"{safe_team}_{timestamp}.png"
    plot_path = PLOT_DIR / plot_filename

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df["ds"], df["y"], label="Faktisk")
    ax.plot(df["ds"], df["yhat"], label="Predikert")
    ax.set_title(f"{team_name} – RMSE: {rmse:.2f}")
    ax.legend()

    fig.savefig(plot_path, dpi=300)
    plt.close(fig)


    # --------------------------------------------------
    # OPPDATER LEADERBOARD
    # --------------------------------------------------

    new_entry = pd.DataFrame({
    "Lagnavn": [team_name],
    "RMSE": [rmse],
    "plot_file": [plot_filename]
    })

    if os.path.exists(LEADERBOARD_FILE):
        leaderboard = pd.read_csv(LEADERBOARD_FILE)
        leaderboard = pd.concat([leaderboard, new_entry], ignore_index=True)
    else:
        leaderboard = new_entry

    leaderboard = leaderboard.sort_values("RMSE").reset_index(drop=True)
    leaderboard.to_csv(LEADERBOARD_FILE, index=False)

    st.rerun()

st.markdown("---")

with st.expander("ℹ️ Hva betyr RMSE?"):
    st.write("""
    **RMSE (Root Mean Squared Error)** måler hvor langt prediksjonene
    ligger fra de faktiske verdiene.

    Formel:

    RMSE = √( gjennomsnitt( (faktisk − predikert)² ) )

    • Lavere er bedre  
    • Store feil straffes ekstra mye  
    • Måles i antall turer

    RMSE = 50 betyr at modellen i snitt bommer med ca 50 turer per 3-timersperiode.
    """)
