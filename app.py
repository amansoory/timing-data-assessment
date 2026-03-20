import streamlit as st
from data_processor import load_contacts, parse_date, get_priority, PRIORITY_MAP
from datetime import datetime

st.set_page_config(page_title="Timing — Contact Recommendations", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #f0fdfa;
    }

    h1 {
        color: #0d9488 !important;
    }

    h2, h3 {
        color: #115e59 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #e0f7f4 !important;
        border-right: 2px solid #0d9488;
    }

    input {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #0d9488 !important;
    }

    [data-baseweb="select"] {
        background-color: #ffffff !important;
    }

    [data-baseweb="input"] {
        background-color: #ffffff !important;
    }

    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }

    [data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    [data-baseweb="popover"] li:hover {
        background-color: #ccfbf1 !important;
    }

    [data-baseweb="menu"] {
        background-color: #ffffff !important;
    }

    [data-baseweb="menu"] li {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    [data-baseweb="menu"] li:hover {
        background-color: #ccfbf1 !important;
    }

    Christopher Johnson,chris@nvidia.com,,mentor



    [data-testid="stAlert"] {
        background-color: #ccfbf1 !important;
        border-left-color: #0d9488 !important;
        color: #115e59 !important;
    }

    [data-testid="stAlert"] p {
        color: #115e59 !important;
    }

    hr {
        border-color: #99f6e4 !important;
    }
</style>
""", unsafe_allow_html=True)

contacts = load_contacts("contacts.csv")
today = datetime.now()

# ---- Header ----
st.title("Timing — Contact Recommendation Engine")
st.markdown("Helping you stay on top of your professional relationships.")
st.divider()

# ---- Sidebar Filters ----
st.sidebar.header("Filters")
search = st.sidebar.text_input("Search by name, email, or role")
role_filter = st.sidebar.multiselect(
    "Filter by role",
    options=["Investor", "Mentor", "Advisor", "Friend", "Other"],
    default=["Investor", "Mentor", "Advisor", "Friend", "Other"]
)
sort_by = st.sidebar.selectbox(
    "Sort by",
    options=["Priority (highest first)", "Days since contact (longest first)", "Name (A-Z)"]
)

# ---- Process All Contacts ----
processed = []
missing_names = []

for contact in contacts:
    parsed_date = parse_date(contact.get("last_contacted", ""))
    raw_role = contact.get("notes", "").strip().lower() if contact.get("notes") else "other"
    role = raw_role.capitalize() if raw_role else "Other"

    if parsed_date is None:
        days_since = None
        missing_names.append({"name": contact["name"], "role": role})
    else:
        days_since = (today - parsed_date).days
        if days_since < 0:
            continue

    processed.append({
        "Name": contact["name"],
        "Email": contact.get("email", ""),
        "Company": contact.get("company", ""),
        "Role": role,
        "Last Contacted": contact.get("last_contacted", "") if contact.get("last_contacted") else "N/A",
        "Days Since Contact": days_since if days_since is not None else "Unknown",
        "Priority": get_priority(contact.get("notes", "")),
    })

# ---- Apply Filters ----
filtered = []
for c in processed:
    if c["Role"] not in role_filter:
        continue
    if search:
        search_lower = search.lower()
        if (search_lower not in c["Name"].lower()
            and search_lower not in c["Email"].lower()
            and search_lower not in c["Role"].lower()):
            continue
    filtered.append(c)

# ---- Apply Sort ----
if sort_by == "Priority (highest first)":
    filtered.sort(key=lambda x: (
        x["Priority"],
        -(x["Days Since Contact"] if isinstance(x["Days Since Contact"], int) else 999999)
    ))
elif sort_by == "Days since contact (longest first)":
    filtered.sort(key=lambda x: -(x["Days Since Contact"] if isinstance(x["Days Since Contact"], int) else 999999))
else:
    filtered.sort(key=lambda x: x["Name"])

# ---- All Contacts Table ----
st.subheader(f"Contacts ({len(filtered)} shown)")
if filtered:
    table_md = "| Name | Email | Company | Role | Last Contacted | Days Since Contact |\n"
    table_md += "|------|-------|---------|------|----------------|--------------------|\n"
    for c in filtered:
        table_md += f"| {c['Name']} | {c['Email']} | {c['Company']} | {c['Role']} | {c['Last Contacted']} | {c['Days Since Contact']} |\n"
    st.markdown(table_md)
else:
    st.info("No contacts match your current filters.")

# ---- Top Recommendations ----
st.divider()
st.subheader("Top Recommendations — Who to Reach Out To")

recs = sorted(filtered, key=lambda x: (
    x["Priority"],
    -(x["Days Since Contact"] if isinstance(x["Days Since Contact"], int) else 999999)
))[:3]

if recs:
    for i, rec in enumerate(recs, 1):
        days_str = f"{rec['Days Since Contact']} days" if isinstance(rec["Days Since Contact"], int) else "Unknown"
        st.markdown(f"""
        **{i}. {rec['Name']}**  
        📧 {rec['Email']} · 🏢 {rec['Role']} · 🕐 Last contacted: {days_str}
        """)
else:
    st.info("No recommendations match your current filters.")

# ---- Data Quality Flags ----
if missing_names:
    st.divider()
    st.subheader("⚠️ Data Quality Flags")
    st.markdown("These contacts have missing or invalid dates:")
    for contact in missing_names:
        st.warning(f"**{contact['name']}** ({contact['role']}) — No valid last contact date")

# ---- Footer ----
st.divider()
st.caption("Built for Timing Engineering Intern Assessment")