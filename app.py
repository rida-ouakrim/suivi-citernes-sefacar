import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as io
from datetime import datetime
import io as python_io
import os
import db

# Streamlit Page Config
st.set_page_config(
    page_title="SEFACAR — Suivi des Citernes",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Database if not already done
db.create_tables()

# Custom Responsive Mobile-First CSS
st.markdown("""
<style>
    /* Main Background & Base Font */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Remove default Streamlit top padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
    /* Mobile-Optimized KPI Cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 12px 8px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        margin-bottom: 8px;
    }
    .kpi-title {
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 800;
        margin-top: 2px;
    }
    
    /* Status Badges */
    .badge-finished {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 700;
    }
    .badge-in-progress {
        background-color: #fef3c7;
        color: #b45309;
        border: 1px solid #fde047;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 700;
    }
    .badge-not-started {
        background-color: #f1f5f9;
        color: #64748b;
        border: 1px solid #cbd5e1;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 700;
    }
    
    /* Mobile Tank Card Header */
    .tank-tour-header {
        background-color: #ffffff;
        padding: 10px 14px;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* Touch-Friendly Large Buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 14px;
        min-height: 44px;
    }
    
    /* Touch Form Submit Button Primary Styling */
    div.stFormSubmitButton > button {
        background-color: #1e40af !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 14px !important;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.25) !important;
    }

    /* Expanders Padding on Mobile */
    .stExpander {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
        margin-bottom: 8px !important;
    }

    /* Titles styling */
    h3 {
        font-size: 18px !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    h4 {
        font-size: 15px !important;
    }

    /* ==========================================
       EXCEL MATRIX DISPLAY STYLES
       ========================================== */
    .matrix-container {
        overflow-x: auto;
        max-width: 100%;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .excel-table {
        border-collapse: collapse;
        font-family: 'Calibri', 'Arial', sans-serif;
        font-size: 10.5px;
        width: 100%;
    }
    .excel-table th, .excel-table td {
        border: 1px solid #cbd5e1;
        padding: 4px 6px;
        text-align: center;
        vertical-align: middle;
        white-space: nowrap;
    }
    .excel-table th {
        background-color: #f8fafc;
        color: #0f172a;
        font-weight: bold;
    }
    
    /* Sticky Left Columns for Scrolling */
    .excel-table .sticky-col-1 {
        position: sticky;
        left: 0;
        background-color: #f8fafc !important;
        z-index: 10;
        border-right: 2px solid #94a3b8 !important;
        min-width: 140px;
        max-width: 150px;
        text-align: left;
        font-weight: normal;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .excel-table .sticky-col-2 {
        position: sticky;
        left: 140px; /* Col 1 width */
        background-color: #f1f5f9 !important;
        z-index: 10;
        border-right: 3px solid #1e40af !important;
        font-weight: bold;
        min-width: 80px;
        max-width: 80px;
        color: #1e40af;
    }
    
    /* Z-Indices for Headers & Body */
    .excel-table thead tr th {
        position: sticky;
        top: 0;
        background-color: #f8fafc;
        z-index: 5;
    }
    
    /* Sticky Intersection Header Cells */
    .excel-table thead tr th.sticky-col-1 {
        z-index: 25;
    }
    .excel-table thead tr th.sticky-col-2 {
        z-index: 25;
        border-right: 3px solid #1e40af !important;
    }
    
    /* Hover and general highlights */
    .excel-table tbody tr:hover td {
        filter: brightness(0.97);
    }
    .excel-table tbody tr:hover td.sticky-col-1,
    .excel-table tbody tr:hover td.sticky-col-2 {
        background-color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Authentication Function (100% Hidden from GitHub)
def check_password():
    if st.session_state.get("authenticated"):
        return True

    valid_passwords = []
    env_pwd = os.environ.get("APP_PASSWORD")
    if env_pwd:
        for p in env_pwd.split(","):
            if p.strip():
                valid_passwords.append(p.strip().upper())
                
    try:
        if "APP_PASSWORD" in st.secrets:
            sec_pwd = str(st.secrets["APP_PASSWORD"])
            for p in sec_pwd.split(","):
                if p.strip():
                    valid_passwords.append(p.strip().upper())
    except Exception:
        pass

    valid_passwords = list(set(valid_passwords))

    st.markdown("""
    <div style="max-width: 420px; margin: 20px auto; background: #ffffff; border: 1px solid #e2e8f0; border-top: 6px solid #1e40af; border-radius: 12px; padding: 24px 20px; text-align: center; box-shadow: 0 6px 18px rgba(0,0,0,0.05);">
        <h2 style="color: #0f172a; margin-bottom: 2px; font-size: 22px;">🚛 SEFACAR</h2>
        <h4 style="color: #1e40af; font-size: 14px; margin-top: 0;">Suivi de Production des Citernes</h4>
        <hr style="margin: 15px 0; border-color: #f1f5f9;">
        <p style="color: #64748b; font-size: 12px; margin-bottom: 12px;">Entrez votre code d'accès pour commencer la tournée.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 10, 1])
    with c2:
        with st.form("login_form_mobile", clear_on_submit=False):
            pwd_input = st.text_input(
                "🔑 Code d'Accès",
                type="password",
                placeholder="Code d'accès...",
                label_visibility="collapsed"
            )
            submit_btn = st.form_submit_button("🔓 Se Connecter", use_container_width=True)
            
            if submit_btn or pwd_input:
                user_val = pwd_input.strip().upper() if pwd_input else ""
                if user_val and user_val in valid_passwords:
                    st.session_state["authenticated"] = True
                    st.rerun()
                elif submit_btn:
                    st.error("❌ Code d'accès incorrect.")
    return False

if not check_password():
    st.stop()

# Sidebar Navigation
st.sidebar.markdown("<h2 style='color: #1e40af; font-size: 18px;'>Navigation</h2>", unsafe_allow_html=True)
mode = st.sidebar.radio(
    "Module :",
    [
        "📱 Mode Tournée (Terrain)",
        "📊 Tableau de Bord (Admin)",
        "📥 Exportation & Rapport du Jour",
        "⚙️ Configuration & Synchro"
    ]
)

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Déconnexion", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.markdown("<div style='font-size: 11px; color: #64748b; margin-top: 15px;'><b>SEFACAR v2.0 Mobile Optimized</b></div>", unsafe_allow_html=True)

# ==========================================
# MODULE 1: MODE TOURNÉE (TERRAIN / MOBILE)
# ==========================================
if mode == "📱 Mode Tournée (Terrain)":
    # Touch-Friendly Segmented Selector for Citerne Type (Placed at the very top)
    type_citerne_raw = st.radio(
        "Type de Citerne :",
        ["⛽ CARBURANT", "💧 EAU"],
        horizontal=True,
        key="tour_type_radio"
    )
    type_citerne = "CARBURANT" if "CARBURANT" in type_citerne_raw else "EAU"
    
    col_filters1, col_filters2 = st.columns([1, 1])
    with col_filters1:
        statut_filter = st.selectbox("Statut", ["Tous", "En cours", "Non commencé", "Terminé"], key="tour_statut")
    with col_filters2:
        search_query = st.text_input("🔍 Rechercher Code", placeholder="ex: CC11", key="tour_search")
        
    df_citernes = db.get_summary_dataframe(type_citerne)
    
    if statut_filter != "Tous":
        df_citernes = df_citernes[df_citernes['statut'] == statut_filter]
    if search_query:
        df_citernes = df_citernes[df_citernes['code'].str.contains(search_query.strip(), case=False)]
        
    citerne_codes = df_citernes['code'].tolist()
    
    if not citerne_codes:
        st.warning("⚠️ Aucune citerne trouvée.")
    else:
        selected_code = st.selectbox(
            f"📋 Citerne à inspecter ({len(citerne_codes)}) :",
            citerne_codes,
            key="selected_citerne_code"
        )
        
        if selected_code:
            citerne_info = db.get_citerne_details(selected_code)
            progress_df = db.get_citerne_progress(selected_code)
            
            total_cadence = progress_df['cadence_hours'].sum()
            completed_weighted = (progress_df['completion_pct'] / 100.0 * progress_df['cadence_hours']).sum()
            global_pct = round((completed_weighted / total_cadence * 100.0) if total_cadence > 0 else 0, 1)
            
            if global_pct >= 99.9:
                badge_html = '<span class="badge-finished">Terminé (100%)</span>'
            elif global_pct > 0:
                badge_html = f'<span class="badge-in-progress">En cours ({global_pct}%)</span>'
            else:
                badge_html = '<span class="badge-not-started">Non commencé (0%)</span>'
                
            st.markdown(f"""
            <div class="tank-tour-header">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="font-size: 20px; font-weight: 800; color: #0f172a;">{selected_code}</span>
                        <span style="font-size: 12px; color: #64748b; margin-left: 6px;">({type_citerne})</span>
                    </div>
                    <div>
                        {badge_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(global_pct / 100.0)
            
            # General Comment Section
            current_citerne_comment = citerne_info.get('comments', '') or ''
            with st.expander("💬 Remarques / Observations sur la Citerne", expanded=bool(current_citerne_comment)):
                new_citerne_comment = st.text_area(
                    "Note générale",
                    value=current_citerne_comment,
                    placeholder="Ex: Fin séchage prévue le 22/07...",
                    key=f"citerne_comment_{selected_code}",
                    label_visibility="collapsed"
                )
                if new_citerne_comment != current_citerne_comment:
                    if st.button("💾 Enregistrer la note", key="save_citerne_comment", use_container_width=True):
                        db.update_citerne_comment(selected_code, new_citerne_comment)
                        st.toast(f"✅ Note enregistrée pour {selected_code} !", icon="💾")
                        st.rerun()
                    
            st.markdown("#### 🛠️ Étapes de Fabrication")
            
            categories = progress_df['category'].unique()
            
            with st.form(key=f"form_progress_{selected_code}"):
                top_save = st.form_submit_button("🚀 Enregistrer la Tournée (Haut)", use_container_width=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                step_updates = {}
                
                for cat in categories:
                    cat_steps = progress_df[progress_df['category'] == cat]
                    cat_avg_pct = round(cat_steps['completion_pct'].mean(), 1)
                    
                    # Category Expander
                    with st.expander(f"📁 **{cat}** — {cat_avg_pct}%", expanded=False):
                        for _, step_row in cat_steps.iterrows():
                            s_id = step_row['step_id']
                            s_name = step_row['step_name']
                            s_cadence = step_row['cadence_hours']
                            s_pct = float(step_row['completion_pct'])
                            s_comment = str(step_row['step_comment']) if step_row['step_comment'] else ""
                            
                            st.markdown(f"**{s_name}** <span style='font-size:11px; color:#64748b;'>({s_cadence}h)</span>", unsafe_allow_html=True)
                            
                            # Touch-optimized Select Slider with discrete percentage points
                            preset_options = [0.0, 25.0, 50.0, 75.0, 100.0]
                            closest_val = min(preset_options, key=lambda x: abs(x - s_pct))
                            
                            c_slider, c_note = st.columns([3, 2])
                            with c_slider:
                                new_pct = st.select_slider(
                                    f"Pct {s_name}",
                                    options=[0.0, 25.0, 50.0, 75.0, 100.0],
                                    value=closest_val,
                                    key=f"select_slider_{selected_code}_{s_id}",
                                    format_func=lambda x: f"{int(x)}%",
                                    label_visibility="collapsed"
                                )
                            with c_note:
                                new_note = st.text_input(
                                    f"Note {s_name}",
                                    value=s_comment,
                                    placeholder="Note...",
                                    key=f"note_{selected_code}_{s_id}",
                                    label_visibility="collapsed"
                                )
                                
                            step_updates[s_id] = (new_pct, new_note)
                            st.markdown("<hr style='margin: 6px 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)
                            
                bottom_save = st.form_submit_button("🚀 Enregistrer la Tournée", use_container_width=True)
                
                if top_save or bottom_save:
                    for s_id, (u_pct, u_note) in step_updates.items():
                        db.update_step_progress(selected_code, s_id, u_pct, u_note)
                    if 'new_citerne_comment' in locals() and new_citerne_comment != current_citerne_comment:
                        db.update_citerne_comment(selected_code, new_citerne_comment)
                    st.toast(f"🎉 Modifications enregistrées avec succès pour {selected_code} !", icon="✅")
                    st.rerun()

# ==========================================
# MODULE 2: TABLEAU DE BORD (ADMINISTRATION)
# ==========================================
elif mode == "📊 Tableau de Bord (Admin)":
    st.markdown("### 📊 Tableau de Bord Administration")
    
    admin_type = st.selectbox("Type", ["TOUS", "CARBURANT", "EAU"], key="admin_type_select")
    filter_type = None if admin_type == "TOUS" else admin_type
    
    df_summary = db.get_summary_dataframe(filter_type)
    
    total_count = len(df_summary)
    completed_count = len(df_summary[df_summary['statut'] == 'Terminé'])
    in_progress_count = len(df_summary[df_summary['statut'] == 'En cours'])
    not_started_count = len(df_summary[df_summary['statut'] == 'Non commencé'])
    avg_global_pct = round(df_summary['global_pct'].mean(), 1) if total_count > 0 else 0.0
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
    with col_kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Citernes</div>
            <div class="kpi-value" style="color: #0f172a;">{total_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Terminées</div>
            <div class="kpi-value" style="color: #16a34a;">{completed_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">En Cours</div>
            <div class="kpi-value" style="color: #d97706;">{in_progress_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Non Commencées</div>
            <div class="kpi-value" style="color: #64748b;">{not_started_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avancement Moyen</div>
            <div class="kpi-value" style="color: #1e40af;">{avg_global_pct}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 📉 Avancement Moyen par Phase")
        target_type = "CARBURANT" if admin_type == "TOUS" else admin_type
        df_cat = db.get_category_progress_df(target_type)
        
        fig_cat = px.bar(
            df_cat,
            x="weighted_completion",
            y="category",
            orientation="h",
            labels={"weighted_completion": "Avancement (%)", "category": "Phase"},
            color="weighted_completion",
            color_continuous_scale="Blues",
            text_auto=".1f"
        )
        fig_cat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            xaxis=dict(range=[0, 100]),
            margin=dict(l=0, r=0, t=20, b=0),
            height=340
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### 🍰 Répartition par Statut")
        statut_counts = df_summary['statut'].value_counts().reset_index()
        statut_counts.columns = ['Statut', 'Nombre']
        
        fig_pie = px.pie(
            statut_counts,
            names="Statut",
            values="Nombre",
            color="Statut",
            color_discrete_map={
                "Terminé": "#16a34a",
                "En cours": "#d97706",
                "Non commencé": "#94a3b8"
            },
            hole=0.4
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            margin=dict(l=0, r=0, t=20, b=0),
            height=340
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    
    # Tabs for different administrative views
    tab_summary, tab_matrix = st.tabs(["📋 Liste & Résumés", "🔲 Matrice d'Avancement (Vue Atelier)"])
    
    with tab_summary:
        st.markdown("#### 📋 Liste d'Avancement des Citernes")
        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            filter_status_table = st.selectbox("Statut", ["Tous", "En cours", "Non commencé", "Terminé"], key="table_status_filter")
        with col_t2:
            search_table = st.text_input("🔍 Rechercher", key="table_search")
            
        df_table_display = df_summary.copy()
        if filter_status_table != "Tous":
            df_table_display = df_table_display[df_table_display['statut'] == filter_status_table]
        if search_table:
            df_table_display = df_table_display[df_table_display['code'].str.contains(search_table.strip(), case=False)]
            
        df_table_display = df_table_display[['code', 'type', 'statut', 'global_pct', 'completed_hours', 'total_cadence', 'comments', 'updated_at']]
        df_table_display.columns = ['Code Citerne', 'Type', 'Statut', 'Avancement (%)', 'Heures Complétées', 'Total Cadence (h)', 'Observations', 'Dernière Maj']
        
        st.dataframe(
            df_table_display,
            use_container_width=True,
            column_config={
                "Avancement (%)": st.column_config.ProgressColumn(
                    "Avancement (%)",
                    help="Pourcentage global d'avancement pondéré",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True
        )

    with tab_matrix:
        st.markdown("#### 🔲 Matrice d'Avancement Réal-Time (Vue Atelier)")
        st.caption("Vue matricielle dynamique identique à l'Excel avec en-têtes imbriqués et colonnes de gauche figées (faites défiler vers la droite).")
        
        matrix_type = st.radio("Afficher la matrice pour :", ["⛽ CARBURANT", "💧 EAU"], horizontal=True, key="matrix_type_radio")
        selected_matrix_type = "CARBURANT" if "CARBURANT" in matrix_type else "EAU"
        
        # Render the custom Excel-like styled HTML grid
        html_view = db.get_html_matrix_view(selected_matrix_type)
        st.markdown(html_view, unsafe_allow_html=True)

# ==========================================
# MODULE 3: EXPORTATION & RAPPORT DU JOUR
# ==========================================
elif mode == "📥 Exportation & Rapport du Jour":
    st.markdown("### 📥 Exportation & Rapport de l'État du Jour")
    st.caption("Générez et téléchargez le rapport d'avancement quotidien au format Excel (.xlsx) pour l'administration.")
    
    export_type = st.radio("Type à Exporter :", ["TOUS (Carburant & Eau)", "CARBURANT uniquement", "EAU uniquement"], horizontal=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("📊 Générer le Rapport Excel Complet", use_container_width=True):
        type_code = "TOUS"
        if export_type == "CARBURANT uniquement":
            type_code = "CARBURANT"
        elif export_type == "EAU uniquement":
            type_code = "EAU"
            
        with st.spinner("Génération du rapport Excel avec styles et cadences..."):
            excel_data = db.generate_styled_excel_report(type_code)
            
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_name = f"SEFACAR_Suivi_Citernes_Etat_du_{date_str}.xlsx"
        
        st.download_button(
            label=f"💾 Télécharger {file_name}",
            data=excel_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.success("✅ Rapport Excel généré avec succès !")
        
    st.markdown("---")
    st.markdown("#### 👁️ Aperçu Synthèse")
    filter_t = None if export_type == "TOUS (Carburant & Eau)" else ("CARBURANT" if "CARBURANT" in export_type else "EAU")
    preview_df = db.get_summary_dataframe(filter_t)
    st.dataframe(preview_df, use_container_width=True, hide_index=True)

# ==========================================
# MODULE 4: CONFIGURATION & SYNCHRO
# ==========================================
elif mode == "⚙️ Configuration & Synchro":
    st.markdown("### ⚙️ Configuration & Synchronisation")
    
    if st.button("🔄 Lancer la Synchronisation / Réinitialisation", key="reset_db_btn", use_container_width=True):
        import init_db
        with st.spinner("Rechargement des données depuis Excel..."):
            init_db.init_database_from_excel(force=True)
        st.success("🎉 Base de données réinitialisée avec succès !")
        st.rerun()
        
    st.markdown("---")
    conn = db.get_connection()
    citerne_count = conn.execute("SELECT COUNT(*) FROM citernes").fetchone()[0]
    etape_count = conn.execute("SELECT COUNT(*) FROM etapes").fetchone()[0]
    progress_count = conn.execute("SELECT COUNT(*) FROM suivi_progress").fetchone()[0]
    conn.close()
    
    st.json({
        "Application": "SEFACAR Mobile Optimized v2.0",
        "Total Citernes": citerne_count,
        "Total Étapes Cataloguées": etape_count,
        "Total Enregistrements": progress_count,
        "Dernière Maj": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
