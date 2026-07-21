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
    initial_sidebar_state="expanded"
)

# Initialize Database if not already done
db.create_tables()

# Custom CSS for Light SEFACAR Executive Theme
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Header Card */
    .header-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #1e40af;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .header-title {
        color: #0f172a;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .header-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-top: 4px;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .kpi-title {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        margin-top: 6px;
    }
    
    /* Status Badges */
    .badge-finished {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-in-progress {
        background-color: #fef3c7;
        color: #b45309;
        border: 1px solid #fde047;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-not-started {
        background-color: #f1f5f9;
        color: #64748b;
        border: 1px solid #cbd5e1;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    
    /* Tour Card */
    .tank-tour-header {
        background-color: #ffffff;
        padding: 15px 20px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    div.stButton > button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Authentication Function
def check_password():
    if st.session_state.get("authenticated"):
        return True

    correct_password = os.environ.get("APP_PASSWORD", "MAN2026").strip()
    try:
        if "APP_PASSWORD" in st.secrets:
            correct_password = str(st.secrets["APP_PASSWORD"]).strip()
    except Exception:
        pass

    st.markdown("""
    <div style="max-width: 480px; margin: 40px auto 20px auto; background: #ffffff; border: 1px solid #e2e8f0; border-top: 6px solid #1e40af; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.06);">
        <h2 style="color: #0f172a; margin-bottom: 4px; font-size: 26px;">🚛 SEFACAR</h2>
        <h4 style="color: #1e40af; font-size: 15px; margin-top: 0;">Plateforme de Suivi des Citernes</h4>
        <hr style="margin: 20px 0; border-color: #f1f5f9;">
        <p style="color: #64748b; font-size: 13px; margin-bottom: 10px;">Veuillez entrer le code d'accès sécurisé pour accéder au système.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        pwd_input = st.text_input(
            "🔑 Code d'Accès",
            type="password",
            key="login_pwd_val",
            placeholder="Code d'accès...",
            label_visibility="collapsed"
        )
        if st.button("🔓 Connexion", use_container_width=True):
            if pwd_input and pwd_input.strip() == correct_password:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Code d'accès incorrect. Veuillez réessayer.")
    return False

if not check_password():
    st.stop()

# Application Header
st.markdown("""
<div class="header-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 class="header-title">🚛 SEFACAR — Suivi de Production des Citernes</h1>
            <div class="header-subtitle">Digitalisation du suivi terrain en temps réel & tableau de bord administratif</div>
        </div>
        <div style="text-align: right; font-size: 12px; color: #1e40af; font-weight: 600; background: #eff6ff; padding: 6px 14px; border-radius: 20px; border: 1px solid #bfdbfe;">
            ⚡ Synchro Temps Réel Active
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("<h2 style='color: #1e40af; font-size: 18px;'>Navigation</h2>", unsafe_allow_html=True)
mode = st.sidebar.radio(
    "Choisissez un module :",
    [
        "📱 Mode Tournée (Terrain)",
        "📊 Tableau de Bord (Administration)",
        "📥 Exportation & Rapport du Jour",
        "⚙️ Configuration & Synchro"
    ]
)

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Déconnexion", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.markdown("<div style='font-size: 12px; color: #64748b; margin-top: 15px;'><b>SEFACAR v2.0 Light Edition</b><br>Gestionnaire de Suivi des Citernes</div>", unsafe_allow_html=True)

# ==========================================
# MODULE 1: MODE TOURNÉE (TERRAIN / MOBILE)
# ==========================================
if mode == "📱 Mode Tournée (Terrain)":
    st.markdown("### 📱 Mode Tournée — Saisie Rapide de Progression")
    st.caption("Sélectionnez une citerne pour mettre à jour l'avancement de chaque étape et enregistrer vos observations.")
    
    col_filters1, col_filters2, col_filters3 = st.columns([1, 1, 2])
    with col_filters1:
        type_citerne = st.selectbox("Type de Citerne", ["CARBURANT", "EAU"], key="tour_type")
    with col_filters2:
        statut_filter = st.selectbox("Filtrer par Statut", ["Tous", "En cours", "Non commencé", "Terminé"], key="tour_statut")
    with col_filters3:
        search_query = st.text_input("🔍 Rechercher une citerne (ex: CC11, CE005)", key="tour_search")
        
    df_citernes = db.get_summary_dataframe(type_citerne)
    
    if statut_filter != "Tous":
        df_citernes = df_citernes[df_citernes['statut'] == statut_filter]
    if search_query:
        df_citernes = df_citernes[df_citernes['code'].str.contains(search_query.strip(), case=False)]
        
    citerne_codes = df_citernes['code'].tolist()
    
    if not citerne_codes:
        st.warning("⚠️ Aucune citerne ne correspond aux critères de recherche.")
    else:
        selected_code = st.selectbox(
            f"📋 Sélectionnez la Citerne ({len(citerne_codes)} disponibles) :",
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
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <h2 style="margin:0; color:#0f172a; font-size:22px;">Citerne <b>{selected_code}</b> ({type_citerne})</h2>
                        <div style="font-size:13px; color:#64748b; margin-top:4px;">Dernière mise à jour : {citerne_info.get('updated_at', 'N/A')}</div>
                    </div>
                    <div>
                        {badge_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(global_pct / 100.0)
            
            st.markdown("#### 💬 Remarques / Observations Générales sur la Citerne")
            current_citerne_comment = citerne_info.get('comments', '') or ''
            new_citerne_comment = st.text_area(
                "Commentaire Général",
                value=current_citerne_comment,
                placeholder="Ex: Fin séchage prévue le 22/07, Démontage validé par l'inspecteur...",
                key=f"citerne_comment_{selected_code}"
            )
            
            if new_citerne_comment != current_citerne_comment:
                if st.button("💾 Enregistrer le Commentaire Général", key="save_citerne_comment"):
                    db.update_citerne_comment(selected_code, new_citerne_comment)
                    st.toast(f"✅ Commentaire général enregistré pour {selected_code} !", icon="💾")
                    st.rerun()
                    
            st.markdown("---")
            st.markdown("#### 🛠️ Étapes de Fabrication & Progression")
            st.caption("Dépliez les catégories ci-dessous pour ajuster l'avancement (% ) et ajouter des notes par étape.")
            
            categories = progress_df['category'].unique()
            
            with st.form(key=f"form_progress_{selected_code}"):
                step_updates = {}
                
                for cat in categories:
                    cat_steps = progress_df[progress_df['category'] == cat]
                    cat_avg_pct = round(cat_steps['completion_pct'].mean(), 1)
                    
                    with st.expander(f"📁 **{cat}** — Progression Moyenne: {cat_avg_pct}% ({len(cat_steps)} étapes)", expanded=False):
                        for _, step_row in cat_steps.iterrows():
                            s_id = step_row['step_id']
                            s_name = step_row['step_name']
                            s_cadence = step_row['cadence_hours']
                            s_pct = float(step_row['completion_pct'])
                            s_comment = str(step_row['step_comment']) if step_row['step_comment'] else ""
                            
                            st.markdown(f"**{s_name}** *(Pondération: {s_cadence}h)*")
                            
                            c1, c2 = st.columns([3, 2])
                            with c1:
                                new_pct = st.slider(
                                    f"Avancement (%) - {s_name}",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=s_pct,
                                    step=5.0,
                                    key=f"slider_{selected_code}_{s_id}",
                                    label_visibility="collapsed"
                                )
                            with c2:
                                new_note = st.text_input(
                                    f"Note - {s_name}",
                                    value=s_comment,
                                    placeholder="Note spécifique...",
                                    key=f"note_{selected_code}_{s_id}",
                                    label_visibility="collapsed"
                                )
                                
                            step_updates[s_id] = (new_pct, new_note)
                            st.markdown("<hr style='margin: 8px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
                            
                submit_button = st.form_submit_button("🚀 Valider et Enregistrer la Tournée", use_container_width=True)
                
                if submit_button:
                    for s_id, (u_pct, u_note) in step_updates.items():
                        db.update_step_progress(selected_code, s_id, u_pct, u_note)
                    if new_citerne_comment != current_citerne_comment:
                        db.update_citerne_comment(selected_code, new_citerne_comment)
                    st.toast(f"🎉 Modifications enregistrées avec succès pour {selected_code} !", icon="✅")
                    st.rerun()

# ==========================================
# MODULE 2: TABLEAU DE BORD (ADMINISTRATION)
# ==========================================
elif mode == "📊 Tableau de Bord (Administration)":
    st.markdown("### 📊 Tableau de Bord Administration (Temps Réel)")
    st.caption("Vue globale des performances de production, suivi des citernes et détection des étapes bloquantes.")
    
    admin_type = st.selectbox("Vue par Type de Citerne", ["TOUS", "CARBURANT", "EAU"], key="admin_type_select")
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
        st.markdown("#### 📉 Avancement Moyen par Phase de Fabrication")
        target_type = "CARBURANT" if admin_type == "TOUS" else admin_type
        df_cat = db.get_category_progress_df(target_type)
        
        fig_cat = px.bar(
            df_cat,
            x="weighted_completion",
            y="category",
            orientation="h",
            labels={"weighted_completion": "Avancement Pondéré (%)", "category": "Phase / Catégorie"},
            color="weighted_completion",
            color_continuous_scale="Blues",
            text_auto=".1f"
        )
        fig_cat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            xaxis=dict(range=[0, 100]),
            margin=dict(l=0, r=0, t=30, b=0),
            height=380
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### 🍰 Répartition des Citernes par Statut")
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
            margin=dict(l=0, r=0, t=30, b=0),
            height=380
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    st.markdown("#### 📋 Matrice d'Avancement Réal-Time de toutes les Citernes")
    
    col_t1, col_t2 = st.columns([1, 2])
    with col_t1:
        filter_status_table = st.selectbox("Filtrer par Statut", ["Tous", "En cours", "Non commencé", "Terminé"], key="table_status_filter")
    with col_t2:
        search_table = st.text_input("🔍 Rechercher une citerne...", key="table_search")
        
    df_table_display = df_summary.copy()
    if filter_status_table != "Tous":
        df_table_display = df_table_display[df_table_display['statut'] == filter_status_table]
    if search_table:
        df_table_display = df_table_display[df_table_display['code'].str.contains(search_table.strip(), case=False)]
        
    df_table_display = df_table_display[['code', 'type', 'statut', 'global_pct', 'completed_hours', 'total_cadence', 'comments', 'updated_at']]
    df_table_display.columns = ['Code Citerne', 'Type', 'Statut', 'Avancement (%)', 'Heures Complétées', 'Total Cadence (h)', 'Observations / Commentaires', 'Dernière Maj']
    
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

# ==========================================
# MODULE 3: EXPORTATION & RAPPORT DU JOUR
# ==========================================
elif mode == "📥 Exportation & Rapport du Jour":
    st.markdown("### 📥 Exportation & Rapport de l'État du Jour")
    st.caption("Générez et téléchargez le rapport d'avancement quotidien au format Excel (.xlsx) ou CSV pour l'administration SEFACAR.")
    
    export_type = st.radio("Sélectionnez le Type à Exporter :", ["TOUS (Carburant & Eau)", "CARBURANT uniquement", "EAU uniquement"], horizontal=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("📊 Générer le Rapport Excel Complet de l'État du Jour", use_container_width=True):
        output = python_io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if export_type in ["TOUS (Carburant & Eau)", "CARBURANT uniquement"]:
                carb_matrix = db.export_full_matrix("CARBURANT")
                carb_matrix.to_excel(writer, sheet_name="CARBURANT")
            if export_type in ["TOUS (Carburant & Eau)", "EAU uniquement"]:
                eau_matrix = db.export_full_matrix("EAU")
                eau_matrix.to_excel(writer, sheet_name="EAU")
                
            filter_t = None if export_type == "TOUS (Carburant & Eau)" else ("CARBURANT" if "CARBURANT" in export_type else "EAU")
            synthese_df = db.get_summary_dataframe(filter_t)
            synthese_df.to_excel(writer, sheet_name="SYNTHESE_GENERAL", index=False)
            
        excel_data = output.getvalue()
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
    st.markdown("#### 👁️ Aperçu des Données à Exporter (Synthèse)")
    filter_t = None if export_type == "TOUS (Carburant & Eau)" else ("CARBURANT" if "CARBURANT" in export_type else "EAU")
    preview_df = db.get_summary_dataframe(filter_t)
    st.dataframe(preview_df, use_container_width=True, hide_index=True)

# ==========================================
# MODULE 4: CONFIGURATION & SYNCHRO
# ==========================================
elif mode == "⚙️ Configuration & Synchro":
    st.markdown("### ⚙️ Configuration & Synchronisation")
    st.caption("Gérez la base de données et réinitialisez les données initiales depuis le fichier Excel d'origine.")
    
    st.markdown("#### 🔄 Réinitialiser la Base de Données depuis `SUIVI CITERNE 2107.xlsx`")
    st.warning("⚠️ Attention : La réinitialisation remplacera les données actuelles de la base par les données du fichier Excel d'origine.")
    
    if st.button("🔄 Lancer la Synchronisation / Réinitialisation", key="reset_db_btn"):
        import init_db
        with st.spinner("Rechargement des données depuis Excel..."):
            init_db.init_database_from_excel(force=True)
        st.success("🎉 Base de données réinitialisée avec succès à partir de l'Excel !")
        st.rerun()
        
    st.markdown("---")
    st.markdown("#### ℹ️ Informations sur le Système")
    conn = db.get_connection()
    citerne_count = conn.execute("SELECT COUNT(*) FROM citernes").fetchone()[0]
    etape_count = conn.execute("SELECT COUNT(*) FROM etapes").fetchone()[0]
    progress_count = conn.execute("SELECT COUNT(*) FROM suivi_progress").fetchone()[0]
    conn.close()
    
    st.json({
        "Application": "SEFACAR Tank Progress Digitalization",
        "Theme": "Light Executive",
        "Authentication": "Secured",
        "Database Engine": "SQLite 3",
        "Total Citernes": citerne_count,
        "Total Étapes Cataloguées": etape_count,
        "Total Enregistrements d'Avancement": progress_count,
        "Dernière Synchronisation System": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
