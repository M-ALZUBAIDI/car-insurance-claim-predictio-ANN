import streamlit as st
import random

# ╔══════════════════════════════════════════════════════════════════╗
# ║                     YOUR ORIGINAL CLASSES                       ║
# ╚══════════════════════════════════════════════════════════════════╝

# ─── Guide Class (Mohammed Alzubaidi) ─────────────────────────────────────────
class Guide:
    def __init__(s, name, guide_id):
        s.name = name
        s.guide_id = guide_id
        s.assigned_sites = []

    def login(s, entered_id):
        if s.guide_id == entered_id:
            return True
        return False

    def view_my_assigned_site(s):
        if not s.assigned_sites:
            print("You are not currently assigned to any site.")
        else:
            print("Your assigned sites:")
            for site in s.assigned_sites:
                print(f"- {site}")


# ─── Visitor Class (Meshari & Mohamed) ───────────────────────────────────────
class Visitor:
    def __init__(s, name, nationality, username, password):
        s.name = name
        s.nationality = nationality
        s.username = username
        s.password = password
        s.bookings = []  # list of dicts: [{booking_id, site_name}]

    def login(s, entered_username, entered_password):
        if s.username == entered_username and s.password == entered_password:
            return True
        return False

    def register_in_system(s):
        print(f"You are now registered as {s.name} and your nationality is {s.nationality}. Welcome!")


# ─── Manager Class (Saleh & Riyadh) ──────────────────────────────────────────
class Manager:
    def __init__(s):
        s.sites = []
        s.guide = {}
        s.visitors = {}       # username → Visitor object
        s.booking_ids = set()

    def site_exists(s, name):
        for site in s.sites:
            if site["name"] == name:
                return True
        return False

    def guide_exists(s, guide_id):
        return guide_id in s.guide

    def visitor_exists(s, username):
        return username in s.visitors

    def add_site(s, name, site_type, capacity, guide_id=None):
        site = {
            "name": name,
            "type": site_type,
            "capacity": capacity,
            "guide_id": guide_id,
            "visitors": 0,
            "status": "Open"
        }
        s.sites.append(site)
        if guide_id:
            s.guide[guide_id].assigned_sites.append(name)

    def view_all_sites(s):
        if not s.sites:
            print("No sites available.")
            return
        for site in s.sites:
            print(f"Name: {site['name']} | Type: {site['type']} | "
                  f"Visitors: {site['visitors']} | Capacity: {site['capacity']} | "
                  f"Guide: {s.guide[site['guide_id']].name if site['guide_id'] and site['guide_id'] in s.guide else 'N/A'} | Status: {site['status']}")

    def view_open_sites(s):
        open_sites = []
        for site in s.sites:
            if site["status"] == "Open":
                open_sites.append(site)
        return open_sites

    def add_new_Guide(s, name):
        # Guide ID is generated randomly
        while True:
            guide_id = random.randint(1000, 9999)
            if guide_id not in s.guide:
                break
        new_guide = Guide(name, guide_id)
        s.guide[guide_id] = new_guide
        print(f"Guide '{name}' added with ID: {guide_id}")
        return guide_id

    def add_new_visitor(s, name, nationality, username, password):
        if username in s.visitors:
            return False
        new_visitor = Visitor(name, nationality, username, password)
        s.visitors[username] = new_visitor
        return True

    def assign_guide(s, site_name, guide_id):
        if guide_id not in s.guide:
            print(f"Guide with ID '{guide_id}' is not registered.")
            return
        for site in s.sites:
            if site["name"] == site_name:
                site["guide_id"] = guide_id
                s.guide[guide_id].assigned_sites.append(site_name)
                print(f"Guide '{s.guide[guide_id].name}' assigned to '{site_name}'.")
                return
        print(f"Site '{site_name}' not found.")

    def close_site(s, site_name):
        for site in s.sites:
            if site["name"] == site_name:
                site["status"] = "Closed"
                print(f"Site '{site_name}' is now closed.")
                return
        print(f"Site '{site_name}' not found.")

    def view_summary(s):
        total_sites = len(s.sites)
        total_visitors = sum(site["visitors"] for site in s.sites)
        most_visited = max(s.sites, key=lambda site: site["visitors"], default=None)
        print(f"Total sites: {total_sites}")
        print(f"Total registered visitors: {total_visitors}")
        if most_visited:
            print(f"Most visited site: {most_visited['name']} ({most_visited['visitors']} visitors)")
        else:
            print("No sites yet.")

    def generate_booking_id(s):
        while True:
            booking_id = random.randint(1000, 9999)
            if booking_id not in s.booking_ids:
                s.booking_ids.add(booking_id)
                return booking_id

    def register_visitor(s, visitor, site_name):
        for site in s.sites:
            if site["name"] == site_name:
                if site["status"] != "Open":
                    return False, "Site is closed."
                if site["visitors"] >= site["capacity"]:
                    return False, "Site is full."
                # check visitor not already booked this site
                for b in visitor.bookings:
                    if b["site_name"] == site_name:
                        return False, "You already registered for this site."
                site["visitors"] += 1
                booking_id = s.generate_booking_id()
                visitor.bookings.append({"booking_id": booking_id, "site_name": site_name})
                return True, booking_id
        return False, "Site not found."

    def cancel_registration(s, visitor, booking_id):
        for b in visitor.bookings:
            if b["booking_id"] == booking_id:
                site_name = b["site_name"]
                for site in s.sites:
                    if site["name"] == site_name:
                        site["visitors"] -= 1
                        break
                s.booking_ids.remove(booking_id)
                visitor.bookings.remove(b)
                return True, f"Booking {booking_id} cancelled."
        return False, "Booking ID not found."

    def view_visitors_by_guide(s, guide_id):
        result = []
        for site in s.sites:
            if site["guide_id"] == guide_id:
                result.append({"site": site["name"], "visitors": site["visitors"]})
        return result


