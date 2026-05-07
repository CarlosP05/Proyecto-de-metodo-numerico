"""
ui_theme.py — Sistema de temas para la Calculadora de Métodos Numéricos
Centraliza todos los colores, fuentes y estilos de matplotlib.
"""

# ─────────────────────────────────────────────
#  PALETAS DE COLORES
# ─────────────────────────────────────────────

DARK = {
    "bg_app":          "#0d0d0d",
    "bg_sidebar":      "#111111",
    "bg_card":         "#181818",
    "bg_card2":        "#1e1e1e",
    "bg_input":        "#1a1a1a",
    "text_primary":    "#f0f0f0",
    "text_secondary":  "#888888",
    "accent":          "#ff2244",          # Rojo neón principal
    "accent_hover":    "#ff4466",
    "accent_glow":     "#ff0033",
    "btn_text":        "#ffffff",
    "border":          "#2a2a2a",
    "tab_selected":    "#ff2244",
    "row_odd":         "#1e1e1e",
    "row_even":        "#252525",
    "row_header":      "#120008",
    "tree_fg":         "#e0e0e0",
    "tree_heading":    "#ff2244",
    "success":         "#00e676",
    "warning":         "#ffab40",
    "info":            "#40c4ff",
    # Matplotlib
    "mpl_bg":          "#111111",
    "mpl_ax_bg":       "#181818",
    "mpl_line":        "#ff2244",
    "mpl_zero":        "#555555",
    "mpl_grid":        "#2a2a2a",
    "mpl_tick":        "#888888",
    "mpl_label":       "#aaaaaa",
    "mpl_root":        "#00e676",
    "mpl_val1":        "#ff9100",
    "mpl_val2":        "#40c4ff",
    "mpl_legend_bg":   "#1e1e1e",
    "mpl_legend_edge": "#333333",
}

LIGHT = {
    "bg_app":          "#f4f6fa",
    "bg_sidebar":      "#ffffff",
    "bg_card":         "#ffffff",
    "bg_card2":        "#f8f9fb",
    "bg_input":        "#f0f2f5",
    "text_primary":    "#1a1a2e",
    "text_secondary":  "#6b7280",
    "accent":          "#2563eb",          # Azul moderno
    "accent_hover":    "#1d4ed8",
    "accent_glow":     "#3b82f6",
    "btn_text":        "#ffffff",
    "border":          "#e5e7eb",
    "tab_selected":    "#2563eb",
    "row_odd":         "#ffffff",
    "row_even":        "#f9fafb",
    "row_header":      "#eff6ff",
    "tree_fg":         "#374151",
    "tree_heading":    "#1e40af",
    "success":         "#059669",
    "warning":         "#d97706",
    "info":            "#0284c7",
    # Matplotlib
    "mpl_bg":          "#f4f6fa",
    "mpl_ax_bg":       "#ffffff",
    "mpl_line":        "#2563eb",
    "mpl_zero":        "#9ca3af",
    "mpl_grid":        "#e5e7eb",
    "mpl_tick":        "#6b7280",
    "mpl_label":       "#374151",
    "mpl_root":        "#059669",
    "mpl_val1":        "#d97706",
    "mpl_val2":        "#7c3aed",
    "mpl_legend_bg":   "#ffffff",
    "mpl_legend_edge": "#e5e7eb",
}


def get_theme(mode: str) -> dict:
    """Devuelve el diccionario de colores según el modo ('dark' | 'light')."""
    return DARK if mode == "dark" else LIGHT


# ─────────────────────────────────────────────
#  ESTILOS PARA tkinter.ttk.Treeview
# ─────────────────────────────────────────────

def apply_treeview_style(style, mode: str):
    """Aplica estilos ttk al Treeview según el tema activo."""
    t = get_theme(mode)

    style.theme_use("clam")

    style.configure(
        "Modern.Treeview",
        background=t["row_odd"],
        foreground=t["tree_fg"],
        fieldbackground=t["row_odd"],
        rowheight=28,
        font=("Segoe UI", 10),
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Modern.Treeview.Heading",
        background=t["row_header"],
        foreground=t["tree_heading"],
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
        relief="flat",
        padding=(6, 4),
    )
    style.map(
        "Modern.Treeview",
        background=[("selected", t["accent"])],
        foreground=[("selected", "#ffffff")],
    )
    style.map(
        "Modern.Treeview.Heading",
        background=[("active", t["accent"])],
        foreground=[("active", "#ffffff")],
    )
    # Scrollbar integrada
    style.configure(
        "Modern.Vertical.TScrollbar",
        background=t["bg_card2"],
        troughcolor=t["bg_card"],
        arrowcolor=t["text_secondary"],
        borderwidth=0,
        relief="flat",
    )
