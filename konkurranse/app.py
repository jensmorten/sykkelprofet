import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import root_mean_squared_error
import os
import io
from cryptography.fernet import Fernet
from pathlib import Path


# --------------------------------------------------
# KONFIG
# --------------------------------------------------

#TARGET_FILE = "test_target_secret.csv"
LEADERBOARD_FILE = "leaderboard.csv"

st.title("🚲 Prophet-konkurranse – Bysykkel")

# --------------------------------------------------
# VIS LEADERBOARD ALLTID
# --------------------------------------------------

st.subheader("🏆 Leaderboard")

if os.path.exists(LEADERBOARD_FILE):
    leaderboard = pd.read_csv(LEADERBOARD_FILE)
    leaderboard = leaderboard.sort_values("rmse").reset_index(drop=True)

    # Legg til plassering og emoji
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

    st.dataframe(leaderboard_display, use_container_width=True)
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
# OPPLASTING
# --------------------------------------------------

st.subheader("📤 Last opp submission")

uploaded_file = st.file_uploader(
    "Last opp submission.csv",
    type=["csv"]
)

team_name = st.text_input("Lagnavn")

if uploaded_file and team_name:

    y_pred = pd.read_csv(uploaded_file, parse_dates=["ds"])

    # --------------------------------------------------
    # VALIDER FORMAT
    # --------------------------------------------------

    if not {"ds", "yhat"}.issubset(y_pred.columns):
        st.error("Filen må inneholde kolonnene: ds, yhat")
    else:

        df = y_true.merge(y_pred, on="ds")

        if len(df) != len(y_true):
            st.error("Feil antall rader eller mismatch på ds")
        else:

            # --------------------------------------------------
            # BEREGN RMSE
            # --------------------------------------------------

            rmse = root_mean_squared_error(df["y"], df["yhat"])

            st.success(f"RMSE: {rmse:.2f}")

            # --------------------------------------------------
            # PLOTT
            # --------------------------------------------------

            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(df["ds"], df["y"], label="Faktisk")
            ax.plot(df["ds"], df["yhat"], label="Predikert")
            ax.set_title(f"{team_name} – RMSE: {rmse:.2f}")
            ax.legend()

            st.pyplot(fig)

            # --------------------------------------------------
            # OPPDATER LEADERBOARD
            # --------------------------------------------------

            new_entry = pd.DataFrame({
                "team": [team_name],
                "rmse": [rmse]
            })

            if os.path.exists(LEADERBOARD_FILE):
                leaderboard = pd.read_csv(LEADERBOARD_FILE)

                # Valgfritt: berre beste score per lag
                if team_name in leaderboard["team"].values:
                    leaderboard = leaderboard[leaderboard["team"] != team_name]

                leaderboard = pd.concat(
                    [leaderboard, new_entry],
                    ignore_index=True
                )
            else:
                leaderboard = new_entry

            leaderboard = leaderboard.sort_values("rmse").reset_index(drop=True)
            leaderboard.to_csv(LEADERBOARD_FILE, index=False)

            st.st.rerun()
