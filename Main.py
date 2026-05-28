"""
Main.py — Calculadora de Métodos Numéricos
Interfaz modernizada con CustomTkinter + Matplotlib.
Lógica matemática separada en módulos externos (biseccion.py, etc.)
"""

# ═══════════════════════════════════════════════
#  IMPORTACIONES
# ═══════════════════════════════════════════════
import math
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import sympy as sp

# Lógica matemática (sin cambios)
from biseccion   import MetodoBiseccion
from regla_falsa import MetodoReglaFalsa
from newton      import MetodoNewton
from secante     import MetodoSecante
from punto_fijo  import MetodoPuntoFijo
from muller import MetodoMuller
from bairstow import MetodoBairstow
from horner_newton import MetodoHornerNewton
from metodos_avanzados import (
    MetodoGaussJordan,
    MetodoInterpolacionLagrange,
    MetodoJacobi,
    MetodoLU,
    MetodoMinimosCuadrados,
    MetodoNewtonDiferenciasDivididas,
    MetodoNewtonSENL,
    MetodoRegresionCuadratica,
    MetodoRoucheFrobenius,
)

# Sistema de temas
from ui_theme import get_theme, apply_treeview_style

# ═══════════════════════════════════════════════
#  CONFIGURACIÓN INICIAL DE CTK
# ═══════════════════════════════════════════════
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


