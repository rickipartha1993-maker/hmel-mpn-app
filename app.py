import datetime
import io
import os
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Page Configuration
st.set_page_config(
    page_title="HMEL-PPWH Material Pick up Note", page_icon="📋", layout="wide"
)

# Initialize Session State for Memory & Users
if "authorized_users" not in st.session_state:
    st.session_state.authorized_users = {
        "admin": "admin123",
        "supervisor1": "pass123",
    }  # Default Master & User ID

if "history_grades" not in st.session_state:
    st.session_state.history_grades = ["FORR", "GRADE-A", "GRADE-B"]

if "history_batch" not in st.session_state:
    st.session_state.history_batch = ["H26I1021", "H36I1021"]

if "history_vehicles" not in st.session_state:
    st.session_state.history_vehicles = ["HR 35 B1560", "PB 08 AB 1234"]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# --- AUTHENTICATION & DEVELOPER PANEL ---
if not st.session_state.logged_in:
  st.title("🔐 HMEL MPN App - Login")
  st.markdown("দয়া করে আপনার আইডি এবং পাসওয়ার্ড দিয়ে লগইন করুন।")

  login_tab1, login_tab2 = st.tabs(["Login", "Developer / Admin Control"])

  with login_tab1:
    username = st.text_input("User ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
      if (
          username in st.session_state.authorized_users
          and st.session_state.authorized_users[username] == password
      ):
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.session_state.is_admin = username == "admin"
        st.rerun()
      else:
        st.error("ভুল ইউজার আইডি বা পাসওয়ার্ড!")

  with login_tab2:
    st.info("শুধুমাত্র ডেভেলপার/মাস্টার অ্যাডমিন নতুন আইডি তৈরি করতে পারবেন।")
    admin_pass = st.text_input("Master Admin Password", type="password")
    if admin_pass == "admin123":
      st.success("অ্যাডমিন প্যানেল আনলকড!")
      new_user = st.text_input("নতুন ইউজার আইডি")
      new_pass = st.text_input("নতুন পাসওয়ার্ড", type="password")
      if st.button("Create New User ID"):
        if new_user and new_pass:
          st.session_state.authorized_users[new_user] = new_pass
          st.success(f"সফলভাবে তৈরি হলো আইডি: {new_user}")
        else:
          st.error("সব ফিল্ড পূরণ করুন।")
    else:
      st.warning("মাস্টার পাসওয়ার্ড দিন (ডিফল্ট: admin123)")

  st.stop()

# --- MAIN APP INTERFACE ---
st.sidebar.title(f"👤 স্বাগতম: {st.session_state.current_user}")
if st.sidebar.button("Logout"):
  st.session_state.logged_in = False
  st.rerun()

st.title("📦 HMEL-PPWH-Material Pick up Note (MPN)")
st.write("ডিজিটাল লোডিং স্লিপ জেনারেটর এবং স্টোরেজ সিস্টেম[span_0](start_span)[span_0](end_span)")

with st.form("mpn_form"):
  col1, col2, col3, col4 = st.columns(4)

  with col1:
    s_no = st.text_input("S. No.", value="10")
    # Vehicle No with memory
    vehicle_no = st.selectbox(
        "Vehicle No.",
        options=st.session_state.history_vehicles,
        index=0,
        key="veh_select",
    )
    new_veh = st.text_input("অথবা নতুন ভেহিকেল নম্বর লিখুন")
    if new_veh:
      vehicle_no = new_veh
      if new_veh not in st.session_state.history_vehicles:
        st.session_state.history_vehicles.append(new_veh)

  with col2:
    date_time = st.text_input(
        "Date/Time", value=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    )
    loading_bay = st.text_input("Loading Bay No.", value="4")

  with col3:
    shift = st.text_input("Shift", value="G")
    damaged_bags = st.text_input("Damaged Bags", value="0")

  with col4:
    replaced_bags = st.text_input("Replaced Bags", value="0")
    storage_location = st.text_input("Storage Location", value="C-05")

  st.divider()

  col_a, col_b, col_c = st.columns(3)
  with col_a:
    grade = st.selectbox(
        "Grade", options=st.session_state.history_grades, index=0
    )
    new_grade = st.text_input("নতুন গ্রেড যোগ করুন")
    if new_grade:
      grade = new_grade
      if new_grade not in st.session_state.history_grades:
        st.session_state.history_grades.append(new_grade)

  with col_b:
    batch_no = st.selectbox(
        "Batch No.", options=st.session_state.history_batch, index=0
    )
    new_batch = st.text_input("নতুন ব্যাচ নম্বর যোগ করুন")
    if new_batch:
      batch_no = new_batch
      if new_batch not in st.session_state.history_batch:
        st.session_state.history_batch.append(new_batch)

  with col_c:
    quantity_mt = st.text_input("Quantity (MT)", value="30")
    no_of_bags = st.text_input("No. of Bags", value="1200")

  st.divider()
  st.subheader("Truck Condition & Safety Check Points")
  c1, c2, c3 = st.columns(3)
  with c1:
    body_damage = st.checkbox("Body Damages OK", value=True)
    protruding_nails = st.checkbox("Protruding Nails/Bolts OK", value=True)
  with c2:
    tarpaulins = st.checkbox("No. of Tarpaulins OK", value=True)
    truck_accepted = st.checkbox("Truck Accepted", value=True)
  with c3:
    hand_brake = st.checkbox("Hand Brake OK", value=True)
    wheel_choke = st.checkbox("Wheel Choke OK", value=True)

  st.subheader("Signatures & Personnel")
  p1, p2, p3 = st.columns(3)
  with p1:
    supervisor_name = st.text_input(
        "Loading Supervisor Name", value="Nilonjan Roy"
    )
  with p2:
    shift_incharge = st.text_input("Shift Incharge Name", value="Jaspal")
  with p3:
    forklift_driver = st.text_input("Forklift Driver Name", value="Raju")

  submitted = st.form_submit_button("Generate PDF & Save Record")

if submitted:
  st.success("ফর্ম সফলভাবে সাবমিট ও প্রসেস করা হয়েছে!")

  # PDF Generation Logic
  buffer = io.BytesIO()
  p = canvas.Canvas(buffer, pagesize=letter)
  width, height = letter

  p.drawString(
      50, height - 50, "HMEL-PPWH - Material Pick up Note (MPN)[span_1](start_span)[span_1](end_span)"
  )
  p.drawString(
      50, height - 80, f"Date/Time: {date_time} | Shift: {shift}[span_2](start_span)[span_2](end_span)"
  )
  p.drawString(
      50,
      height - 100,
      f"Vehicle No.: {vehicle_no} | Loading Bay: {loading_bay}[span_3](start_span)[span_3](end_span)",
  )
  p.drawString(
      50,
      height - 120,
      f"Grade: {grade} | Batch No.: {batch_no} | Qty: {quantity_mt} MT"
      f[span_4](start_span)"[span_4](end_span)",
  )
  p.drawString(
      50,
      height - 140,
      f"Total No. of Bags: {no_of_bags} | Storage Location:"
      f" {storage_location}[span_5](start_span)[span_5](end_span)",
  )
  p.drawString(
      50, height - 180, f"Loading Supervisor: {supervisor_name}[span_6](start_span)[span_6](end_span)"
  )
  p.drawString(
      50, height - 200, f"Forklift Driver: {forklift_driver}[span_7](start_span)[span_7](end_span)"
  )
  p.drawString(
      50, height - 220, f"Shift Incharge: {shift_incharge}[span_8](start_span)[span_8](end_span)"
  )

  p.showPage()
  p.save()
  buffer.seek(0)

  st.download_button(
      label="📥 Download Filled PDF",
      data=buffer,
      file_name=f"MPN_{vehicle_no.replace(' ', '_')}.pdf",
      mime="application/pdf",
  )