# ╔══════════════════════════════════════════════════════════════════╗
# ║                  STREAMLIT APP (added for web UI)               ║
# ╚══════════════════════════════════════════════════════════════════╝

st.set_page_config(
    page_title="AlUla Tourism System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #1A1208; }
[data-testid="stSidebar"] { background: #120D05 !important; border-right: 1px solid #C8922A55; }
[data-testid="stSidebar"] * { color: #E8D5A0 !important; }
.main .block-container { padding-top: 2rem; }

h1, h2, h3, h4 { color: #E8B84B !important; font-weight: 600 !important; }
p, div, span, label { color: #E8D5A0 !important; }
.stMarkdown p { color: #E8D5A0 !important; }

input { background: #2A1E0F !important; color: #FFE8A0 !important; border: 1px solid #C8922A88 !important; border-radius: 8px !important; }
.stTextInput input, .stNumberInput input { background: #2A1E0F !important; color: #FFE8A0 !important; }
.stTextInput label, .stNumberInput label, .stSelectbox label { color: #E8B84B !important; font-weight: 500 !important; }

.stButton > button { background: #C8922A !important; color: #1A1208 !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 14px !important; padding: 0.5rem 1.4rem !important; }
.stButton > button:hover { background: #E8B84B !important; color: #1A1208 !important; }

.stSelectbox > div > div { background: #2A1E0F !important; color: #FFE8A0 !important; border: 1px solid #C8922A88 !important; }
.stTabs [data-baseweb="tab"] { color: #C8A870 !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { color: #E8B84B !important; border-bottom: 2px solid #E8B84B !important; }
.stTabs [data-baseweb="tab-list"] { background: #120D05 !important; border-bottom: 1px solid #3A2A10 !important; }

[data-testid="metric-container"] { background: #2A1E0F !important; border: 1px solid #C8922A55 !important; border-radius: 10px !important; padding: 1rem !important; }
[data-testid="stMetricValue"] { color: #E8B84B !important; font-size: 28px !important; }
[data-testid="stMetricLabel"] { color: #C8A870 !important; font-size: 13px !important; }

.stSuccess > div { background: #0F4A2A !important; border: 1px solid #4EC9BB !important; color: #A0FFD0 !important; font-weight: 500 !important; border-radius: 8px !important; }
.stError > div { background: #4A0F0F !important; border: 1px solid #F09595 !important; color: #FFB0B0 !important; font-weight: 500 !important; border-radius: 8px !important; }
.stWarning > div { background: #3A2A00 !important; border: 1px solid #E8B84B !important; color: #FFE8A0 !important; font-weight: 500 !important; border-radius: 8px !important; }
.stInfo > div { background: #0F2A4A !important; border: 1px solid #7AB8E8 !important; color: #B0D8FF !important; font-weight: 500 !important; border-radius: 8px !important; }

hr { border-color: #C8922A55 !important; }

.alula-card { background: #2A1E0F; border: 1px solid #C8922A55; border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 12px; }
.alula-card h4 { color: #E8B84B !important; margin: 0 0 6px; font-size: 16px; }
.alula-card p { color: #C8A870 !important; margin: 0; font-size: 13px; }

.role-card {
    background: #2A1E0F; border: 2px solid #C8922A55;
    border-radius: 16px; padding: 2rem 1.5rem; text-align: center;
    cursor: pointer; transition: border 0.2s;
}
.role-card:hover { border-color: #E8B84B; }
.role-card h3 { color: #E8B84B !important; margin: 0.5rem 0; font-size: 20px; }
.role-card p { color: #C8A870 !important; font-size: 13px; margin: 0; }
.role-icon { font-size: 40px; margin-bottom: 8px; }

.receipt-box { background: #0F0A05; border: 2px solid #C8922A; border-radius: 12px; padding: 1.8rem; max-width: 420px; }
.receipt-box h3 { color: #E8B84B !important; text-align: center; margin-bottom: 1.2rem; font-size: 18px; }
.receipt-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2A1E0F; }
.receipt-label { color: #9A8B72 !important; font-size: 13px; }
.receipt-value { color: #E8D5A0 !important; font-size: 13px; font-weight: 600; }
.receipt-id { color: #E8B84B !important; font-size: 20px !important; font-weight: 700 !important; }

.booking-row { background: #2A1E0F; border: 1px solid #C8922A55; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
.booking-site { color: #E8B84B !important; font-weight: 600; font-size: 14px; }
.booking-id { color: #C8A870 !important; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
if "manager" not in st.session_state:
    st.session_state.manager = Manager()
if "role" not in st.session_state:
    st.session_state.role = None
if "logged_in_guide" not in st.session_state:
    st.session_state.logged_in_guide = None
if "logged_in_visitor" not in st.session_state:
    st.session_state.logged_in_visitor = None

manager = st.session_state.manager

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏛️ AlUla Tourism")
    st.markdown("---")

    if st.session_state.role is None:
        st.markdown("### Select your role")
        if st.button("🏢  Manager", use_container_width=True):
            st.session_state.role = "manager"
            st.session_state.manager_page = "summary"
            st.rerun()
        if st.button("🧭  Guide", use_container_width=True):
            st.session_state.role = "guide"
            st.rerun()
        if st.button("🎟️  Visitor", use_container_width=True):
            st.session_state.role = "visitor"
            st.rerun()
    else:
        st.markdown(f"### {st.session_state.role.capitalize()}")
        st.markdown("---")

        if st.session_state.role == "manager":
            if st.button("📊  Summary", use_container_width=True):
                st.session_state.manager_page = "summary"
                st.rerun()
            if st.button("🗺️  Sites", use_container_width=True):
                st.session_state.manager_page = "sites"
                st.rerun()
            if st.button("🧭  Guides", use_container_width=True):
                st.session_state.manager_page = "guides"
                st.rerun()

        elif st.session_state.role == "guide":
            if st.session_state.logged_in_guide:
                st.markdown(f"**Welcome, {st.session_state.logged_in_guide.name}!**")
                st.markdown("---")
                if st.button("🗺️  My sites", use_container_width=True):
                    st.session_state.guide_page = "sites"
                    st.rerun()
                if st.button("👥  My visitors", use_container_width=True):
                    st.session_state.guide_page = "visitors"
                    st.rerun()

        elif st.session_state.role == "visitor":
            if st.session_state.logged_in_visitor:
                st.markdown(f"**{st.session_state.logged_in_visitor.name}**")
                st.markdown("---")
                if st.button("🔍  Browse sites", use_container_width=True):
                    st.session_state.visitor_page = "browse"
                    st.rerun()
                if st.button("🎟️  My bookings", use_container_width=True):
                    st.session_state.visitor_page = "bookings"
                    st.rerun()

        st.markdown("---")
        if st.button("🔙  Back to home", use_container_width=True):
            st.session_state.role = None
            st.session_state.logged_in_guide = None
            st.session_state.logged_in_visitor = None
            st.rerun()

# ─── Home ─────────────────────────────────────────────────────────────────────
if st.session_state.role is None:
    st.markdown("# 🏛️ AlUla Tourism System")
    st.markdown("##### Welcome — select your role to get started")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="role-card"><div class="role-icon">🏢</div><h3>Manager</h3><p>Manage sites, assign guides and view system summary</p></div>', unsafe_allow_html=True)
        if st.button("Enter as Manager", use_container_width=True, key="home_manager"):
            st.session_state.role = "manager"
            st.session_state.manager_page = "summary"
            st.rerun()
    with col2:
        st.markdown('<div class="role-card"><div class="role-icon">🧭</div><h3>Guide</h3><p>Login to view your assigned sites and visitors</p></div>', unsafe_allow_html=True)
        if st.button("Enter as Guide", use_container_width=True, key="home_guide"):
            st.session_state.role = "guide"
            st.rerun()
    with col3:
        st.markdown('<div class="role-card"><div class="role-icon">🎟️</div><h3>Visitor</h3><p>Browse open sites and register for a visit</p></div>', unsafe_allow_html=True)
        if st.button("Enter as Visitor", use_container_width=True, key="home_visitor"):
            st.session_state.role = "visitor"
            st.rerun()

# ─── Manager ──────────────────────────────────────────────────────────────────
elif st.session_state.role == "manager":
    if "manager_page" not in st.session_state:
        st.session_state.manager_page = "summary"
    page = st.session_state.manager_page

    if page == "summary":
        st.markdown("# 📊 Summary")
        total_sites = len(manager.sites)
        total_visitors = sum(site["visitors"] for site in manager.sites)
        most_visited = max(manager.sites, key=lambda site: site["visitors"], default=None)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total sites", total_sites)
        col2.metric("Total visitors", total_visitors)
        col3.metric("Most visited", most_visited["name"] if most_visited and most_visited["visitors"] > 0 else "—")
        st.markdown("---")
        st.markdown("#### Available guides")
        if manager.guide:
            for g in manager.guide.values():
                st.markdown(f"- **{g.name}** — ID: `{g.guide_id}` — {len(g.assigned_sites)} site(s)")
        else:
            st.info("No guides added yet.")

    elif page == "sites":
        st.markdown("# 🗺️ Sites")
        tab1, tab2, tab3 = st.tabs(["All sites", "Add site", "Assign / Close"])

        with tab1:
            if not manager.sites:
                st.info("No sites added yet.")
            else:
                for site in manager.sites:
                    guide_name = manager.guide[site["guide_id"]].name if site["guide_id"] and site["guide_id"] in manager.guide else "N/A"
                    badge = "🟢 Open" if site["status"] == "Open" else "🔴 Closed"
                    st.markdown(f'<div class="alula-card"><h4>{site["name"]} &nbsp; {badge}</h4><p>Type: {site["type"]} &nbsp;|&nbsp; Visitors: {site["visitors"]}/{site["capacity"]} &nbsp;|&nbsp; Guide: {guide_name}</p></div>', unsafe_allow_html=True)

        with tab2:
            st.markdown("#### Add a new site")
            col1, col2 = st.columns(2)
            with col1:
                site_name = st.text_input("Site name")
                site_type = st.text_input("Site type")
            with col2:
                capacity = st.number_input("Max capacity", min_value=1, value=50)
                guide_options = ["None"] + [f"{g.name} (ID: {gid})" for gid, g in manager.guide.items()]
                guide_choice = st.selectbox("Assign guide (optional)", guide_options)
            if st.button("✅ Add site"):
                if not site_name:
                    st.error("❌ Please enter a site name.")
                elif manager.site_exists(site_name):
                    st.error(f"❌ Site '{site_name}' already exists.")
                else:
                    guide_id = None
                    if guide_choice != "None":
                        guide_id = int(guide_choice.split("ID: ")[1].replace(")", ""))
                    manager.add_site(site_name, site_type, capacity, guide_id)
                    st.success(f"✅ Site '{site_name}' added successfully!")
                    st.rerun()

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Assign a guide")
                if manager.sites and manager.guide:
                    sel_site = st.selectbox("Select site", [s["name"] for s in manager.sites], key="assign_site")
                    sel_guide = st.selectbox("Select guide", [f"{g.name} (ID: {gid})" for gid, g in manager.guide.items()], key="assign_guide_sel")
                    if st.button("✅ Assign guide"):
                        guide_id = int(sel_guide.split("ID: ")[1].replace(")", ""))
                        manager.assign_guide(sel_site, guide_id)
                        st.success(f"✅ Guide '{manager.guide[guide_id].name}' assigned to '{sel_site}'!")
                        st.rerun()
                else:
                    st.info("Need at least one site and one guide.")
            with col2:
                st.markdown("#### Close a site")
                open_sites = [s["name"] for s in manager.sites if s["status"] == "Open"]
                if open_sites:
                    sel_close = st.selectbox("Select site to close", open_sites, key="close_site")
                    if st.button("🔴 Close site"):
                        manager.close_site(sel_close)
                        st.success(f"✅ Site '{sel_close}' is now closed.")
                        st.rerun()
                else:
                    st.info("No open sites to close.")

    elif page == "guides":
        st.markdown("# 🧭 Guides")
        tab1, tab2 = st.tabs(["All guides", "Add guide"])
        with tab1:
            if not manager.guide:
                st.info("No guides added yet.")
            else:
                for gid, g in manager.guide.items():
                    sites_str = ", ".join(g.assigned_sites) if g.assigned_sites else "None"
                    st.markdown(f'<div class="alula-card"><h4>{g.name} &nbsp; <small style="color:#C8A870">ID: {gid}</small></h4><p>Assigned sites: {sites_str}</p></div>', unsafe_allow_html=True)
        with tab2:
            st.markdown("#### Add a new guide")
            st.info("ℹ️ Guide ID will be generated automatically.")
            guide_name = st.text_input("Guide name")
            if st.button("✅ Add guide"):
                if not guide_name:
                    st.error("❌ Please enter a guide name.")
                else:
                    new_id = manager.add_new_Guide(guide_name)
                    st.success(f"✅ Guide '{guide_name}' added with ID: `{new_id}`")
                    st.rerun()

# ─── Guide ────────────────────────────────────────────────────────────────────
elif st.session_state.role == "guide":
    if not st.session_state.logged_in_guide:
        st.markdown("# 🧭 Guide Login")
        guide_id_input = st.number_input("Guide ID", min_value=1000, max_value=9999, value=1000)
        if st.button("🔐 Login"):
            found = None
            for g in manager.guide.values():
                if g.login(int(guide_id_input)):
                    found = g
                    break
            if found:
                st.session_state.logged_in_guide = found
                st.session_state.guide_page = "sites"
                st.success(f"✅ Welcome, {found.name}!")
                st.rerun()
            else:
                st.error("❌ Guide ID not found.")
    else:
        guide = st.session_state.logged_in_guide
        if "guide_page" not in st.session_state:
            st.session_state.guide_page = "sites"

        if st.session_state.guide_page == "sites":
            st.markdown(f"# 🗺️ My assigned sites")
            if not guide.assigned_sites:
                st.info("You are not assigned to any sites yet.")
            else:
                for site_name in guide.assigned_sites:
                    for site in manager.sites:
                        if site["name"] == site_name:
                            badge = "🟢 Open" if site["status"] == "Open" else "🔴 Closed"
                            st.markdown(f'<div class="alula-card"><h4>{site["name"]} &nbsp; {badge}</h4><p>Type: {site["type"]} &nbsp;|&nbsp; Visitors: {site["visitors"]}/{site["capacity"]}</p></div>', unsafe_allow_html=True)

        elif st.session_state.guide_page == "visitors":
            st.markdown(f"# 👥 My visitors")
            results = manager.view_visitors_by_guide(guide.guide_id)
            if not results:
                st.info("No visitors registered for your sites.")
            else:
                for r in results:
                    st.markdown(f'<div class="alula-card"><h4>{r["site"]}</h4><p>Registered visitors: {r["visitors"]}</p></div>', unsafe_allow_html=True)

# ─── Visitor ──────────────────────────────────────────────────────────────────
elif st.session_state.role == "visitor":
    if not st.session_state.logged_in_visitor:
        st.markdown("# 🎟️ Visitor")
        tab1, tab2 = st.tabs(["Login", "Create account"])

        with tab1:
            st.markdown("#### Login to your account")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("🔐 Login"):
                if not username or not password:
                    st.error("❌ Please fill in all fields.")
                elif not manager.visitor_exists(username):
                    st.error("❌ Username not found. Please create an account.")
                else:
                    visitor = manager.visitors[username]
                    if visitor.login(username, password):
                        st.session_state.logged_in_visitor = visitor
                        st.session_state.visitor_page = "browse"
                        st.success(f"✅ Welcome back, {visitor.name}!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password.")

        with tab2:
            st.markdown("#### Create a new account")
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full name", key="reg_name")
                new_username = st.text_input("Username", key="reg_username")
            with col2:
                new_nationality = st.text_input("Nationality", key="reg_nationality")
                new_password = st.text_input("Password", type="password", key="reg_password")
            if st.button("✅ Create account"):
                if not new_name or not new_username or not new_nationality or not new_password:
                    st.error("❌ Please fill in all fields.")
                elif manager.visitor_exists(new_username):
                    st.error(f"❌ Username '{new_username}' is already taken.")
                else:
                    manager.add_new_visitor(new_name, new_nationality, new_username, new_password)
                    st.success(f"✅ Account created! Welcome, {new_name}! You can now login.")
    else:
        visitor = st.session_state.logged_in_visitor
        if "visitor_page" not in st.session_state:
            st.session_state.visitor_page = "browse"

        if st.session_state.visitor_page == "browse":
            st.markdown("# 🔍 Open sites")
            open_sites = manager.view_open_sites()
            if not open_sites:
                st.info("No open sites available right now.")
            else:
                for site in open_sites:
                    guide_name = manager.guide[site["guide_id"]].name if site["guide_id"] and site["guide_id"] in manager.guide else "N/A"
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f'<div class="alula-card"><h4>{site["name"]}</h4><p>Type: {site["type"]} &nbsp;|&nbsp; Guide: {guide_name} &nbsp;|&nbsp; Visitors: {site["visitors"]}/{site["capacity"]}</p></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                        if st.button("Register", key=f"reg_{site['name']}"):
                            success, result = manager.register_visitor(visitor, site["name"])
                            if success:
                                st.success(f"✅ Registered! Booking ID: `{result}`")
                                st.rerun()
                            else:
                                st.error(f"❌ {result}")
                        st.markdown("</div>", unsafe_allow_html=True)

        elif st.session_state.visitor_page == "bookings":
            st.markdown("# 🎟️ My bookings")
            if not visitor.bookings:
                st.info("You have no active bookings.")
            else:
                for b in visitor.bookings:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="receipt-box" style="max-width:100%; padding:1rem;">
                            <div class="receipt-row">
                                <span class="receipt-label">Site</span>
                                <span class="receipt-value">{b['site_name']}</span>
                            </div>
                            <div class="receipt-row">
                                <span class="receipt-label">Booking ID</span>
                                <span class="receipt-id">{b['booking_id']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                        if st.button("Cancel", key=f"cancel_{b['booking_id']}"):
                            success, msg = manager.cancel_registration(visitor, b["booking_id"])
                            if success:
                                st.success(f"✅ {msg}")
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                        st.markdown("</div>", unsafe_allow_html=True)