# ═══════════════════════════════════════════════
#  CLASE TOOLTIP
# ═══════════════════════════════════════════════
class Tooltip:
    """Pequeño texto flotante que aparece al pasar el mouse sobre un widget.
    Aparece con un pequeño delay para no ser intrusivo."""

    def __init__(self, widget, text: str, delay: int = 600):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self._after_id = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)
        widget.bind("<ButtonPress>", self._hide)

    def _schedule(self, event=None):
        self._cancel()
        self._after_id = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self, event=None):
        if self.tip_window:
            return
        # Posicionar a la derecha del widget
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 6
        y = self.widget.winfo_rooty() + (self.widget.winfo_height() // 2) - 14
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        # Marco exterior con color accent como borde de 1px
        outer = tk.Frame(tw, bg="#ff2244", padx=1, pady=1)
        outer.pack()
        inner = tk.Label(
            outer,
            text=self.text,
            background="#1e1e1e",
            foreground="#e0e0e0",
            relief="flat",
            font=("Segoe UI", 9),
            padx=10,
            pady=5,
        )
        inner.pack()

    def _hide(self, event=None):
        self._cancel()
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ═══════════════════════════════════════════════
#  CLASE PRINCIPAL
# ═══════════════════════════════════════════════
class AplicacionPrincipal(ctk.CTk):

    # ──────────────────────────────────────────
    #  INICIALIZACIÓN
    # ──────────────────────────────────────────
    def __init__(self):
        super().__init__()

        self._modo_oscuro = True          # Estado del tema
        self._btn_activo  = None          # Referencia al botón de nav activo
        self._hover_timers = {}           # Timers para animaciones hover
        self._vista_activa = None         # Función del panel actualmente visible
        self._entradas_actuales = []      # Widgets de entrada del panel activo
        self._tree_actual = None          # Treeview del panel activo

        self.title("Métodos Numéricos — Calculadora de Raíces")
        self.geometry("1100x680")
        self.minsize(900, 560)
        self.configure(fg_color=self._t("bg_app"))

        # Estilo ttk global (para Treeview)
        self._style = ttk.Style()
        apply_treeview_style(self._style, "dark")

        self._construir_ui()
        self.mostrar_bienvenida()

    # ──────────────────────────────────────────
    #  ACCESO AL TEMA ACTIVO
    # ──────────────────────────────────────────
    def _t(self, key: str) -> str:
        """Devuelve el color del tema actual para la clave dada."""
        return get_theme("dark" if self._modo_oscuro else "light")[key]

    # ──────────────────────────────────────────
    #  CONSTRUCCIÓN DE LA UI PRINCIPAL
    # ──────────────────────────────────────────
    def _construir_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._construir_sidebar()
        self._construir_area_principal()

    # ── SIDEBAR ───────────────────────────────
    def _construir_sidebar(self):
        t = self._t

        self.sidebar = ctk.CTkFrame(
            self, width=210, corner_radius=0,
            fg_color=t("bg_sidebar"),
            border_width=1, border_color=t("border")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(15, weight=1)   # Empuja el selector de tema hacia abajo

        # ── Logo / Título
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=16, pady=(24, 6), sticky="ew")

        ctk.CTkLabel(
            logo_frame, text="∫",
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            text_color=self._t("accent")
        ).pack(side="left", padx=(0, 8))

        titulo_col = ctk.CTkFrame(logo_frame, fg_color="transparent")
        titulo_col.pack(side="left")
        ctk.CTkLabel(
            titulo_col, text="NumSolver",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self._t("text_primary")
        ).pack(anchor="w")
        ctk.CTkLabel(
            titulo_col, text="Raíces de ecuaciones",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self._t("text_secondary")
        ).pack(anchor="w")

        # Separador
        self._sep(self.sidebar, row=1)

        # ── Sección Métodos Cerrados
        self._seccion_label(self.sidebar, "MÉTODOS CERRADOS", row=2)

        self.btn_biseccion = self._nav_button(
            self.sidebar, "  📐  Bisección", self.mostrar_biseccion, row=3,
            tooltip="Divide el intervalo [a,b] a la mitad iterativamente"
        )
        self.btn_regla_falsa = self._nav_button(
            self.sidebar, "  📏  Regla Falsa", self.mostrar_regla_falsa, row=4,
            tooltip="Interpolación lineal entre a y b para estimar la raíz"
        )

        # ── Sección Métodos Abiertos
        self._seccion_label(self.sidebar, "MÉTODOS ABIERTOS", row=5)

        self.btn_newton = self._nav_button(
            self.sidebar, "  ⚡  Newton-Raphson", self.mostrar_newton, row=6,
            tooltip="Usa la derivada f'(x) para converger rápidamente"
        )
        self.btn_secante = self._nav_button(
            self.sidebar, "  📈  Secante", self.mostrar_secante, row=7,
            tooltip="Aproxima la derivada usando dos puntos iniciales"
        )
        self.btn_punto_fijo = self._nav_button(
            self.sidebar, "  🔄  Punto Fijo", self.mostrar_punto_fijo, row=8,
            tooltip="Itera x = g(x) hasta que converge al punto fijo"
        )

        # ── NUEVA SECCIÓN: Raíces de Polinomios ──
        self._seccion_label(self.sidebar, "RAÍCES DE POLINOMIOS", row=9)

        self.btn_muller = self._nav_button(
            self.sidebar, "  🧮  Müller", self.mostrar_muller, row=10,
            tooltip="Usa parábola para encontrar raíces complejas"
        )
        self.btn_bairstow = self._nav_button(
            self.sidebar, "  ✂️  Bairstow", self.mostrar_bairstow, row=11,
            tooltip="Extrae factores cuadráticos (raíces complejas)"
        )
        self.btn_horner = self._nav_button(
            self.sidebar, "  📝  Horner-Newton", self.mostrar_horner, row=12,
            tooltip="Evaluación eficiente con el esquema de Horner"
        )
        self.btn_avanzados = self._nav_button(
            self.sidebar, "  🧩  Métodos avanzados", self.mostrar_avanzados, row=13,
            tooltip="Álgebra lineal, interpolación, regresión y sistemas no lineales"
        )

        # Separador inferior
        self._sep(self.sidebar, row=14)

        # ── Toggle de tema
        tema_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        tema_frame.grid(row=16, column=0, padx=16, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(
            tema_frame, text="Tema:",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self._t("text_secondary")
        ).pack(side="left")

        self.btn_tema = ctk.CTkButton(
            tema_frame,
            text="🌙  Oscuro",
            width=90,
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=self._t("accent"),
            hover_color=self._t("accent_hover"),
            text_color="#ffffff",
            corner_radius=14,
            command=self.alternar_tema,
        )
        self.btn_tema.pack(side="right")

    # ──────────────────────────────────────────
    #  UTILIDADES DE SIDEBAR
    # ──────────────────────────────────────────
    def _sep(self, parent, row: int):
        """Línea divisora horizontal."""
        sep = ctk.CTkFrame(parent, height=1, fg_color=self._t("border"))
        sep.grid(row=row, column=0, padx=16, pady=6, sticky="ew")

    def _seccion_label(self, parent, texto: str, row: int):
        lbl = ctk.CTkLabel(
            parent, text=texto,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=self._t("text_secondary"),
            anchor="w"
        )
        lbl.grid(row=row, column=0, padx=20, pady=(12, 2), sticky="w")

    def _nav_button(self, parent, texto: str, comando, row: int, tooltip: str = ""):
        """Crea un botón de navegación con animación hover y tooltip opcional."""
        btn = ctk.CTkButton(
            parent,
            text=texto,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="transparent",
            hover_color=self._t("bg_card2"),
            text_color=self._t("text_primary"),
            anchor="w",
            height=38,
            corner_radius=8,
            border_width=0,
            command=lambda b=None, c=comando: self._nav_click(c),
        )
        btn.grid(row=row, column=0, padx=10, pady=2, sticky="ew")

        # Micro-animaciones hover
        btn.bind("<Enter>", lambda e, b=btn: self._on_nav_enter(b))
        btn.bind("<Leave>", lambda e, b=btn: self._on_nav_leave(b))

        # Tooltip descriptivo (aparece a la derecha del sidebar)
        if tooltip:
            Tooltip(btn, tooltip)

        return btn

    # ── ÁREA PRINCIPAL ────────────────────────
    def _construir_area_principal(self):
        self.frame_principal = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=self._t("bg_card"),
            border_width=1,
            border_color=self._t("border"),
        )
        self.frame_principal.grid(row=0, column=1, padx=(0, 16), pady=16, sticky="nsew")
        self.frame_principal.grid_columnconfigure((0, 1, 2, 3), weight=1)
        # La fila de contenido (tabs) se configura dinámicamente en cada vista

    # ──────────────────────────────────────────
    #  ANIMACIONES DE HOVER (SIDEBAR)
    # ──────────────────────────────────────────
    def _on_nav_enter(self, btn):
        if btn is self._btn_activo:
            return
        btn.configure(
            fg_color=self._t("bg_card2"),
            text_color=self._t("accent"),
        )

    def _on_nav_leave(self, btn):
        if btn is self._btn_activo:
            return
        btn.configure(
            fg_color="transparent",
            text_color=self._t("text_primary"),
        )

    def _nav_click(self, comando):
        """Resetea el botón activo anterior y ejecuta el comando."""
        comando()

    def _set_btn_activo(self, btn):
        """Resalta visualmente el botón de nav actualmente seleccionado."""
        # Resetear anterior
        if self._btn_activo and self._btn_activo is not btn:
            self._btn_activo.configure(
                fg_color="transparent",
                text_color=self._t("text_primary"),
                border_width=0,
            )
        self._btn_activo = btn
        btn.configure(
            fg_color=self._t("accent") if self._modo_oscuro else self._t("bg_card2"),
            text_color="#ffffff" if self._modo_oscuro else self._t("accent"),
            border_width=0,
        )

    # ──────────────────────────────────────────
    #  CAMBIO DE TEMA
    # ──────────────────────────────────────────
    def alternar_tema(self):
        self._modo_oscuro = not self._modo_oscuro
        modo_str = "Dark" if self._modo_oscuro else "Light"
        ctk.set_appearance_mode(modo_str)
        apply_treeview_style(self._style, "dark" if self._modo_oscuro else "light")

        # Actualizar botón de tema
        self.btn_tema.configure(
            text="🌙  Oscuro" if self._modo_oscuro else "☀️  Claro",
            fg_color=self._t("accent"),
            hover_color=self._t("accent_hover"),
        )

        # Actualizar colores del frame raíz y sidebar
        self.configure(fg_color=self._t("bg_app"))
        self.sidebar.configure(
            fg_color=self._t("bg_sidebar"),
            border_color=self._t("border"),
        )
        self.frame_principal.configure(
            fg_color=self._t("bg_card"),
            border_color=self._t("border"),
        )

        # ── RE-RENDERIZAR el panel activo ────────────────────────────────
        # Los widgets con colores hardcodeados (entries, tabs, treeview) necesitan
        # ser recreados para que reflejen el nuevo tema.
        if self._vista_activa is not None:
            self._vista_activa()

    # ──────────────────────────────────────────
    #  UTILIDADES DE UI
    # ──────────────────────────────────────────
    def limpiar_frame_principal(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
        # Resetear pesos de todas las filas usadas (hasta 12 cubre todos los casos)
        for i in range(12):
            self.frame_principal.grid_rowconfigure(i, weight=0, minsize=0)
        # Resetear entradas y tree del panel anterior
        self._entradas_actuales = []
        self._tree_actual = None

    def _set_tab_row(self, row: int):
        """Configura la fila de tabs/resultados para que se expanda fluidamente con la ventana."""
        self.frame_principal.grid_rowconfigure(row, weight=1, minsize=180)

    def _titulo(self, texto: str, icono: str = ""):
        """Crea un encabezado de sección con icono y línea de acento."""
        frame = ctk.CTkFrame(
            self.frame_principal,
            fg_color="transparent",
            corner_radius=0,
        )
        frame.grid(row=0, column=0, columnspan=4, padx=24, pady=(24, 4), sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text=f"{icono}  {texto}" if icono else texto,
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=self._t("text_primary"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        # Línea accent debajo del título
        ctk.CTkFrame(
            self.frame_principal,
            height=2,
            fg_color=self._t("accent"),
            corner_radius=1,
        ).grid(row=1, column=0, columnspan=4, padx=24, pady=(0, 16), sticky="ew")

    def _label(self, texto: str, row: int, col: int, **kwargs):
        lbl = ctk.CTkLabel(
            self.frame_principal,
            text=texto,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self._t("text_secondary"),
            anchor="e",
            **kwargs,
        )
        lbl.grid(row=row, column=col, padx=(16, 4), pady=8, sticky="e")
        return lbl

    def _entry(self, row: int, col: int, placeholder: str = "", width: int = 120):
        """Entry estilizado. border_width explícito permite la animación de error rojo."""
        if self._modo_oscuro:
            e = ctk.CTkEntry(
                self.frame_principal,
                placeholder_text=placeholder,
                width=width,
                height=34,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                fg_color="#1a1a1a",
                border_color="#2a2a2a",
                border_width=1,
                text_color="#f0f0f0",
                placeholder_text_color="#666666",
                corner_radius=8,
            )
        else:
            e = ctk.CTkEntry(
                self.frame_principal,
                placeholder_text=placeholder,
                width=width,
                height=34,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                fg_color="#ffffff",
                border_color="#d1d5db",
                border_width=1,
                text_color="#111827",
                placeholder_text_color="#9ca3af",
                corner_radius=8,
            )
        e.grid(row=row, column=col, padx=(4, 16), pady=8, sticky="w")
        return e

    def _textbox(self, row: int, col: int, texto: str = "", width: int = 260,
                 height: int = 90, colspan: int = 1):
        bg = "#1a1a1a" if self._modo_oscuro else "#ffffff"
        border = "#2a2a2a" if self._modo_oscuro else "#d1d5db"
        fg = "#f0f0f0" if self._modo_oscuro else "#111827"
        box = ctk.CTkTextbox(
            self.frame_principal,
            width=width,
            height=height,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=bg,
            border_color=border,
            text_color=fg,
            corner_radius=8,
            border_width=1,
        )
        if texto:
            box.insert("1.0", texto)
        box.grid(row=row, column=col, columnspan=colspan, padx=(4, 16), pady=8, sticky="nsew")
        return box

    def _boton_calcular(self, texto: str, comando, row: int, col: int = 0, colspan: int = 2):
        """Botón 'Calcular Raíz' con efecto glow. Ocupa col 0-1 para dejar espacio al botón limpiar."""
        btn = ctk.CTkButton(
            self.frame_principal,
            text=texto,
            command=comando,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=self._t("accent"),
            hover_color=self._t("accent_hover"),
            text_color="#ffffff",
            height=40,
            width=200,
            corner_radius=10,
        )
        btn.grid(row=row, column=col, columnspan=colspan, padx=(16, 4), pady=(8, 16), sticky="w")

        # Micro-animación: hover scale (visual approximation via color pulse)
        btn.bind("<Enter>",  lambda e: self._btn_hover_enter(btn))
        btn.bind("<Leave>",  lambda e: self._btn_hover_leave(btn))
        btn.bind("<Button-1>", lambda e: self._btn_click_anim(btn))
        return btn

    def _boton_limpiar(self, row: int, col: int = 2, colspan: int = 2):
        """Botón secundario 🗑️ discreto para limpiar entradas y resultados del panel activo."""
        btn = ctk.CTkButton(
            self.frame_principal,
            text="🗑️  Limpiar",
            command=self._limpiar_entradas_actuales,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="transparent",
            hover_color=self._t("bg_card2"),
            text_color=self._t("text_secondary"),
            border_width=1,
            border_color=self._t("border"),
            height=40,
            width=110,
            corner_radius=10,
        )
        btn.grid(row=row, column=col, columnspan=colspan, padx=(0, 16), pady=(8, 16), sticky="e")
        return btn

    def _limpiar_entradas_actuales(self):
        """Limpia todas las entradas registradas y el Treeview del panel activo."""
        for widget in self._entradas_actuales:
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                # Restaurar borde normal por si quedó en estado de error
                bc = "#2a2a2a" if self._modo_oscuro else "#d1d5db"
                widget.configure(border_color=bc, border_width=1)
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
        if self._tree_actual is not None:
            try:
                self._tree_actual.delete(*self._tree_actual.get_children())
            except Exception:
                pass

    def _btn_hover_enter(self, btn):
        btn.configure(fg_color=self._t("accent_hover"))

    def _btn_hover_leave(self, btn):
        btn.configure(fg_color=self._t("accent"))

    def _btn_click_anim(self, btn):
        """Pulso rápido al hacer clic."""
        btn.configure(fg_color=self._t("accent_glow"))
        self.after(120, lambda: btn.configure(fg_color=self._t("accent")))

    # ──────────────────────────────────────────
    #  FEEDBACK VISUAL EN ENTRADAS INVÁLIDAS
    # ──────────────────────────────────────────
    def _marcar_entrada_error(self, *entries):
        """Pone borde rojo 2.5 s en las entries inválidas, luego lo restaura."""
        bc_normal = "#2a2a2a" if self._modo_oscuro else "#d1d5db"
        for entry in entries:
            if entry is None:
                continue
            entry.configure(border_color=self._t("error_border"), border_width=2)
            self.after(2500, lambda e=entry: e.configure(
                border_color=bc_normal,
                border_width=1,
            ))

    def _detectar_entries_invalidas(self, *entries):
        """Detecta y marca en rojo las entries que estén vacías o no sean numéricas."""
        invalidas = []
        for e in entries:
            val = e.get().strip()
            if not val:
                invalidas.append(e)
                continue
            try:
                float(val)
            except ValueError:
                invalidas.append(e)
        if invalidas:
            self._marcar_entrada_error(*invalidas)
        return invalidas

    def _crear_tabs(self, row: int):
        """Crea las pestañas 'Tabla de Iteraciones' y 'Gráfica'."""
        if self._modo_oscuro:
            tabs = ctk.CTkTabview(
                self.frame_principal,
                fg_color="#1e1e1e",
                segmented_button_fg_color="#181818",
                segmented_button_selected_color=self._t("accent"),
                segmented_button_selected_hover_color=self._t("accent_hover"),
                segmented_button_unselected_color="#181818",
                segmented_button_unselected_hover_color="#252525",
                text_color="#f0f0f0",
                text_color_disabled="#555555",
                corner_radius=10,
            )
        else:
            tabs = ctk.CTkTabview(
                self.frame_principal,
                fg_color="#f3f4f6",
                segmented_button_fg_color="#e5e7eb",
                segmented_button_selected_color=self._t("accent"),
                segmented_button_selected_hover_color=self._t("accent_hover"),
                segmented_button_unselected_color="#e5e7eb",
                segmented_button_unselected_hover_color="#d1d5db",
                text_color="#111827",
                text_color_disabled="#9ca3af",
                corner_radius=10,
            )
        tabs.grid(row=row, column=0, columnspan=4, padx=16, pady=(0, 16), sticky="nsew")
        tabs.add("📊  Tabla de Iteraciones")
        tabs.add("📈  Gráfica")
        return tabs

    def _crear_tabs_resultado(self, row: int):
        tabs = ctk.CTkTabview(
            self.frame_principal,
            fg_color="#1e1e1e" if self._modo_oscuro else "#f3f4f6",
            segmented_button_fg_color="#181818" if self._modo_oscuro else "#e5e7eb",
            segmented_button_selected_color=self._t("accent"),
            segmented_button_selected_hover_color=self._t("accent_hover"),
            segmented_button_unselected_color="#181818" if self._modo_oscuro else "#e5e7eb",
            segmented_button_unselected_hover_color="#252525" if self._modo_oscuro else "#d1d5db",
            text_color="#f0f0f0" if self._modo_oscuro else "#111827",
            corner_radius=10,
        )
        tabs.grid(row=row, column=0, columnspan=4, padx=16, pady=(0, 16), sticky="nsew")
        tabs.add("📋  Resultado")
        tabs.add("📊  Detalle")
        self._mostrar_texto_resultado(
            tabs.tab("📊  Detalle"),
            "Aquí aparecerá el detalle del cálculo cuando presiones el botón calcular."
        )
        return tabs

    def _mostrar_resultado_avanzado(self, tabs, resumen: str, detalle: str | None = None):
        self._mostrar_texto_resultado(tabs.tab("📋  Resultado"), resumen)
        self._mostrar_texto_resultado(tabs.tab("📊  Detalle"), detalle or resumen)

    def _mostrar_texto_resultado(self, parent, texto: str):
        for child in parent.winfo_children():
            child.destroy()
        bg = "#1a1a1a" if self._modo_oscuro else "#ffffff"
        fg = "#f0f0f0" if self._modo_oscuro else "#111827"
        box = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=bg,
            text_color=fg,
            corner_radius=8,
        )
        box.pack(fill="both", expand=True, padx=8, pady=8)
        box.insert("1.0", texto)
        box.configure(state="disabled")

    def _matriz_a_texto(self, titulo: str, filas) -> str:
        lineas = [titulo]
        for fila in filas:
            lineas.append("  [" + "  ".join(str(v) for v in fila) + "]")
        return "\n".join(lineas)

    def _crear_treeview(self, parent, columnas: list) -> ttk.Treeview:
        """Crea un Treeview estilizado con scrollbar y filas alternadas."""
        # El fondo del contenedor debe coincidir con el del tab en el tema activo
        cont_bg = "#1e1e1e" if self._modo_oscuro else "#f3f4f6"
        container = ctk.CTkFrame(parent, fg_color=cont_bg, corner_radius=8)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        # Scrollbar
        sb = ttk.Scrollbar(container, orient="vertical", style="Modern.Vertical.TScrollbar")
        sb.pack(side="right", fill="y")

        tree = ttk.Treeview(
            container,
            columns=columnas,
            show="headings",
            style="Modern.Treeview",
            yscrollcommand=sb.set,
        )
        sb.config(command=tree.yview)

        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=max(80, len(col) * 9))

        tree.pack(fill="both", expand=True)

        # Etiquetas para filas alternadas
        tree.tag_configure("odd",  background=self._t("row_odd"),  foreground=self._t("tree_fg"))
        tree.tag_configure("even", background=self._t("row_even"), foreground=self._t("tree_fg"))
        return tree

    def _llenar_treeview(self, tree: ttk.Treeview, filas: list):
        """Inserta filas en un Treeview con tag par/impar."""
        tree.delete(*tree.get_children())
        for i, fila in enumerate(filas):
            tag = "odd" if i % 2 == 0 else "even"
            valores = [str(v) if v is not None else "N/A" for v in fila]
            tree.insert("", "end", values=valores, tags=(tag,))

    def _panel_resultado(self, parent, raiz, iteraciones: int):
        """Mini-banner con la raíz encontrada."""
        self._limpiar_banners(parent)

        frame = ctk.CTkFrame(parent, fg_color=self._t("bg_card"), corner_radius=8)
        frame._mensaje_temporal = True
        frame.pack(fill="x", padx=8, pady=(8, 2))

        texto_raiz = f"{raiz:.8f}" if isinstance(raiz, (int, float)) else str(raiz)

        ctk.CTkLabel(
            frame,
            text=f"✅  Raíz aproximada:  {texto_raiz}    (en {iteraciones} iteraciones)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self._t("success"),
            anchor="w",
        ).pack(padx=12, pady=6, anchor="w")

    # ──────────────────────────────────────────
    #  GRÁFICA MATPLOTLIB (CON TOOLBAR INTERACTIVA)
    # ──────────────────────────────────────────
    def dibujar_grafico(self, funcion_str, val_1, val_2, raiz,
                        frame_destino, tipo_metodo="cerrado", metodo_nombre=""):
        for w in frame_destino.winfo_children():
            w.destroy()

        try:
            x_sym = sp.Symbol('x')
            f_expr = sp.sympify(funcion_str)
            f = sp.lambdify(x_sym, f_expr, 'numpy')

            minimo = min(val_1, val_2, raiz)
            maximo = max(val_1, val_2, raiz)
            margen = abs(maximo - minimo) * 0.35 if maximo != minimo else 2.5

            x_vals = np.linspace(minimo - margen, maximo + margen, 400)
            try:
                y_vals = np.array(f(x_vals), dtype=float)
            except Exception:
                y_vals = np.zeros_like(x_vals)

            # ── Colores según tema
            t = self._t
            bg      = t("mpl_bg")
            ax_bg   = t("mpl_ax_bg")
            col_ln  = t("mpl_line")
            col_0   = t("mpl_zero")
            col_gr  = t("mpl_grid")
            col_tk  = t("mpl_tick")
            col_lb  = t("mpl_label")
            col_rt  = t("mpl_root")
            col_v1  = t("mpl_val1")
            col_v2  = t("mpl_val2")
            leg_bg  = t("mpl_legend_bg")
            leg_eg  = t("mpl_legend_edge")

            # ── Figura (altura reducida para dejar espacio a la toolbar)
            fig, ax = plt.subplots(figsize=(6.5, 4.0), dpi=100)
            fig.patch.set_facecolor(bg)
            ax.set_facecolor(ax_bg)

            # Curva principal
            ax.plot(x_vals, y_vals, color=col_ln, linewidth=2.2,
                    alpha=0.9, label=f"f(x) = {funcion_str}", zorder=3)

            # Eje Y = 0
            ax.axhline(0, color=col_0, linewidth=1.2, alpha=0.7, zorder=1)

            # Líneas de referencia
            if tipo_metodo == "cerrado":
                ax.axvline(val_1, color=col_v1, linestyle="--",
                           linewidth=1.4, alpha=0.75, label=f"a = {val_1}")
                ax.axvline(val_2, color=col_v2, linestyle="--",
                           linewidth=1.4, alpha=0.75, label=f"b = {val_2}")
            elif tipo_metodo == "abierto":
                ax.axvline(val_1, color=col_v1, linestyle="--",
                           linewidth=1.4, alpha=0.75, label=f"x₀ = {val_1}")
                if val_1 != val_2:
                    ax.axvline(val_2, color=col_v2, linestyle="--",
                               linewidth=1.4, alpha=0.75, label=f"x₁ = {val_2}")

            # Punto de la raíz (con halo brillante)
            ax.scatter([raiz], [0], s=120, color=col_rt, zorder=6,
                       label=f"Raíz ≈ {raiz:.6f}")
            ax.scatter([raiz], [0], s=300, color=col_rt, alpha=0.18,
                       zorder=5)  # Halo

            # Línea vertical punteada desde la raíz hasta la curva
            try:
                y_raiz = float(f(raiz))
                ax.plot([raiz, raiz], [0, y_raiz], color=col_rt,
                        linestyle=":", linewidth=1.2, alpha=0.5, zorder=4)
            except Exception:
                pass

            # Cuadrícula y ticks
            ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.5, color=col_gr)
            ax.tick_params(colors=col_tk, labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor(col_gr)

            ax.set_xlabel("x", color=col_lb, fontsize=10, labelpad=6)
            ax.set_ylabel("f(x)", color=col_lb, fontsize=10, labelpad=6)

            titulo = metodo_nombre if metodo_nombre else "Gráfica de la función"
            ax.set_title(titulo, color=col_lb, fontsize=11, pad=10)

            legend = ax.legend(
                fontsize=8.5,
                facecolor=leg_bg,
                edgecolor=leg_eg,
                labelcolor=col_lb,
                framealpha=0.9,
            )

            fig.tight_layout(pad=1.0)

            # ── Incrustar canvas en CustomTkinter
            canvas = FigureCanvasTkAgg(fig, master=frame_destino)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(4, 0))

            # ── Toolbar de navegación interactiva (zoom, pan, guardar)
            toolbar_frame = tk.Frame(frame_destino, bg=bg, height=32)
            toolbar_frame.pack(fill="x", padx=4, pady=(0, 4))
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.config(background=bg)
            for child in toolbar.winfo_children():
                try:
                    child.config(background=bg)
                except Exception:
                    pass
            toolbar.update()

            plt.close(fig)

        except Exception as e:
            ctk.CTkLabel(
                frame_destino,
                text=f"⚠️  Error al graficar:\n{e}",
                text_color=self._t("warning"),
                font=ctk.CTkFont(family="Segoe UI", size=12),
            ).pack(expand=True)

    # ──────────────────────────────────────────
    #  PANTALLA DE BIENVENIDA
    # ──────────────────────────────────────────
    def mostrar_bienvenida(self):
        self.limpiar_frame_principal()

        # Card central
        card = ctk.CTkFrame(
            self.frame_principal,
            fg_color=self._t("bg_card2"),
            corner_radius=16,
        )
        card.grid(row=0, column=0, columnspan=4,
                  padx=60, pady=60, sticky="nsew")
        self.frame_principal.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="∫",
            font=ctk.CTkFont(family="Segoe UI", size=64, weight="bold"),
            text_color=self._t("accent"),
        ).pack(pady=(40, 8))

        ctk.CTkLabel(
            card,
            text="Calculadora de Métodos Numéricos",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=self._t("text_primary"),
        ).pack()

        ctk.CTkLabel(
            card,
            text="Selecciona un método en el panel izquierdo para comenzar.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self._t("text_secondary"),
        ).pack(pady=(8, 16))

        # Mini-guía de métodos
        metodos = [
            ("📐", "Bisección",       "Divide el intervalo a la mitad"),
            ("📏", "Regla Falsa",     "Interpolación lineal en el intervalo"),
            ("⚡", "Newton-Raphson",  "Usa la derivada para converger rápido"),
            ("📈", "Secante",         "Aproxima la derivada con dos puntos"),
            ("🔄", "Punto Fijo",      "Itera x = g(x) hasta converger"),
        ]
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(pady=(10, 40), padx=30)

        for idx, (icon, nombre, desc) in enumerate(metodos):
            col = idx % 3
            row_g = idx // 3
            cell = ctk.CTkFrame(
                grid,
                fg_color=self._t("bg_card"),
                corner_radius=10,
            )
            cell.grid(row=row_g, column=col, padx=8, pady=6, ipadx=10, ipady=8)
            ctk.CTkLabel(cell, text=icon, font=ctk.CTkFont(size=20)).pack()
            ctk.CTkLabel(
                cell, text=nombre,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=self._t("text_primary"),
            ).pack()
            ctk.CTkLabel(
                cell, text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=9),
                text_color=self._t("text_secondary"),
            ).pack()

    # ══════════════════════════════════════════
    #  ─────────── MÉTODO BISECCIÓN ───────────
    # ══════════════════════════════════════════
    def mostrar_biseccion(self):
        self._vista_activa = self.mostrar_biseccion
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_biseccion)
        self._titulo("Método de Bisección", "📐")

        # Entradas
        self._label("Función  f(x):", 2, 0)
        self.entrada_funcion = self._entry(2, 1, "Ej: x**3 - x - 2", width=220)

        self._label("Intervalo  [a]:", 3, 0)
        self.entrada_a = self._entry(3, 1, "Ej: 1")

        self._label("Intervalo  [b]:", 3, 2)
        self.entrada_b = self._entry(3, 3, "Ej: 2")

        self._label("Tolerancia (%):", 4, 0)
        self.entrada_tol = self._entry(4, 1, "Ej: 0.5")

        # Registrar entradas para el botón limpiar
        self._entradas_actuales = [self.entrada_funcion, self.entrada_a,
                                   self.entrada_b, self.entrada_tol]

        # Botones Calcular + Limpiar en la misma fila
        self._boton_calcular("⚙️  Calcular Raíz", self.ejecutar_biseccion, row=5)
        self._boton_limpiar(row=5)

        # Tabs
        self.tabs_biseccion = self._crear_tabs(row=6)
        self._set_tab_row(6)

        # Treeview en pestaña 1
        tab_tabla = self.tabs_biseccion.tab("📊  Tabla de Iteraciones")
        self.tree_biseccion = self._crear_treeview(
            tab_tabla,
            ["Iter", "a", "b", "c (Punto Medio)", "f(c)", "Error (%)"]
        )
        self._tree_actual = self.tree_biseccion

    def ejecutar_biseccion(self):
        funcion_str = self.entrada_funcion.get().strip()
        try:
            a = float(self.entrada_a.get())
            b = float(self.entrada_b.get())
            tol = float(self.entrada_tol.get())
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_a, self.entrada_b, self.entrada_tol)
            self._mostrar_error(self.tree_biseccion, "Ingresa números válidos en los campos.")
            return
        if not self._validar_tolerancia(tol, self.tree_biseccion):
            return
        if not self._validar_numeros(self.tree_biseccion, a=a, b=b):
            return

        metodo   = MetodoBiseccion()
        resultado = self._calcular_seguro(metodo.calcular, funcion_str, a, b, tol)

        if "error" in resultado:
            self._mostrar_error_label(self.tabs_biseccion.tab("📊  Tabla de Iteraciones"),
                                      resultado["error"])
            return

        # Llenar tabla
        filas = []
        for f in resultado["tabla_iteraciones"]:
            err_str = f"{f['Error (%)']:.6f}" if f['Error (%)'] is not None else "N/A"
            filas.append([
                f["Iteración"],
                f"{f['a']:.6f}", f"{f['b']:.6f}",
                f"{f['c']:.6f}", f"{f['f(c)']:.6f}", err_str,
            ])
        self._llenar_treeview(self.tree_biseccion, filas)

        # Banner resultado
        tab_tabla = self.tabs_biseccion.tab("📊  Tabla de Iteraciones")
        self._limpiar_banners(tab_tabla)
        self._panel_resultado(tab_tabla, resultado["raiz_aproximada"],
                              resultado["total_iteraciones"])

        # Gráfica
        self.dibujar_grafico(
            funcion_str, a, b,
            resultado["raiz_aproximada"],
            self.tabs_biseccion.tab("📈  Gráfica"),
            tipo_metodo="cerrado",
            metodo_nombre="Bisección",
        )

    # ══════════════════════════════════════════
    #  ─────────── REGLA FALSA ────────────────
    # ══════════════════════════════════════════
    def mostrar_regla_falsa(self):
        self._vista_activa = self.mostrar_regla_falsa
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_regla_falsa)
        self._titulo("Método de Regla Falsa", "📏")

        self._label("Función  f(x):", 2, 0)
        self.entrada_funcion_rf = self._entry(2, 1, "Ej: exp(x) - 2", width=220)

        self._label("Intervalo  [a]:", 3, 0)
        self.entrada_a_rf = self._entry(3, 1, "Ej: 0")

        self._label("Intervalo  [b]:", 3, 2)
        self.entrada_b_rf = self._entry(3, 3, "Ej: 1")

        self._label("Tolerancia (%):", 4, 0)
        self.entrada_tol_rf = self._entry(4, 1, "Ej: 0.5")

        self._entradas_actuales = [self.entrada_funcion_rf, self.entrada_a_rf,
                                   self.entrada_b_rf, self.entrada_tol_rf]
        self._boton_calcular("⚙️  Calcular Raíz", self.ejecutar_regla_falsa, row=5)
        self._boton_limpiar(row=5)

        self.tabs_rf = self._crear_tabs(row=6)
        self._set_tab_row(6)

        tab_tabla = self.tabs_rf.tab("📊  Tabla de Iteraciones")
        self.tree_rf = self._crear_treeview(
            tab_tabla,
            ["Iter", "a", "b", "c (R. Falsa)", "f(c)", "Error (%)"]
        )
        self._tree_actual = self.tree_rf

    def ejecutar_regla_falsa(self):
        funcion_str = self.entrada_funcion_rf.get().strip()
        try:
            a = float(self.entrada_a_rf.get())
            b = float(self.entrada_b_rf.get())
            tol = float(self.entrada_tol_rf.get())
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_a_rf, self.entrada_b_rf, self.entrada_tol_rf)
            self._mostrar_error(self.tree_rf, "Ingresa números válidos en los campos.")
            return
        if not self._validar_tolerancia(tol, self.tree_rf):
            return
        if not self._validar_numeros(self.tree_rf, a=a, b=b):
            return

        metodo    = MetodoReglaFalsa()
        resultado = self._calcular_seguro(metodo.calcular, funcion_str, a, b, tol)

        if "error" in resultado:
            self._mostrar_error_label(
                self.tabs_rf.tab("📊  Tabla de Iteraciones"),
                resultado["error"]
            )
            return

        filas = []
        for f in resultado["tabla_iteraciones"]:
            err_str = f"{f['Error (%)']:.6f}" if f['Error (%)'] is not None else "N/A"
            filas.append([
                f["Iteración"],
                f"{f['a']:.6f}", f"{f['b']:.6f}",
                f"{f['c']:.6f}", f"{f['f(c)']:.6f}", err_str,
            ])
        self._llenar_treeview(self.tree_rf, filas)

        tab_tabla = self.tabs_rf.tab("📊  Tabla de Iteraciones")
        self._limpiar_banners(tab_tabla)
        self._panel_resultado(tab_tabla, resultado["raiz_aproximada"],
                                    resultado["total_iteraciones"])

        self.dibujar_grafico(
            funcion_str, a, b,
            resultado["raiz_aproximada"],
            self.tabs_rf.tab("📈  Gráfica"),
            tipo_metodo="cerrado",
            metodo_nombre="Regla Falsa",
        )

    # ══════════════════════════════════════════
    #  ─────────── NEWTON-RAPHSON ─────────────
    # ══════════════════════════════════════════
    def mostrar_newton(self):
        self._vista_activa = self.mostrar_newton
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_newton)
        self._titulo("Método de Newton-Raphson", "⚡")

        self._label("Función  f(x):", 2, 0)
        self.entrada_funcion_nw = self._entry(2, 1, "Ej: exp(-x) - x", width=220)

        self._label("Valor Inicial  x₀:", 3, 0)
        self.entrada_x0_nw = self._entry(3, 1, "Ej: 1")

        self._label("Tolerancia (%):", 3, 2)
        self.entrada_tol_nw = self._entry(3, 3, "Ej: 0.5")

        self._entradas_actuales = [self.entrada_funcion_nw, self.entrada_x0_nw, self.entrada_tol_nw]
        self._boton_calcular("⚙️  Calcular Raíz", self.ejecutar_newton, row=4)
        self._boton_limpiar(row=4)

        self.tabs_nw = self._crear_tabs(row=5)
        self._set_tab_row(5)

        tab_tabla = self.tabs_nw.tab("📊  Tabla de Iteraciones")
        self.tree_nw = self._crear_treeview(
            tab_tabla,
            ["Iter", "xᵢ", "f(xᵢ)", "f'(xᵢ)", "Error (%)"]
        )
        self._tree_actual = self.tree_nw

    def ejecutar_newton(self):
        funcion_str = self.entrada_funcion_nw.get().strip()
        try:
            x0  = float(self.entrada_x0_nw.get())
            tol = float(self.entrada_tol_nw.get())
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_x0_nw, self.entrada_tol_nw)
            self._mostrar_error(self.tree_nw, "Ingresa números válidos en los campos.")
            return
        if not self._validar_tolerancia(tol, self.tree_nw):
            return
        if not self._validar_numeros(self.tree_nw, x0=x0):
            return

        metodo    = MetodoNewton()
        resultado = self._calcular_seguro(metodo.calcular, funcion_str, x0, tol)

        if "error" in resultado:
            self._mostrar_error_label(
            self.tabs_nw.tab("📊  Tabla de Iteraciones"),
            resultado["error"]
            )
            return

        filas = []
        for f in resultado["tabla_iteraciones"]:
            err_str = f"{f['Error (%)']:.6f}" if f['Error (%)'] is not None else "N/A"
            key_dfxi = "f'(xi)"
            dfxi_val = f"{f[key_dfxi]:.6f}"
            filas.append([
                f["Iteración"],
                f"{f['xi']:.6f}",
                f"{f['f(xi)']:.6f}",
                dfxi_val,
                err_str,
            ])
        self._llenar_treeview(self.tree_nw, filas)

        tab_tabla = self.tabs_nw.tab("📊  Tabla de Iteraciones")
        self._limpiar_banners(tab_tabla)
        self._panel_resultado(tab_tabla, resultado["raiz_aproximada"],
                              resultado["total_iteraciones"])

        self.dibujar_grafico(
            funcion_str, x0, x0,
            resultado["raiz_aproximada"],
            self.tabs_nw.tab("📈  Gráfica"),
            tipo_metodo="abierto",
            metodo_nombre="Newton-Raphson",
        )

    # ══════════════════════════════════════════
    #  ─────────── SECANTE ────────────────────
    # ══════════════════════════════════════════
    def mostrar_secante(self):
        self._vista_activa = self.mostrar_secante
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_secante)
        self._titulo("Método de la Secante", "📈")

        self._label("Función  f(x):", 2, 0)
        self.entrada_funcion_sec = self._entry(2, 1, "Ej: exp(-x) - x", width=220)

        self._label("Valor Inicial  x₀:", 3, 0)
        self.entrada_x0_sec = self._entry(3, 1, "Ej: 0")

        self._label("Valor Inicial  x₁:", 3, 2)
        self.entrada_x1_sec = self._entry(3, 3, "Ej: 1")

        self._label("Tolerancia (%):", 4, 0)
        self.entrada_tol_sec = self._entry(4, 1, "Ej: 0.5")

        self._entradas_actuales = [self.entrada_funcion_sec, self.entrada_x0_sec,
                                   self.entrada_x1_sec, self.entrada_tol_sec]
        self._boton_calcular("⚙️  Calcular Raíz", self.ejecutar_secante, row=5)
        self._boton_limpiar(row=5)

        self.tabs_sec = self._crear_tabs(row=6)
        self._set_tab_row(6)

        tab_tabla = self.tabs_sec.tab("📊  Tabla de Iteraciones")
        self.tree_sec = self._crear_treeview(
            tab_tabla,
            ["Iter", "xᵢ₋₁", "xᵢ", "f(xᵢ)", "Error (%)"]
        )
        self._tree_actual = self.tree_sec

    def ejecutar_secante(self):
        funcion_str = self.entrada_funcion_sec.get().strip()
        try:
            x0  = float(self.entrada_x0_sec.get())
            x1  = float(self.entrada_x1_sec.get())
            tol = float(self.entrada_tol_sec.get())
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_x0_sec, self.entrada_x1_sec, self.entrada_tol_sec)
            self._mostrar_error(self.tree_sec, "Ingresa números válidos en los campos.")
            return
        if not self._validar_tolerancia(tol, self.tree_sec):
            return
        if not self._validar_numeros(self.tree_sec, x0=x0, x1=x1):
            return

        metodo    = MetodoSecante()
        resultado = self._calcular_seguro(metodo.calcular, funcion_str, x0, x1, tol)

        if "error" in resultado:
            self._mostrar_error_label(
            self.tabs_sec.tab("📊  Tabla de Iteraciones"),
            resultado["error"]
            )
            return

        filas = []
        for f in resultado["tabla_iteraciones"]:
            xi_ant = f"{f['xi_anterior']:.6f}" if f['xi_anterior'] is not None else "N/A"
            err_str = f"{f['Error (%)']:.6f}" if f['Error (%)'] is not None else "N/A"
            filas.append([
                f["Iteración"],
                xi_ant,
                f"{f['xi']:.6f}",
                f"{f['f(xi)']:.6f}",
                err_str,
            ])
        self._llenar_treeview(self.tree_sec, filas)

        tab_tabla = self.tabs_sec.tab("📊  Tabla de Iteraciones")
        self._limpiar_banners(tab_tabla)
        self._panel_resultado(tab_tabla, resultado["raiz_aproximada"],
                              resultado["total_iteraciones"])

        self.dibujar_grafico(
            funcion_str, x0, x1,
            resultado["raiz_aproximada"],
            self.tabs_sec.tab("📈  Gráfica"),
            tipo_metodo="abierto",
            metodo_nombre="Secante",
        )

    # ══════════════════════════════════════════
    #  ─────────── PUNTO FIJO ─────────────────
    # ══════════════════════════════════════════
    def mostrar_punto_fijo(self):
        self._vista_activa = self.mostrar_punto_fijo
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_punto_fijo)
        self._titulo("Método de Punto Fijo", "🔄")

        self._label("Función  g(x):", 2, 0)
        self.entrada_funcion_pf = self._entry(2, 1, "Ej: exp(-x)", width=220)

        self._label("Valor Inicial  x₀:", 3, 0)
        self.entrada_x0_pf = self._entry(3, 1, "Ej: 0")

        self._label("Tolerancia (%):", 3, 2)
        self.entrada_tol_pf = self._entry(3, 3, "Ej: 0.5")

        self._entradas_actuales = [self.entrada_funcion_pf, self.entrada_x0_pf, self.entrada_tol_pf]
        self._boton_calcular("⚙️  Calcular Raíz", self.ejecutar_punto_fijo, row=4)
        self._boton_limpiar(row=4)

        self.tabs_pf = self._crear_tabs(row=5)
        self._set_tab_row(5)

        tab_tabla = self.tabs_pf.tab("📊  Tabla de Iteraciones")
        self.tree_pf = self._crear_treeview(
            tab_tabla,
            ["Iter", "xᵢ", "g(xᵢ)", "|g'(xᵢ)|", "Error (%)"]
        )
        self._tree_actual = self.tree_pf

    def ejecutar_punto_fijo(self):
        g_str = self.entrada_funcion_pf.get().strip()
        try:
            x0  = float(self.entrada_x0_pf.get())
            tol = float(self.entrada_tol_pf.get())
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_x0_pf, self.entrada_tol_pf)
            self._mostrar_error(self.tree_pf, "Ingresa números válidos en los campos.")
            return
        if not self._validar_tolerancia(tol, self.tree_pf):
            return
        if not self._validar_numeros(self.tree_pf, x0=x0):
            return

        metodo    = MetodoPuntoFijo()
        resultado = self._calcular_seguro(metodo.calcular, g_str, x0, tol)

        if "error" in resultado:
            self._mostrar_error_label(
            self.tabs_pf.tab("📊  Tabla de Iteraciones"),
            resultado["error"]
            )
            return

        filas = []
        for f in resultado["tabla_iteraciones"]:
            err_str = f"{f['Error (%)']:.6f}" if f['Error (%)'] is not None else "N/A"
            key_dg = "|g'(xi)|"
            dg_val = f"{f[key_dg]:.6f}"
            filas.append([
                f["Iteración"],
                f"{f['xi']:.6f}",
                f"{f['g(xi)']:.6f}",
                dg_val,
                err_str,
            ])
        self._llenar_treeview(self.tree_pf, filas)

        tab_tabla = self.tabs_pf.tab("📊  Tabla de Iteraciones")
        self._limpiar_banners(tab_tabla)
        self._panel_resultado(tab_tabla, resultado["raiz_aproximada"],
                              resultado["total_iteraciones"])

        funcion_grafica = f"({g_str}) - x"
        self.dibujar_grafico(
            funcion_grafica, x0, x0,
            resultado["raiz_aproximada"],
            self.tabs_pf.tab("📈  Gráfica"),
            tipo_metodo="abierto",
            metodo_nombre="Punto Fijo  —  g(x) - x",
        )

    # ══════════════════════════════════════════
    #  ─────────── MÉTODO MÜLLER ──────────────
    # ══════════════════════════════════════════
    def mostrar_muller(self):
        self._vista_activa = self.mostrar_muller
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_muller)
        self._titulo("Método de Müller", "🧮")

        # Fila 2: Función
        self._label("Polinomio f(x):", 2, 0)
        self.entrada_funcion_mul = self._entry(2, 1, "Ej: 4*x**3 + 2*x**2 - 2*x + 3", width=220)

        # Fila 3: Valores Iniciales x0, x1
        self._label("Valor x₀:", 3, 0)
        self.entrada_x0_mul = self._entry(3, 1, "Ej: -1.50")

        self._label("Valor x₁:", 3, 2)
        self.entrada_x1_mul = self._entry(3, 3, "Ej: -1.45")

        # Fila 4: Valor Inicial x2 y Tolerancia
        self._label("Valor x₂:", 4, 0)
        self.entrada_x2_mul = self._entry(4, 1, "Ej: -1.40")

        self._label("Tolerancia (%):", 4, 2)
        self.entrada_tol_mul = self._entry(4, 3, "Ej: 0.01")

        self._entradas_actuales = [
            self.entrada_funcion_mul, self.entrada_x0_mul,
            self.entrada_x1_mul, self.entrada_x2_mul, self.entrada_tol_mul
        ]

        # Botón
        self._boton_calcular("⚙️  Calcular Raíz", self.ejecutar_muller, row=5)
        self._boton_limpiar(row=5)

        # Tabs y Tabla
        self.tabs_mul = self._crear_tabs(row=6)
        self._set_tab_row(6)

        tab_tabla = self.tabs_mul.tab("📊  Tabla de Iteraciones")
        self.tree_mul = self._crear_treeview(
            tab_tabla,
            ["Iter", "x₀", "x₁", "x₂", "x₃ (Nueva Raíz)", "Error (%)"]
        )
        self._tree_actual = self.tree_mul

    def ejecutar_muller(self):
        funcion_str = self.entrada_funcion_mul.get().strip()
        try:
            x0  = float(self.entrada_x0_mul.get())
            x1  = float(self.entrada_x1_mul.get())
            x2  = float(self.entrada_x2_mul.get())
            tol = float(self.entrada_tol_mul.get())
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_x0_mul, self.entrada_x1_mul,
                                             self.entrada_x2_mul, self.entrada_tol_mul)
            self._mostrar_error(self.tree_mul, "Ingresa números válidos en todos los campos.")
            return
        if not self._validar_tolerancia(tol, self.tree_mul):
            return
        if not self._validar_numeros(self.tree_mul, x0=x0, x1=x1, x2=x2):
            return

        metodo    = MetodoMuller()
        resultado = self._calcular_seguro(metodo.calcular, funcion_str, x0, x1, x2, tol)

        if "error" in resultado:
            self._mostrar_error_label(self.tabs_mul.tab("📊  Tabla de Iteraciones"), resultado["error"])
            return

        # Llenar el Treeview
        filas = []
        for f in resultado["tabla_iteraciones"]:
            err_str = f"{f['Error (%)']:.6f}" if f['Error (%)'] is not None else "N/A"
            filas.append([
                f["Iteración"],
                f["x0"], f["x1"], f["x2"], f["x3"],
                err_str,
            ])
        self._llenar_treeview(self.tree_mul, filas)

        # Banner de Resultados
        tab_tabla = self.tabs_mul.tab("📊  Tabla de Iteraciones")
        self._limpiar_banners(tab_tabla)

        # Extraemos la parte real para que no choque con el float que espera _panel_resultado
        raiz_aprox = resultado["raiz_aproximada"]
        raiz_float = raiz_aprox.real if isinstance(raiz_aprox, complex) else float(raiz_aprox)

        self._panel_resultado(tab_tabla, raiz_float, resultado["total_iteraciones"])

        # Dibujar Gráfica
        self.dibujar_grafico(
            funcion_str, min(x0, x1, x2), max(x0, x1, x2),
            raiz_float,
            self.tabs_mul.tab("📈  Gráfica"),
            tipo_metodo="abierto",
            metodo_nombre="Método de Müller"
        )

    # ══════════════════════════════════════════
    #  ─────────── MÉTODO BAIRSTOW ────────────
    # ══════════════════════════════════════════
    def mostrar_bairstow(self):
        self._vista_activa = self.mostrar_bairstow
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_bairstow)
        self._titulo("Método de Bairstow", "✂️")

        # Fila 2: Función
        self._label("Polinomio f(x):", 2, 0)
        self.entrada_funcion_bai = self._entry(2, 1, "Ej: x**3 + 3*x**2 - x - 3", width=220)

        # Fila 3: Valores Iniciales r, s
        self._label("Valor r₀:", 3, 0)
        self.entrada_r0_bai = self._entry(3, 1, "Ej: -0.333")

        self._label("Valor s₀:", 3, 2)
        self.entrada_s0_bai = self._entry(3, 3, "Ej: -1")

        # Fila 4: Tolerancia
        self._label("Tolerancia (%):", 4, 0)
        self.entrada_tol_bai = self._entry(4, 1, "Ej: 0.01")

        self._entradas_actuales = [
            self.entrada_funcion_bai, self.entrada_r0_bai,
            self.entrada_s0_bai, self.entrada_tol_bai
        ]

        # Botón
        self._boton_calcular("⚙️  Calcular Raíces", self.ejecutar_bairstow, row=5)
        self._boton_limpiar(row=5)

        # Tabs y Tabla
        self.tabs_bai = self._crear_tabs(row=6)
        self._set_tab_row(6)

        tab_tabla = self.tabs_bai.tab("📊  Tabla de Iteraciones")
        self.tree_bai = self._crear_treeview(
            tab_tabla,
            ["Iter", "r", "s", "Δr", "Δs", "Error Máx (%)"]
        )
        self._tree_actual = self.tree_bai

    def ejecutar_bairstow(self):
        funcion_str = self.entrada_funcion_bai.get().strip()
        try:
            r0  = float(self.entrada_r0_bai.get())
            s0  = float(self.entrada_s0_bai.get())
            tol = float(self.entrada_tol_bai.get())
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_r0_bai, self.entrada_s0_bai, self.entrada_tol_bai)
            self._mostrar_error(self.tree_bai, "Ingresa números válidos en todos los campos.")
            return
        if not self._validar_tolerancia(tol, self.tree_bai):
            return
        if not self._validar_numeros(self.tree_bai, r0=r0, s0=s0):
            return

        metodo    = MetodoBairstow()
        resultado = self._calcular_seguro(metodo.calcular, funcion_str, r0, s0, tol)

        if "error" in resultado:
            self._mostrar_error_label(self.tabs_bai.tab("📊  Tabla de Iteraciones"), resultado["error"])
            return

        # Llenar el Treeview
        filas = []
        for f in resultado["tabla_iteraciones"]:
            err_str = f"{f['Error Máx (%)']:.6f}" if f['Error Máx (%)'] is not None else "N/A"
            filas.append([
                f["Iteración"],
                f"{f['r']:.6f}", f"{f['s']:.6f}",
                f"{f['Δr']:.6f}", f"{f['Δs']:.6f}",
                err_str,
            ])
        self._llenar_treeview(self.tree_bai, filas)

        # Banner de Resultados
        tab_tabla = self.tabs_bai.tab("📊  Tabla de Iteraciones")
        self._limpiar_banners(tab_tabla)

        # Como Bairstow encuentra dos raíces simultáneamente, creamos un texto para mostrarlas
        r1 = resultado["raiz1"]
        r2 = resultado["raiz2"]
        texto_raiz = f"x₁= {r1}  |  x₂= {r2}"

        self._panel_resultado(tab_tabla, texto_raiz, resultado["total_iteraciones"])

        # Para el gráfico, tomamos la parte real de la primera raíz como guía visual
        raiz_grafico = r1.real if isinstance(r1, complex) else r1

        self.dibujar_grafico(
            funcion_str, raiz_grafico - 2, raiz_grafico + 2,
            raiz_grafico,
            self.tabs_bai.tab("📈  Gráfica"),
            tipo_metodo="abierto",
            metodo_nombre="Método de Bairstow"
        )

    # ══════════════════════════════════════════
    #  ─────────── HORNER-NEWTON ──────────────
    # ══════════════════════════════════════════
    def mostrar_horner(self):
        self._vista_activa = self.mostrar_horner
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_horner)
        self._titulo("Método de Horner-Newton", "📝")

        # Fila 2: Función
        self._label("Polinomio f(x):", 2, 0)
        self.entrada_funcion_hn = self._entry(2, 1, "Ej: x**3 - 2*x - 5", width=220)

        # Fila 3: Valor Inicial y Tolerancia
        self._label("Valor Inicial x₀:", 3, 0)
        self.entrada_x0_hn = self._entry(3, 1, "Ej: 2")

        self._label("Tolerancia (%):", 3, 2)
        self.entrada_tol_hn = self._entry(3, 3, "Ej: 0.01")

        self._entradas_actuales = [self.entrada_funcion_hn, self.entrada_x0_hn, self.entrada_tol_hn]

        # Botón
        self._boton_calcular("⚙️  Calcular Raíz", self.ejecutar_horner, row=4)
        self._boton_limpiar(row=4)

        # Tabs y Tabla
        self.tabs_hn = self._crear_tabs(row=5)
        self._set_tab_row(5)

        tab_tabla = self.tabs_hn.tab("📊  Tabla de Iteraciones")
        self.tree_hn = self._crear_treeview(
            tab_tabla,
            ["Iter", "xᵢ", "P(xᵢ) [bₙ]", "P'(xᵢ) [cₙ₋₁]", "Error (%)"]
        )
        self._tree_actual = self.tree_hn

    def ejecutar_horner(self):
        funcion_str = self.entrada_funcion_hn.get().strip()
        try:
            x0  = float(self.entrada_x0_hn.get())
            tol = float(self.entrada_tol_hn.get())
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_x0_hn, self.entrada_tol_hn)
            self._mostrar_error(self.tree_hn, "Ingresa números válidos en todos los campos.")
            return
        if not self._validar_tolerancia(tol, self.tree_hn):
            return
        if not self._validar_numeros(self.tree_hn, x0=x0):
            return

        metodo = MetodoHornerNewton()
        resultado = self._calcular_seguro(metodo.calcular, funcion_str, x0, tol)

        if "error" in resultado:
            self._mostrar_error_label(self.tabs_hn.tab("📊  Tabla de Iteraciones"), resultado["error"])
            return

        # Llenar el Treeview
        filas = []
        for f in resultado["tabla_iteraciones"]:
            err_str = f"{f['Error (%)']:.6f}" if f['Error (%)'] is not None else "N/A"
            filas.append([
                f["Iteración"],
                f"{f['xi']:.6f}",
                f"{f['P(xi) [bn]']:.6f}",
                f"{f['P\'(xi) [cn-1]']:.6f}",
                err_str,
            ])
        self._llenar_treeview(self.tree_hn, filas)

        # Banner de Resultados
        tab_tabla = self.tabs_hn.tab("📊  Tabla de Iteraciones")
        self._limpiar_banners(tab_tabla)
        self._panel_resultado(tab_tabla, resultado["raiz_aproximada"], resultado["total_iteraciones"])

        # Dibujar Gráfica
        self.dibujar_grafico(
            funcion_str, x0, x0,
            resultado["raiz_aproximada"],
            self.tabs_hn.tab("📈  Gráfica"),
            tipo_metodo="abierto",
            metodo_nombre="Método de Horner-Newton"
        )

    # ══════════════════════════════════════════
    #  ─────────── MÉTODOS AVANZADOS ──────────
    # ══════════════════════════════════════════
    def mostrar_avanzados(self):
        self._vista_activa = self.mostrar_avanzados
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_avanzados)
        self._titulo("Métodos avanzados", "🧩")

        metodos = [
            ("Factorización LU", self.mostrar_lu),
            ("Gauss-Jordan", self.mostrar_gauss_jordan),
            ("Jacobi", self.mostrar_jacobi),
            ("Rouché-Frobenius", self.mostrar_rouche),
            ("Regresión cuadrática", self.mostrar_regresion_cuadratica),
            ("Mínimos cuadrados", self.mostrar_minimos_cuadrados),
            ("Newton dif. divididas", self.mostrar_diferencias_divididas),
            ("Interpolación", self.mostrar_interpolacion),
            ("Newton SENL", self.mostrar_newton_senl),
        ]

        cont = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        cont.grid(row=2, column=0, columnspan=4, padx=24, pady=18, sticky="nsew")
        for i, (texto, comando) in enumerate(metodos):
            btn = ctk.CTkButton(
                cont,
                text=texto,
                command=comando,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                fg_color=self._t("bg_card2"),
                hover_color=self._t("accent_hover"),
                text_color=self._t("text_primary"),
                height=52,
                corner_radius=8,
            )
            btn.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="ew")
        for col in range(3):
            cont.grid_columnconfigure(col, weight=1)

    def _abrir_metodo_avanzado(self, titulo, icono):
        self._vista_activa = lambda: self._abrir_metodo_avanzado(titulo, icono)
        self.limpiar_frame_principal()
        self._set_btn_activo(self.btn_avanzados)
        self._titulo(titulo, icono)
        ctk.CTkButton(
            self.frame_principal,
            text="← Volver a métodos avanzados",
            command=self.mostrar_avanzados,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=self._t("bg_card2"),
            hover_color=self._t("accent_hover"),
            text_color=self._t("text_primary"),
            height=34,
            width=220,
            corner_radius=8,
        ).grid(row=2, column=0, padx=24, pady=(0, 8), sticky="w")

    def mostrar_lu(self):
        self._abrir_metodo_avanzado("Factorización LU", "🧮")
        self._vista_activa = self.mostrar_lu
        self._label("Matriz A:", 3, 0)
        self.txt_lu_a = self._textbox(3, 1, "2 1 -1\n-3 -1 2\n-2 1 2", height=92, colspan=1)
        self._label("Vector b:", 3, 2)
        self.txt_lu_b = self._textbox(3, 3, "8\n-11\n-3", width=160, height=92)
        self._boton_calcular("Calcular LU", self.ejecutar_lu, row=4)
        self._boton_limpiar(row=4)
        self._entradas_actuales = [self.txt_lu_a, self.txt_lu_b]
        self.tabs_lu = self._crear_tabs_resultado(row=5)
        self._set_tab_row(5)

    def ejecutar_lu(self):
        resultado = MetodoLU().calcular(self.txt_lu_a.get("1.0", "end"), self.txt_lu_b.get("1.0", "end"))
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_lu.tab("📋  Resultado"), resultado["error"])
            return
        resumen = "x = [" + ", ".join(resultado["solucion"]) + "]"
        detalle = "\n\n".join([
            self._matriz_a_texto("P =", resultado["P"]),
            self._matriz_a_texto("L =", resultado["L"]),
            self._matriz_a_texto("U =", resultado["U"]),
            "y = [" + ", ".join(resultado["y"]) + "]",
            resumen,
        ])
        self._mostrar_resultado_avanzado(self.tabs_lu, resumen, detalle)

    def mostrar_gauss_jordan(self):
        self._abrir_metodo_avanzado("Método de Gauss-Jordan", "🧾")
        self._vista_activa = self.mostrar_gauss_jordan
        self._label("Matriz A:", 3, 0)
        self.txt_gj_a = self._textbox(3, 1, "2 1 -1\n-3 -1 2\n-2 1 2", height=92)
        self._label("Vector b:", 3, 2)
        self.txt_gj_b = self._textbox(3, 3, "8\n-11\n-3", width=160, height=92)
        self._boton_calcular("Calcular Gauss-Jordan", self.ejecutar_gauss_jordan, row=4)
        self._boton_limpiar(row=4)
        self._entradas_actuales = [self.txt_gj_a, self.txt_gj_b]
        self.tabs_gj = self._crear_tabs_resultado(row=5)
        self._set_tab_row(5)

    def ejecutar_gauss_jordan(self):
        resultado = MetodoGaussJordan().calcular(self.txt_gj_a.get("1.0", "end"), self.txt_gj_b.get("1.0", "end"))
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_gj.tab("📋  Resultado"), resultado["error"])
            return
        resumen = resultado["tipo"]
        if resultado["solucion"]:
            resumen += "\n\nx = [" + ", ".join(resultado["solucion"]) + "]"
        detalle = resumen + "\n\n" + self._matriz_a_texto("Matriz reducida =", resultado["rref"])
        self._mostrar_resultado_avanzado(self.tabs_gj, resumen, detalle)

    def mostrar_jacobi(self):
        self._abrir_metodo_avanzado("Método de Jacobi", "🔁")
        self._vista_activa = self.mostrar_jacobi
        self._label("Matriz A:", 3, 0)
        self.txt_jac_a = self._textbox(3, 1, "10 -1 2\n-1 11 -1\n2 -1 10", height=92)
        self._label("Vector b:", 3, 2)
        self.txt_jac_b = self._textbox(3, 3, "6\n25\n-11", width=160, height=92)
        self._label("x0:", 4, 0)
        self.txt_jac_x0 = self._textbox(4, 1, "0 0 0", height=42)
        self._label("Tol / Iter:", 4, 2)
        self.entrada_jac_tol = self._entry(4, 3, "0.01", width=80)
        self._label("Iter:", 5, 2)
        self.entrada_jac_iter = self._entry(5, 3, "100", width=80)
        self._boton_calcular("Calcular Jacobi", self.ejecutar_jacobi, row=6)
        self._boton_limpiar(row=6)
        self._entradas_actuales = [self.txt_jac_a, self.txt_jac_b, self.txt_jac_x0,
                                   self.entrada_jac_tol, self.entrada_jac_iter]
        self.tabs_jac = self._crear_tabs_resultado(row=7)
        self._set_tab_row(7)

    def ejecutar_jacobi(self):
        try:
            tol = float(self.entrada_jac_tol.get())
            max_iter = int(float(self.entrada_jac_iter.get()))
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_jac_tol, self.entrada_jac_iter)
            self._mostrar_error_label(self.tabs_jac.tab("📋  Resultado"), "La tolerancia e iteraciones deben ser numéricas.")
            return
        resultado = MetodoJacobi().calcular(
            self.txt_jac_a.get("1.0", "end"),
            self.txt_jac_b.get("1.0", "end"),
            self.txt_jac_x0.get("1.0", "end"),
            tol,
            max_iter,
        )
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_jac.tab("📋  Resultado"), resultado["error"])
            return
        resumen = ""
        if resultado["advertencia"]:
            resumen += resultado["advertencia"] + "\n\n"
        resumen += "x = [" + ", ".join(resultado["solucion"]) + "]"
        detalle = resumen + "\n\nIteraciones:\n"
        detalle += "\n".join("  " + " | ".join(map(str, fila)) for fila in resultado["iteraciones"])
        self._mostrar_resultado_avanzado(self.tabs_jac, resumen, detalle)

    def mostrar_rouche(self):
        self._abrir_metodo_avanzado("Teorema Rouché-Frobenius", "🧠")
        self._vista_activa = self.mostrar_rouche
        self._label("Matriz A:", 3, 0)
        self.txt_rouche_a = self._textbox(3, 1, "1 1 1\n2 2 2\n1 -1 0", height=92)
        self._label("Vector b:", 3, 2)
        self.txt_rouche_b = self._textbox(3, 3, "6\n12\n1", width=160, height=92)
        self._boton_calcular("Analizar sistema", self.ejecutar_rouche, row=4)
        self._boton_limpiar(row=4)
        self._entradas_actuales = [self.txt_rouche_a, self.txt_rouche_b]
        self.tabs_rouche = self._crear_tabs_resultado(row=5)
        self._set_tab_row(5)

    def ejecutar_rouche(self):
        resultado = MetodoRoucheFrobenius().calcular(self.txt_rouche_a.get("1.0", "end"), self.txt_rouche_b.get("1.0", "end"))
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_rouche.tab("📋  Resultado"), resultado["error"])
            return
        resumen = resultado["conclusion"]
        detalle = (
            f"Rango(A) = {resultado['rango_a']}\n"
            f"Rango(A|b) = {resultado['rango_aug']}\n"
            f"Incógnitas = {resultado['incognitas']}\n\n"
            f"{resumen}"
        )
        self._mostrar_resultado_avanzado(self.tabs_rouche, resumen, detalle)

    def mostrar_regresion_cuadratica(self):
        self._abrir_metodo_avanzado("Regresión cuadrática", "📈")
        self._vista_activa = self.mostrar_regresion_cuadratica
        self._label("Puntos x,y:", 3, 0)
        self.txt_reg_puntos = self._textbox(3, 1, "0 1\n1 2.2\n2 5.1\n3 10.2\n4 17.1", height=120, colspan=2)
        self._boton_calcular("Calcular regresión", self.ejecutar_regresion_cuadratica, row=4)
        self._boton_limpiar(row=4)
        self._entradas_actuales = [self.txt_reg_puntos]
        self.tabs_reg = self._crear_tabs_resultado(row=5)
        self._set_tab_row(5)

    def ejecutar_regresion_cuadratica(self):
        resultado = MetodoRegresionCuadratica().calcular(self.txt_reg_puntos.get("1.0", "end"))
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_reg.tab("📋  Resultado"), resultado["error"])
            return
        resumen = f"{resultado['ecuacion']}\nR^2 = {resultado['r2']}"
        detalle = resumen + "\n\nx | y | y_estimado | residuo\n"
        detalle += "\n".join(" | ".join(fila) for fila in resultado["tabla"])
        self._mostrar_resultado_avanzado(self.tabs_reg, resumen, detalle)

    def mostrar_minimos_cuadrados(self):
        self._abrir_metodo_avanzado("Mínimos cuadrados", "📉")
        self._vista_activa = self.mostrar_minimos_cuadrados
        self._label("Puntos x,y:", 3, 0)
        self.txt_mc_puntos = self._textbox(3, 1, "0 1\n1 2.2\n2 5.1\n3 10.2\n4 17.1", height=120, colspan=2)
        self._label("Grado:", 3, 2)
        self.entrada_mc_grado = self._entry(3, 3, "2", width=80)
        self._boton_calcular("Ajustar curva", self.ejecutar_minimos_cuadrados, row=5)
        self._boton_limpiar(row=5)
        self._entradas_actuales = [self.txt_mc_puntos, self.entrada_mc_grado]
        self.tabs_mc = self._crear_tabs_resultado(row=6)
        self._set_tab_row(6)

    def ejecutar_minimos_cuadrados(self):
        resultado = MetodoMinimosCuadrados().calcular(self.txt_mc_puntos.get("1.0", "end"), self.entrada_mc_grado.get())
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_mc.tab("📋  Resultado"), resultado["error"])
            return
        resumen = f"{resultado['ecuacion']}\nR^2 = {resultado['r2']}"
        detalle = resumen + "\n\nx | y | y_estimado | residuo\n"
        detalle += "\n".join(" | ".join(fila) for fila in resultado["tabla"])
        self._mostrar_resultado_avanzado(self.tabs_mc, resumen, detalle)

    def mostrar_diferencias_divididas(self):
        self._abrir_metodo_avanzado("Newton por diferencias divididas", "🧮")
        self._vista_activa = self.mostrar_diferencias_divididas
        self._label("Puntos x,y:", 3, 0)
        self.txt_dd_puntos = self._textbox(3, 1, "0 1\n1 3\n2 2\n4 5", height=120, colspan=2)
        self._label("Evaluar x:", 3, 2)
        self.entrada_dd_eval = self._entry(3, 3, "3", width=80)
        self._boton_calcular("Interpolar", self.ejecutar_diferencias_divididas, row=5)
        self._boton_limpiar(row=5)
        self._entradas_actuales = [self.txt_dd_puntos, self.entrada_dd_eval]
        self.tabs_dd = self._crear_tabs_resultado(row=6)
        self._set_tab_row(6)

    def ejecutar_diferencias_divididas(self):
        resultado = MetodoNewtonDiferenciasDivididas().calcular(
            self.txt_dd_puntos.get("1.0", "end"),
            self.entrada_dd_eval.get(),
        )
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_dd.tab("📋  Resultado"), resultado["error"])
            return
        resumen = "Polinomio:\n" + resultado["polinomio"]
        if resultado["valor"] is not None:
            resumen += "\n\nValor evaluado = " + resultado["valor"]
        detalle = resumen + "\n\nCoeficientes:\n[" + ", ".join(resultado["coeficientes"]) + "]"
        detalle += "\n\nTabla de diferencias divididas:\n"
        detalle += "\n".join(" | ".join(fila) for fila in resultado["tabla"])
        self._mostrar_resultado_avanzado(self.tabs_dd, resumen, detalle)

    def mostrar_interpolacion(self):
        self._abrir_metodo_avanzado("Interpolación de funciones", "📌")
        self._vista_activa = self.mostrar_interpolacion
        self._label("Puntos x,y:", 3, 0)
        self.txt_int_puntos = self._textbox(3, 1, "0 1\n1 3\n2 2\n4 5", height=120, colspan=2)
        self._label("Evaluar x:", 3, 2)
        self.entrada_int_eval = self._entry(3, 3, "3", width=80)
        self._boton_calcular("Interpolar", self.ejecutar_interpolacion, row=5)
        self._boton_limpiar(row=5)
        self._entradas_actuales = [self.txt_int_puntos, self.entrada_int_eval]
        self.tabs_int = self._crear_tabs_resultado(row=6)
        self._set_tab_row(6)

    def ejecutar_interpolacion(self):
        resultado = MetodoInterpolacionLagrange().calcular(
            self.txt_int_puntos.get("1.0", "end"),
            self.entrada_int_eval.get(),
        )
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_int.tab("📋  Resultado"), resultado["error"])
            return
        resumen = "Polinomio interpolante:\n" + resultado["polinomio"]
        if resultado["valor"] is not None:
            resumen += "\n\nValor evaluado = " + resultado["valor"]
        self._mostrar_resultado_avanzado(self.tabs_int, resumen, resumen)

    def mostrar_newton_senl(self):
        self._abrir_metodo_avanzado("Newton para SENL", "🧬")
        self._vista_activa = self.mostrar_newton_senl
        self._label("Ecuaciones:", 3, 0)
        self.txt_senl_ecs = self._textbox(3, 1, "x**2 + y**2 - 4\nx - y - 1", height=92)
        self._label("Variables:", 3, 2)
        self.entrada_senl_vars = self._entry(3, 3, "x,y", width=120)
        self._label("x0:", 4, 0)
        self.txt_senl_x0 = self._textbox(4, 1, "1.5 0.5", height=42)
        self._label("Tol / Iter:", 4, 2)
        self.entrada_senl_tol = self._entry(4, 3, "0.01", width=80)
        self._label("Iter:", 5, 2)
        self.entrada_senl_iter = self._entry(5, 3, "50", width=80)
        self._boton_calcular("Calcular Newton SENL", self.ejecutar_newton_senl, row=6)
        self._boton_limpiar(row=6)
        self._entradas_actuales = [
            self.txt_senl_ecs, self.entrada_senl_vars,
            self.txt_senl_x0, self.entrada_senl_tol, self.entrada_senl_iter
        ]
        self.tabs_senl = self._crear_tabs_resultado(row=7)
        self._set_tab_row(7)

    def ejecutar_newton_senl(self):
        try:
            tol = float(self.entrada_senl_tol.get())
            max_iter = int(float(self.entrada_senl_iter.get()))
        except ValueError:
            self._detectar_entries_invalidas(self.entrada_senl_tol, self.entrada_senl_iter)
            self._mostrar_error_label(self.tabs_senl.tab("📋  Resultado"), "La tolerancia e iteraciones deben ser numéricas.")
            return
        resultado = MetodoNewtonSENL().calcular(
            self.txt_senl_ecs.get("1.0", "end"),
            self.entrada_senl_vars.get(),
            self.txt_senl_x0.get("1.0", "end"),
            tol,
            max_iter,
        )
        if "error" in resultado:
            self._mostrar_error_label(self.tabs_senl.tab("📋  Resultado"), resultado["error"])
            return
        pares = [f"{var} = {val}" for var, val in zip(resultado["variables"], resultado["solucion"])]
        resumen = "Solución:\n" + "\n".join(pares)
        detalle = resumen + "\n\nIteraciones:\n"
        detalle += "\n".join("  " + " | ".join(map(str, fila)) for fila in resultado["iteraciones"])
        self._mostrar_resultado_avanzado(self.tabs_senl, resumen, detalle)

    # ──────────────────────────────────────────
    #  HELPERS DE ERROR
    # ──────────────────────────────────────────
    def _validar_tolerancia(self, tolerancia: float, tree: ttk.Treeview) -> bool:
        if not math.isfinite(tolerancia) or tolerancia <= 0:
            self._mostrar_error(tree, "La tolerancia debe ser un número mayor que 0.")
            return False
        return True

    def _validar_numeros(self, tree: ttk.Treeview, **valores) -> bool:
        for nombre, valor in valores.items():
            if not math.isfinite(valor):
                self._mostrar_error(
                    tree,
                    f"El valor {nombre} debe ser un número real finito. Evita nan, inf o -inf."
                )
                return False
        return True

    def _calcular_seguro(self, funcion_calculo, *args):
        try:
            return funcion_calculo(*args)
        except ZeroDivisionError:
            return {"error": "Se produjo una división entre cero durante el cálculo."}
        except OverflowError:
            return {"error": "El cálculo produjo un número demasiado grande para representarse."}
        except ValueError as e:
            return {"error": f"Error matemático al evaluar la función: {e}"}
        except Exception as e:
            return {"error": f"Error inesperado durante el cálculo: {e}"}

    def _mensaje_con_sugerencia(self, mensaje: str) -> str:
        texto = str(mensaje)
        lower = texto.lower()

        if "parse" in lower or "syntax" in lower or "interpretar" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: revisa la sintaxis. Usa x como variable, ** para potencias, "
                "log(x) para ln(x), y funciones como sin(x), cos(x), tan(x), exp(x)."
            )
        if "división entre cero" in lower or "division" in lower or "zero" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: cambia el valor inicial o el intervalo para evitar evaluar "
                "la función en un punto donde el denominador sea 0."
            )
        if "intervalo" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: elige a y b de forma que f(a) y f(b) tengan signos opuestos."
            )
        if "derivada" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: prueba otro valor inicial donde la derivada no sea 0."
            )
        if "diverge" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: cambia los valores iniciales, usa una tolerancia razonable "
                "o prueba un método más adecuado para esa función."
            )
        if "determinante" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: cambia los valores iniciales para evitar un sistema singular."
            )
        if ("matriz" in lower or "vector" in lower) and "singular" not in lower and "jacobiana" not in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: escribe matrices por filas, separando números con espacios. "
                "Ejemplo: 2 1 -1 en una fila, y asegúrate de que las dimensiones coincidan."
            )
        if "puntos" in lower or "punto" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: escribe un punto por fila en formato x y, por ejemplo: 0 1. "
                "No repitas valores de x en interpolación."
            )
        if "diagonal" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: reordena las ecuaciones para evitar ceros en la diagonal o usa otro método."
            )
        if "singular" in lower or "jacobiana" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: cambia los valores iniciales o revisa si el sistema tiene dependencia entre ecuaciones."
            )
        if "iteraciones" in lower or "grado" in lower or "tolerancia" in lower:
            return (
                f"{texto}\n\n"
                "Cómo solucionarlo: usa tolerancia mayor que 0, iteraciones enteras positivas y grados enteros válidos."
            )
        return texto

    def _mostrar_error_label(self, parent, mensaje: str):
        self._limpiar_banners(parent)
        mensaje = self._mensaje_con_sugerencia(mensaje)

        lbl = ctk.CTkLabel(
            parent,
            text=f"⚠️  {mensaje}",
            text_color=self._t("accent"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            wraplength=900,
            justify="center",
        )
        lbl._mensaje_temporal = True
        lbl.pack(pady=20)

    def _mostrar_error(self, tree: ttk.Treeview, mensaje: str):
        tree.delete(*tree.get_children())
        tree.insert("", "end", values=[mensaje] + [""] * 5)

    def _limpiar_banners(self, tab):
        """Elimina mensajes anteriores de error o resultado."""
        for child in tab.winfo_children():
            if getattr(child, "_mensaje_temporal", False):
                child.destroy()


# ═══════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.mainloop()
