import streamlit as st
import sqlite3
from datetime import date, timedelta

st.set_page_config(page_title="Smart Plant Care", page_icon="🌱")
DB = "plants.db"

def connect():
    return sqlite3.connect(DB)

def setup():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT,
            location TEXT,
            interval_days INTEGER NOT NULL,
            last_watered TEXT NOT NULL,
            notes TEXT
        )""")

def add_plant(name, species, location, interval_days, last_watered, notes):
    with connect() as con:
        con.execute("""INSERT INTO plants
            (name, species, location, interval_days, last_watered, notes)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (name, species, location, interval_days, last_watered.isoformat(), notes))

def get_plants():
    with connect() as con:
        return con.execute("SELECT * FROM plants ORDER BY name").fetchall()

def mark_watered(plant_id):
    with connect() as con:
        con.execute("UPDATE plants SET last_watered=? WHERE id=?",
                    (date.today().isoformat(), plant_id))

def delete_plant(plant_id):
    with connect() as con:
        con.execute("DELETE FROM plants WHERE id=?", (plant_id,))

setup()
st.title("🌱 Smart Plant Care")
st.write("Organize your plants and track estimated watering dates.")

with st.form("add_plant_form"):
    st.subheader("Add a plant")
    name = st.text_input("Plant name *")
    species = st.text_input("Plant type / species")
    location = st.text_input("Location")
    interval = st.number_input("Watering interval (days)", min_value=1, max_value=60, value=7)
    last_watered = st.date_input("Last watered", value=date.today())
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Save plant")
    if submitted:
        if name.strip():
            add_plant(name.strip(), species.strip(), location.strip(), int(interval), last_watered, notes.strip())
            st.success("Plant saved successfully!")
            st.rerun()
        else:
            st.error("Please enter a plant name.")

st.divider()
st.subheader("My plants")
for plant in get_plants():
    plant_id, name, species, location, interval, last_watered, notes = plant
    due_date = date.fromisoformat(last_watered) + timedelta(days=interval)
    with st.container(border=True):
        st.markdown(f"### {name}")
        st.write(f"**Type:** {species or 'Not specified'}")
        st.write(f"**Location:** {location or 'Not specified'}")
        st.write(f"**Last watered:** {last_watered}")
        st.write(f"**Estimated next watering:** {due_date.isoformat()}")
        if due_date <= date.today():
            st.warning("Watering may be due. Check the soil and plant needs first.")
        else:
            st.info(f"Estimated watering in {(due_date - date.today()).days} day(s).")
        if notes:
            st.caption(f"Notes: {notes}")
        c1, c2 = st.columns(2)
        if c1.button("Mark watered today", key=f"water_{plant_id}"):
            mark_watered(plant_id)
            st.rerun()
        if c2.button("Delete plant", key=f"delete_{plant_id}"):
            delete_plant(plant_id)
            st.rerun()
