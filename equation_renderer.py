"""
equation_renderer.py
====================
Módulo de visualización matemática rica para NumSolver.
Usa matplotlib embebido en customtkinter para mostrar:
  • Matrices con bordes y colores
  • Polinomios en notación LaTeX (mathtext)
  • Pasos de transformación numerados
  • Gráficas de convergencia
  • Tablas de iteraciones coloreadas
"""
from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from tkinter import ttk

# ─────────────────────────────────────────────────────────────────
#  PALETAS DE COLORES (dark / light)
# ─────────────────────────────────────────────────────────────────

DARK: dict = {
    'fig_bg':   '#1a1a1a',
    'ax_bg':    '#202020',
    'card':     '#252525',
    'card2':    '#2c2c2c',
    'border':   '#333333',
    'accent':   '#ff2244',
    'success':  '#22c55e',
    'warning':  '#f59e0b',
    'info':     '#60a5fa',
    'purple':   '#a78bfa',
    'text':     '#f0f0f0',
    'text_dim': '#777777',
    'tbl_odd':  '#1e1e1e',
    'tbl_even': '#242424',
    'tbl_diag': '#1a2422',
    'tbl_aug':  '#1a1a2e',
    'tbl_head': '#1e2040',
    'tbl_edge': '#303030',
}

LIGHT: dict = {
    'fig_bg':   '#f3f4f6',
    'ax_bg':    '#ffffff',
    'card':     '#ffffff',
    'card2':    '#f9fafb',
    'border':   '#e5e7eb',
    'accent':   '#dc2626',
    'success':  '#16a34a',
    'warning':  '#d97706',
    'info':     '#2563eb',
    'purple':   '#7c3aed',
    'text':     '#111827',
    'text_dim': '#6b7280',
    'tbl_odd':  '#ffffff',
    'tbl_even': '#f9fafb',
    'tbl_diag': '#f0fdf4',
    'tbl_aug':  '#eff6ff',
    'tbl_head': '#dbeafe',
    'tbl_edge': '#d1d5db',
}


def _th(dark: bool) -> dict:
    return DARK if dark else LIGHT


# ─────────────────────────────────────────────────────────────────
#  UTILIDADES
# ─────────────────────────────────────────────────────────────────

def _fmt(v, digits: int = 5) -> str:
    """Formatea un valor numérico para mostrarlo en tablas."""
    try:
        f = float(v)
        if abs(f) < 1e-10:
            return '0'
        if f == int(f) and abs(f) < 1e6:
            return str(int(f))
        return f'{f:.{digits}g}'
    except (TypeError, ValueError):
        return str(v)


def _clear(tab) -> None:
    """Destruye todos los hijos de un frame / tab."""
    for child in tab.winfo_children():
        child.destroy()


def _scrollable(parent, dark: bool) -> ctk.CTkScrollableFrame:
    """Crea un frame con scroll vertical que llena el espacio disponible."""
    t = _th(dark)
    sf = ctk.CTkScrollableFrame(
        parent,
        fg_color=t['fig_bg'],
        label_text='',
        scrollbar_button_color=t['border'],
        scrollbar_button_hover_color=t['accent'],
    )
    sf.pack(fill='both', expand=True)
    return sf


# ─────────────────────────────────────────────────────────────────
#  WIDGETS CUSTOMTKINTER (banners, headers, labels)
# ─────────────────────────────────────────────────────────────────

def _hdr(parent, title: str, icon: str, dark: bool, color: str = 'info') -> None:
    """Encabezado de sección con borde e ícono."""
    t = _th(dark)
    f = ctk.CTkFrame(parent, fg_color=t['card2'], corner_radius=8,
                     border_width=1, border_color=t['border'])
    f.pack(fill='x', padx=10, pady=(10, 2))
    ctk.CTkLabel(
        f,
        text=f'{icon}  {title}',
        font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'),
        text_color=t[color],
    ).pack(anchor='w', padx=12, pady=7)


def _banner(parent, label: str, value: str, dark: bool,
            color: str = 'success') -> None:
    """Card de resultado con borde de color y valor en monoespaciado."""
    t = _th(dark)
    c = t[color]
    outer = ctk.CTkFrame(parent, fg_color=c, corner_radius=10)
    outer.pack(fill='x', padx=10, pady=4)
    inner = ctk.CTkFrame(outer, fg_color=t['card'], corner_radius=8)
    inner.pack(fill='both', padx=2, pady=2)
    ctk.CTkLabel(
        inner, text=label,
        font=ctk.CTkFont(family='Segoe UI', size=10),
        text_color=t['text_dim'],
    ).pack(anchor='w', padx=12, pady=(8, 0))
    ctk.CTkLabel(
        inner, text=value,
        font=ctk.CTkFont(family='Consolas', size=13, weight='bold'),
        text_color=c, wraplength=720, justify='left',
    ).pack(anchor='w', padx=12, pady=(2, 8))


def _warn(parent, text: str, dark: bool) -> None:
    """Card de advertencia con borde naranja."""
    t = _th(dark)
    f = ctk.CTkFrame(parent, fg_color=t['card'], corner_radius=8,
                     border_width=2, border_color=t['warning'])
    f.pack(fill='x', padx=10, pady=4)
    ctk.CTkLabel(
        f, text=f'⚠️  {text}',
        font=ctk.CTkFont(family='Segoe UI', size=11),
        text_color=t['warning'], wraplength=700, justify='left',
    ).pack(anchor='w', padx=12, pady=8)


def _info(parent, text: str, dark: bool,
          color: str = 'text_dim', size: int = 11) -> None:
    """Label de texto informativo simple."""
    t = _th(dark)
    ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(family='Segoe UI', size=size),
        text_color=t[color], wraplength=750, justify='left',
    ).pack(anchor='w', padx=14, pady=2)


# ─────────────────────────────────────────────────────────────────
#  FIGURAS MATPLOTLIB EMBEBIDAS
# ─────────────────────────────────────────────────────────────────

def _embed(parent, fig: Figure) -> FigureCanvasTkAgg:
    """Incrusta una figura matplotlib dentro de un frame tkinter."""
    c = FigureCanvasTkAgg(fig, master=parent)
    c.draw()
    c.get_tk_widget().pack(fill='x', padx=10, pady=3)
    return c


def render_matrix(parent, data, title: str, dark: bool,
                  col_labels=None,
                  highlight_last_col: bool = False,
                  highlight_diag: bool = False) -> None:
    """
    Renderiza una matriz 2-D como tabla matplotlib estilizada.

    Parameters
    ----------
    data : list[list]  — filas con valores (str o numéricos)
    title : str        — título de la tabla
    highlight_last_col : bool — colorea la última columna (para [A|b])
    highlight_diag     : bool — colorea la diagonal principal (para L, U)
    """
    t = _th(dark)
    rows = len(data)
    cols = len(data[0]) if rows else 0
    if not rows or not cols:
        return

    cell_text = [[_fmt(v) for v in row] for row in data]

    # Tamaño dinámico según dimensiones
    cw = max(0.75, min(7.5 / max(cols, 1), 1.6))
    rh = 0.42
    fw = min(cw * cols + 0.6, 9.2)
    fh = rh * rows + (0.55 if title else 0.25) + (0.38 if col_labels else 0)
    fh = max(fh, 0.9)

    fig = Figure(figsize=(fw, fh), facecolor=t['fig_bg'], dpi=96)
    ax = fig.add_subplot(111)
    ax.set_facecolor(t['fig_bg'])
    ax.axis('off')

    # Mapa de colores de celda
    colors = []
    for r in range(rows):
        rc = []
        for c in range(cols):
            if highlight_last_col and c == cols - 1:
                rc.append(t['tbl_aug'])
            elif highlight_diag and r == c:
                rc.append(t['tbl_diag'])
            elif r % 2 == 0:
                rc.append(t['tbl_odd'])
            else:
                rc.append(t['tbl_even'])
        colors.append(rc)

    tbl = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc='center',
        cellLoc='center',
        cellColours=colors,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.0, 1.65)

    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(t['tbl_edge'])
        cell.set_linewidth(0.5)
        if r == 0 and col_labels is not None:
            cell.set_facecolor(t['tbl_head'])
            cell.set_text_props(color=t['info'], fontweight='bold')
        else:
            cell.set_text_props(color=t['text'], fontfamily='Consolas')

    if title:
        ax.set_title(title, color=t['info'], fontsize=11,
                     fontweight='bold', loc='left', pad=4)

    fig.tight_layout(pad=0.4)
    _embed(parent, fig)


def render_poly(parent, latex_str: str, var_label: str, dark: bool,
                eval_x=None, eval_y=None) -> None:
    """
    Renderiza un polinomio usando mathtext de matplotlib.
    latex_str debe ser la salida de sympy.latex(expr).
    """
    t = _th(dark)
    has_eval = (eval_x is not None and eval_y is not None)
    fig_h = 1.55 if has_eval else 0.95
    fig = Figure(figsize=(8.5, fig_h), facecolor=t['card'], dpi=96)
    ax = fig.add_axes([0.01, 0, 0.99, 1])
    ax.set_facecolor(t['card'])
    ax.axis('off')

    y0 = 0.72 if has_eval else 0.5

    # Etiqueta
    ax.text(0.01, y0, var_label,
            color=t['text_dim'], fontsize=10, va='center', ha='left',
            transform=ax.transAxes)

    # Polinomio con mathtext
    math_str = f'${latex_str}$'
    try:
        ax.text(0.12, y0, math_str,
                color=t['success'], fontsize=12, va='center', ha='left',
                transform=ax.transAxes)
    except Exception:
        # Fallback a texto plano si mathtext falla
        plain = latex_str.replace('{', '').replace('}', '').replace('^', '**')
        ax.text(0.12, y0, plain,
                color=t['success'], fontsize=11, va='center', ha='left',
                transform=ax.transAxes, fontfamily='Consolas')

    # Valor evaluado
    if has_eval:
        try:
            ev = f'$P({eval_x}) = {eval_y}$'
            ax.text(0.12, 0.22, ev,
                    color=t['accent'], fontsize=12, va='center', ha='left',
                    transform=ax.transAxes, fontweight='bold')
        except Exception:
            ax.text(0.12, 0.22, f'P({eval_x}) = {eval_y}',
                    color=t['accent'], fontsize=11, va='center', ha='left',
                    transform=ax.transAxes, fontfamily='Consolas')

    fig.tight_layout(pad=0.2)
    _embed(parent, fig)


def render_text_eq(parent, pieces: list[tuple[str, str, str]],
                   dark: bool, height: float = 1.1) -> None:
    """
    Muestra líneas de texto con etiqueta y valor coloreado.
    pieces : [(etiqueta, texto, color_key), ...]
    """
    t = _th(dark)
    n = max(len(pieces), 1)
    fig = Figure(figsize=(8, height), facecolor=t['card'], dpi=96)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(t['card'])
    ax.axis('off')

    step = 1.0 / (n + 0.5)
    for i, (label, expr, ck) in enumerate(pieces):
        y = 1 - (i + 1) * step
        if label:
            ax.text(0.02, y, label,
                    color=t['text_dim'], fontsize=10, va='center', ha='left',
                    transform=ax.transAxes)
        ax.text(0.22, y, expr,
                color=t.get(ck, t['text']), fontsize=11, va='center', ha='left',
                transform=ax.transAxes, fontfamily='Consolas', fontweight='bold')

    fig.tight_layout(pad=0.2)
    _embed(parent, fig)


def render_ops(parent, ops: list[str], dark: bool) -> None:
    """Lista numerada de operaciones elementales de fila."""
    t = _th(dark)
    n = max(len(ops), 1)
    fh = max(0.36 * n, 0.7)
    fig = Figure(figsize=(8, fh), facecolor=t['fig_bg'], dpi=96)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(t['fig_bg'])
    ax.axis('off')

    for i, op in enumerate(ops):
        y = 1 - (i + 0.5) / n
        ax.text(0.01, y, f'{i + 1:2}.',
                color=t['text_dim'], fontsize=9, va='center', ha='left',
                transform=ax.transAxes)
        ax.text(0.055, y, op,
                color=t['purple'], fontsize=10, va='center', ha='left',
                transform=ax.transAxes, fontfamily='Consolas')

    _embed(parent, fig)


def render_convergence(parent, iteraciones: list, dark: bool) -> None:
    """Gráfica de error relativo vs. iteración."""
    t = _th(dark)
    
    if not iteraciones:
        return

    is_dict = isinstance(iteraciones[0], dict)
    
    if is_dict:
        iters = []
        errors = []
        for row in iteraciones:
            iters.append(row.get('Iteración', len(iters) + 1))
            err_val = row.get('Error (%)', row.get('Error Máx (%)', 0.0))
            if err_val is None:
                err_val = 100.0
            try:
                errors.append(abs(float(err_val)))
            except (TypeError, ValueError):
                errors.append(0.0)
    else:
        iters = [row[0] for row in iteraciones]
        errors = []
        for row in iteraciones:
            try:
                errors.append(abs(float(row[-1])))
            except (TypeError, ValueError):
                errors.append(0.0)

    if len(iters) < 2:
        return

    fig = Figure(figsize=(7.5, 2.8), facecolor=t['fig_bg'], dpi=96)
    ax = fig.add_subplot(111)
    ax.set_facecolor(t['ax_bg'])

    ax.plot(iters, errors, color=t['accent'], lw=2,
            marker='o', ms=4, zorder=3, label='Error (%)')
    ax.fill_between(iters, errors, alpha=0.12, color=t['accent'])

    ax.set_xlabel('Iteración', color=t['text_dim'], fontsize=9)
    ax.set_ylabel('Error relativo (%)', color=t['text_dim'], fontsize=9)
    ax.set_title('Convergencia del error', color=t['info'],
                 fontsize=10, fontweight='bold')
    ax.tick_params(colors=t['text_dim'], labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(t['border'])
    ax.grid(True, color=t['border'], alpha=0.4, linewidth=0.5)

    # Anotación del punto final
    ax.annotate(
        f"  Final: {errors[-1]:.3g}%",
        xy=(iters[-1], errors[-1]),
        xytext=(-55, 18), textcoords='offset points',
        color=t['success'], fontsize=8, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color=t['success'], lw=1.2),
    )

    fig.tight_layout(pad=0.8)
    _embed(parent, fig)


def render_r2_bar(parent, r2_val: float, dark: bool) -> None:
    """Barra visual del coeficiente de determinación R²."""
    t = _th(dark)
    color = (t['success'] if r2_val >= 0.9
             else (t['warning'] if r2_val >= 0.7 else t['accent']))

    fig = Figure(figsize=(7.5, 0.85), facecolor=t['card'], dpi=96)
    ax = fig.add_axes([0.03, 0.15, 0.94, 0.7])
    ax.set_facecolor(t['card'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Barra de fondo
    ax.barh(0.5, 1.0, height=0.55, color=t['border'], align='center', zorder=1)
    # Barra de R²
    ax.barh(0.5, r2_val, height=0.55, color=color, align='center',
            alpha=0.9, zorder=2)

    txt_x = min(r2_val + 0.02, 0.65)
    ax.text(txt_x, 0.5, f'R² = {r2_val:.6f}',
            va='center', ha='left', color=color, fontsize=11, fontweight='bold')
    ax.text(0.005, 0.5, '0', va='center', ha='left',
            color=t['text_dim'], fontsize=8)
    ax.text(0.995, 0.5, '1', va='center', ha='right',
            color=t['text_dim'], fontsize=8)

    fig.tight_layout(pad=0.15)
    _embed(parent, fig)


def render_iter_table(parent, headers: list[str],
                      rows: list, dark: bool) -> None:
    """Treeview estilizado para tablas de iteraciones."""
    t = _th(dark)
    cont = ctk.CTkFrame(parent, fg_color=t['fig_bg'], corner_radius=6)
    cont.pack(fill='x', padx=10, pady=4)

    sn = f'EqTab{"D" if dark else "L"}.Treeview'
    s = ttk.Style()
    s.configure(sn,
                background=t['tbl_odd'],
                foreground=t['text'],
                fieldbackground=t['tbl_odd'],
                borderwidth=0,
                rowheight=22,
                font=('Consolas', 9))
    s.configure(f'{sn}.Heading',
                background=t['tbl_head'],
                foreground=t['info'],
                font=('Segoe UI', 9, 'bold'),
                borderwidth=0)
    s.map(sn, background=[('selected', t['accent'])])

    sb = ttk.Scrollbar(cont, orient='vertical')
    sb.pack(side='right', fill='y')

    tree = ttk.Treeview(
        cont, columns=headers, show='headings',
        style=sn, yscrollcommand=sb.set,
        height=min(len(rows), 12),
    )
    sb.config(command=tree.yview)

    for h in headers:
        tree.heading(h, text=h)
        tree.column(h, anchor='center', width=max(65, len(str(h)) * 10))

    tree.tag_configure('odd',  background=t['tbl_odd'],  foreground=t['text'])
    tree.tag_configure('even', background=t['tbl_even'], foreground=t['text'])

    for i, row in enumerate(rows):
        tree.insert('', 'end',
                    values=[str(v) for v in row],
                    tags=('odd' if i % 2 == 0 else 'even',))
    tree.pack(fill='x')


# ─────────────────────────────────────────────────────────────────
#  RENDERIZADORES POR MÉTODO
# ─────────────────────────────────────────────────────────────────

def _lu(tab_res, tab_det, d: dict, dk: bool) -> None:
    """Factorización LU."""
    sol = d.get('solucion', [])
    y_v = d.get('y', [])

    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, 'Factorización LU con Pivoteo Parcial', '🧮', dk, 'success')
    _banner(sf, 'Solución  x',
            '   '.join(f'x{i+1} = {v}' for i, v in enumerate(sol)), dk, 'success')
    _banner(sf, 'Vector auxiliar  y  (solución de Ly = Pb)',
            '   '.join(y_v), dk, 'info')
    _info(sf, '① Se descompone  A = P · L · U  usando pivoteo parcial por columna.', dk)
    _info(sf, '② Se resuelve  L · y = P · b  por sustitución progresiva (adelante).', dk)
    _info(sf, '③ Se resuelve  U · x = y  por sustitución regresiva (atrás).', dk)

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)
    _hdr(sf2, 'Paso 1 — Matriz de Permutación  P', '🔀', dk, 'purple')
    render_matrix(sf2, d.get('P', []), '', dk)

    _hdr(sf2, 'Paso 2 — Triangular Inferior  L  (diagonal = 1)', '⬇️', dk, 'info')
    render_matrix(sf2, d.get('L', []), '', dk, highlight_diag=True)

    _hdr(sf2, 'Paso 3 — Triangular Superior  U  (pivotes en diagonal)', '⬆️', dk, 'warning')
    render_matrix(sf2, d.get('U', []), '', dk, highlight_diag=True)

    _hdr(sf2, 'Paso 4 — Resolución de los dos sistemas triangulares', '🔢', dk, 'success')
    render_text_eq(sf2, [
        ('Sistema 1:', f'L · y = P · b   →   y = [{", ".join(y_v)}]', 'info'),
        ('Sistema 2:', f'U · x = y       →   x = [{", ".join(sol)}]', 'success'),
    ], dk, height=1.1)


def _gauss_jordan(tab_res, tab_det, d: dict, dk: bool) -> None:
    """Eliminación Gauss-Jordan."""
    tipo = d.get('tipo', '')
    sol = d.get('solucion')
    pasos = d.get('pasos', [])

    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, 'Eliminación Gauss-Jordan — Resultado', '🧾', dk, 'info')
    ck = ('success' if 'unica' in tipo.lower()
          else ('warning' if 'indeter' in tipo.lower() else 'accent'))
    _banner(sf, 'Clasificación del sistema', tipo, dk, ck)
    if sol:
        _banner(sf, 'Solución única  x',
                '   '.join(f'x{i+1} = {v}' for i, v in enumerate(sol)),
                dk, 'success')

    rref = d.get('rref', [])
    if rref:
        _hdr(sf, 'Matriz RREF final  [A | b]', '✅', dk, 'success')
        render_matrix(sf, rref, '', dk, highlight_last_col=True)

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)
    if pasos:
        _hdr(sf2, f'Operaciones elementales de fila  ({len(pasos)} pasos)', '⚙️', dk, 'purple')
        ops = [p.get('operacion', '') for p in pasos if p.get('operacion')]
        render_ops(sf2, ops, dk)

        # Mostrar estado de la matriz en pasos clave
        # (primero 4 + último si hay muchos)
        shown = pasos if len(pasos) <= 5 else (pasos[:4] + [pasos[-1]])
        for idx, paso in enumerate(shown):
            mat = paso.get('matriz')
            op  = paso.get('operacion', f'Paso {idx + 1}')
            if mat:
                if idx == 4 and len(pasos) > 5:
                    _info(sf2,
                          f'... ({len(pasos) - 5} pasos intermedios omitidos) ...',
                          dk, 'text_dim')
                render_matrix(sf2, mat, f'Después de:  {op}', dk,
                              highlight_last_col=True)
    else:
        _hdr(sf2, 'Forma RREF Final  [A | b]', '✅', dk, 'success')
        render_matrix(sf2, rref, '', dk, highlight_last_col=True)


def _rouche(tab_res, tab_det, d: dict, dk: bool) -> None:
    """Teorema de Rouché-Frobenius."""
    t = _th(dk)
    conclusion = d.get('conclusion', '')
    ra  = d.get('rango_a',   '?')
    rab = d.get('rango_aug', '?')
    n   = d.get('incognitas','?')

    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, 'Teorema de Rouché-Frobenius', '🧠', dk, 'info')
    ck = ('success' if 'unica' in conclusion.lower()
          else ('warning' if 'infinitas' in conclusion.lower() else 'accent'))
    _banner(sf, 'Conclusión', conclusion, dk, ck)
    _banner(sf,
            'Datos clave del sistema',
            f'Rango(A) = {ra}   |   Rango([A|b]) = {rab}   |   Incógnitas = {n}',
            dk, 'info')

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)
    _hdr(sf2, 'Análisis paso a paso del teorema', '🔍', dk, 'info')

    fig = Figure(figsize=(7.5, 3.8), facecolor=t['fig_bg'], dpi=96)
    ax = fig.add_subplot(111)
    ax.set_facecolor(t['ax_bg'])
    ax.axis('off')

    datos_txt = [
        f'  Rango(A)       = {ra}',
        f'  Rango([A|b])   = {rab}',
        f'  n (incógnitas) = {n}',
    ]
    y = 0.88
    for txt in datos_txt:
        ax.text(0.03, y, txt, color=t['text'], fontsize=12,
                va='center', transform=ax.transAxes, fontfamily='Consolas')
        y -= 0.17

    ax.axhline(0.42, color=t['border'], lw=1.2,
               xmin=0.02, xmax=0.98, transform=ax.transAxes)

    analysis: list[tuple[str, str]] = []
    try:
        if int(ra) == int(rab):
            analysis.append((f'✓  Rango(A) = Rango([A|b])  →  Sistema compatible', t['success']))
            if int(ra) == int(n):
                analysis.append(('✓  Rango = n  →  Solución única y determinada', t['success']))
            else:
                dof = int(n) - int(ra)
                analysis.append((
                    f'△  Rango < n  →  Infinitas soluciones'
                    f'  (grados de libertad = {dof})', t['warning']))
        else:
            analysis.append((
                '✗  Rango(A) ≠ Rango([A|b])  →  Sistema incompatible (sin solución)',
                t['accent']))
    except (ValueError, TypeError):
        analysis.append((conclusion, t['text']))

    y2 = 0.32
    for txt, clr in analysis:
        ax.text(0.03, y2, txt, color=clr, fontsize=12,
                va='center', transform=ax.transAxes, fontweight='bold')
        y2 -= 0.18

    fig.tight_layout(pad=0.5)
    _embed(sf2, fig)


def _iterativo(tab_res, tab_det, d: dict, dk: bool, nombre: str) -> None:
    """Métodos iterativos: Jacobi y Gauss-Seidel."""
    sol   = d.get('solucion', [])
    iters = d.get('iteraciones', [])

    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, f'Método de {nombre} — Resultado', '🔁', dk, 'success')
    if d.get('advertencia'):
        _warn(sf, d['advertencia'], dk)
    _banner(sf, 'Vector solución  x  (convergido)',
            '   '.join(f'x{i+1} = {v}' for i, v in enumerate(sol)), dk, 'success')
    if iters:
        _banner(sf, 'Total de iteraciones para converger',
                str(len(iters)), dk, 'info')

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)
    if iters:
        n_vars = len(iters[0]) - 2
        headers = ['Iter'] + [f'x{i+1}' for i in range(n_vars)] + ['Error (%)']
        _hdr(sf2, 'Tabla de Iteraciones', '📊', dk, 'info')
        render_iter_table(sf2, headers, iters, dk)
        _hdr(sf2, 'Gráfica de Convergencia del Error', '📉', dk, 'accent')
        render_convergence(sf2, iters, dk)


def _trazadores(tab_res, tab_det, d: dict, dk: bool) -> None:
    """Trazadores Cúbicos (Splines)."""
    t  = _th(dk)
    eqs = d.get('ecuaciones', [])

    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, 'Trazadores Cúbicos — Resultado', '🎢', dk, 'success')

    if d.get('valor') is not None:
        _banner(sf, f'Valor interpolado en  x = {d.get("evaluado_en", "?")}',
                f'S(x) = {d["valor"]}', dk, 'success')
    _banner(sf, 'Tramos cúbicos generados',
            f'{len(eqs)} polinomios cúbicos', dk, 'info')

    _hdr(sf, 'Polinomios por intervalo  S(x)', '📐', dk, 'info')
    for eq in eqs:
        ctk.CTkLabel(
            sf,
            text=f"  [{eq['intervalo']}]  →  {eq['polinomio']}",
            font=ctk.CTkFont(family='Consolas', size=10),
            text_color=t['success'],
            wraplength=740, justify='left',
        ).pack(anchor='w', padx=14, pady=2)

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)
    _hdr(sf2, 'Coeficientes  (a, b, c, d)  por tramo', '🔢', dk, 'purple')
    _info(sf2, 'Fórmula:  Sᵢ(x) = a + b(x − xᵢ) + c(x − xᵢ)² + d(x − xᵢ)³', dk)

    rows = [
        [eq['intervalo'], _fmt(eq['a']), _fmt(eq['b']),
         _fmt(eq['c']), _fmt(eq['d'])]
        for eq in eqs
    ]
    render_iter_table(sf2, ['Intervalo', 'a', 'b', 'c', 'd'], rows, dk)

    # Polinomios renderizados con mathtext
    has_latex = any(eq.get('latex_poly') for eq in eqs)
    if has_latex:
        _hdr(sf2, 'Polinomios en notación matemática', '📝', dk, 'info')
        for eq in eqs:
            lx = eq.get('latex_poly', '')
            if lx:
                render_poly(sf2, lx, f"[{eq['intervalo']}]", dk)


def _poly(tab_res, tab_det, d: dict, dk: bool,
          nombre: str, icon: str) -> None:
    """Interpolación de Lagrange y Diferencias Divididas."""
    t = _th(dk)
    poly_str = d.get('polinomio', '')
    valor    = d.get('valor')
    eval_x   = d.get('eval_x')
    lx       = d.get('latex_poly', '')

    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, f'{nombre} — Resultado', icon, dk, 'success')
    _banner(sf, 'Polinomio interpolante  P(x)', poly_str, dk, 'success')
    if valor is not None and eval_x is not None:
        _banner(sf, f'Evaluación en  x = {eval_x}',
                f'P({eval_x}) = {valor}', dk, 'accent')

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)
    _hdr(sf2, 'Polinomio en notación matemática', '📐', dk, 'info')
    if lx:
        render_poly(sf2, lx, 'P(x) = ', dk, eval_x=eval_x, eval_y=valor)
    else:
        ctk.CTkLabel(
            sf2, text=f'P(x) = {poly_str}',
            font=ctk.CTkFont(family='Consolas', size=12),
            text_color=t['success'], wraplength=750, justify='left',
        ).pack(anchor='w', padx=14, pady=6)

    # Tabla de diferencias divididas (solo en Newton DD)
    tabla = d.get('tabla')
    if tabla:
        _hdr(sf2, 'Tabla de diferencias divididas', '🔢', dk, 'purple')
        n = len(tabla)
        hdrs = ['f(x)'] + [f'Δ{j}f' for j in range(1, n)]
        render_iter_table(sf2, hdrs, tabla, dk)


def _regresion(tab_res, tab_det, d: dict, dk: bool, nombre: str) -> None:
    """Regresión cuadrática y Mínimos cuadrados."""
    ecuacion = d.get('ecuacion', '')
    r2_str   = str(d.get('r2', '?'))
    lx       = d.get('latex_ecuacion', '')
    tabla    = d.get('tabla', [])

    try:
        r2v = float(r2_str)
        ck  = ('success' if r2v >= 0.9 else ('warning' if r2v >= 0.7 else 'accent'))
    except ValueError:
        r2v = None
        ck  = 'info'

    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, f'{nombre} — Resultado', '📈', dk, 'success')
    _banner(sf, 'Ecuación ajustada', ecuacion, dk, 'success')
    _banner(sf, 'Coeficiente de determinación  R²', r2_str, dk, ck)

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)

    if lx:
        _hdr(sf2, 'Ecuación en notación matemática', '📐', dk, 'info')
        render_poly(sf2, lx, 'y = ', dk)

    _hdr(sf2, f'Bondad del ajuste  —  R² = {r2_str}', '📊', dk, ck)
    if r2v is not None:
        render_r2_bar(sf2, r2v, dk)

    if tabla:
        _hdr(sf2, 'Tabla de datos y residuos', '🔢', dk, 'purple')
        render_iter_table(sf2, ['x', 'y', 'y estimado', 'residuo'], tabla, dk)


def _newton_senl(tab_res, tab_det, d: dict, dk: bool) -> None:
    """Newton-Raphson para SENL."""
    variables = d.get('variables', [])
    sol       = d.get('solucion', [])
    iters     = d.get('iteraciones', [])

    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, 'Newton-Raphson para SENL — Resultado', '🧬', dk, 'success')
    for var, val in zip(variables, sol):
        _banner(sf, f'Variable  {var}', str(val), dk, 'success')
    if iters:
        _banner(sf, 'Iteraciones hasta convergencia',
                str(len(iters)), dk, 'info')

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)
    if iters:
        headers = ['Iter'] + list(variables) + ['Error (%)']
        _hdr(sf2, 'Tabla de Iteraciones', '📊', dk, 'info')
        render_iter_table(sf2, headers, iters, dk)
        _hdr(sf2, 'Gráfica de Convergencia', '📉', dk, 'accent')
        render_convergence(sf2, iters, dk)


# ─────────────────────────────────────────────────────────────────
#  DISPATCHER PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def mostrar_resultado_enriquecido(tabs, tipo: str, datos: dict,
                                  dark: bool = True) -> None:
    """
    Punto de entrada principal: limpia y re-renderiza las tabs con
    contenido matemático rico.

    Parameters
    ----------
    tabs  : CTkTabview  — debe contener las tabs '📋  Resultado' y '📊  Detalle'
    tipo  : str         — identificador del método:
               'lu' | 'gauss_jordan' | 'rouche' | 'jacobi' | 'gauss_seidel' |
               'trazadores' | 'lagrange' | 'diferencias_divididas' |
               'regresion' | 'minimos_cuadrados' | 'newton_senl'
    datos : dict        — diccionario resultado del método numérico
    dark  : bool        — True para tema oscuro
    """
    plt.close('all')   # Libera figuras antiguas de matplotlib

    tab_r = tabs.tab('📋  Resultado')
    tab_d = tabs.tab('📊  Detalle')
    _clear(tab_r)
    _clear(tab_d)

    dispatch = {
        'lu':                    _lu,
        'gauss_jordan':          _gauss_jordan,
        'rouche':                _rouche,
        'jacobi':                lambda a, b, d, k: _iterativo(a, b, d, k, 'Jacobi'),
        'gauss_seidel':          lambda a, b, d, k: _iterativo(a, b, d, k, 'Gauss-Seidel'),
        'trazadores':            _trazadores,
        'lagrange':              lambda a, b, d, k: _poly(
                                     a, b, d, k, 'Interpolación de Lagrange', '📌'),
        'diferencias_divididas': lambda a, b, d, k: _poly(
                                     a, b, d, k, 'Diferencias Divididas de Newton', '🧮'),
        'regresion':             lambda a, b, d, k: _regresion(
                                     a, b, d, k, 'Regresión Cuadrática'),
        'minimos_cuadrados':     lambda a, b, d, k: _regresion(
                                     a, b, d, k, 'Mínimos Cuadrados'),
        'newton_senl':           _newton_senl,
    }

    fn = dispatch.get(tipo)
    if fn:
        fn(tab_r, tab_d, datos, dark)


def _raiz_generica(tab_res, tab_det, d: dict, dk: bool, nombre: str, icon: str) -> None:
    """Renderizador genérico para métodos de búsqueda de raíces."""
    import sympy as sp
    
    sol = d.get('raiz_aproximada')
    iters = d.get('tabla_iteraciones', [])
    funcion_str = d.get('funcion_str', '')
    
    # ── Tab Resultado ──────────────────────────────
    sf = _scrollable(tab_res, dk)
    _hdr(sf, f'{nombre} — Resultado', icon, dk, 'success')
    
    if d.get('advertencia'):
        _warn(sf, d['advertencia'], dk)
        
    if sol is not None:
        if isinstance(sol, complex):
            sol_str = f"{sol.real:.6g} + {sol.imag:.6g}j" if abs(sol.imag) > 1e-10 else f"{sol.real:.6g}"
        else:
            try:
                # Intenta convertirlo y formatearlo como un número real estándar
                sol_str = f"{float(sol):.6g}"
            except (TypeError, ValueError):
                # Si es un número complejo (Add) o falla la conversión, lo maneja aquí
                try:
                    c_sol = complex(sol)
                    # Formatea la parte real e imaginaria por separado
                    signo = "+" if c_sol.imag >= 0 else "-"
                    sol_str = f"{c_sol.real:.6g} {signo} {abs(c_sol.imag):.6g}i"
                except Exception:
                    # Plan de respaldo absoluto si es una expresión 100% simbólica
                    sol_str = str(sol)
        _banner(sf, 'Raíz aproximada  (x)', sol_str, dk, 'success')
        
    if 'raiz1' in d and 'raiz2' in d:
        r1 = d['raiz1']
        r2 = d['raiz2']
        r1_s = f"{r1.real:.6g} + {r1.imag:.6g}j" if isinstance(r1, complex) and abs(r1.imag) > 1e-10 else f"{r1.real:.6g}" if isinstance(r1, complex) else f"{r1:.6g}"
        r2_s = f"{r2.real:.6g} + {r2.imag:.6g}j" if isinstance(r2, complex) and abs(r2.imag) > 1e-10 else f"{r2.real:.6g}" if isinstance(r2, complex) else f"{r2:.6g}"
        _banner(sf, 'Raíz 1  (x₁)', r1_s, dk, 'success')
        _banner(sf, 'Raíz 2  (x₂)', r2_s, dk, 'success')

    if funcion_str:
        try:
            lx = sp.latex(sp.sympify(funcion_str))
            _hdr(sf, 'Función Objetivo', '📐', dk, 'info')
            render_poly(sf, lx, 'f(x) = ', dk)
        except Exception:
            pass

    if 'derivada_str' in d:
        try:
            lx_d = sp.latex(sp.sympify(d['derivada_str']))
            render_poly(sf, lx_d, "f'(x) = ", dk)
        except Exception:
            pass

    if iters:
        _banner(sf, 'Iteraciones totales', str(d.get('total_iteraciones', len(iters))), dk, 'info')

    # ── Tab Detalle ────────────────────────────────
    sf2 = _scrollable(tab_det, dk)
    if iters:
        headers = list(iters[0].keys())
        rows = []
        for row_dict in iters:
            row_vals = []
            for k, v in row_dict.items():
                if v is None:
                    row_vals.append("N/A")
                elif isinstance(v, float):
                    row_vals.append(f"{v:.6g}")
                elif isinstance(v, complex):
                    row_vals.append(f"{v.real:.6g} + {v.imag:.6g}j" if abs(v.imag) > 1e-10 else f"{v.real:.6g}")
                else:
                    row_vals.append(str(v))
            rows.append(row_vals)
            
        _hdr(sf2, 'Tabla de Iteraciones', '📊', dk, 'info')
        render_iter_table(sf2, headers, rows, dk)
        
        _hdr(sf2, 'Gráfica de Convergencia del Error', '📉', dk, 'accent')
        render_convergence(sf2, iters, dk)


def mostrar_resultado_enriquecido_raices(tabs, tipo: str, datos: dict, dark: bool = True) -> None:
    """
    Punto de entrada para métodos de raíces. Usa '📋  Resultado' y '📊  Detalle'
    y deja intacta la tab de '📈  Gráfica'.
    """
    plt.close('all')

    tab_r = tabs.tab('📋  Resultado')
    tab_d = tabs.tab('📊  Detalle')
    _clear(tab_r)
    _clear(tab_d)

    dispatch = {
        'biseccion':      lambda a, b, d, k: _raiz_generica(a, b, d, k, 'Método de Bisección', '📏'),
        'regla_falsa':    lambda a, b, d, k: _raiz_generica(a, b, d, k, 'Regla Falsa', '📏'),
        'newton':         lambda a, b, d, k: _raiz_generica(a, b, d, k, 'Newton-Raphson', '⚡'),
        'secante':        lambda a, b, d, k: _raiz_generica(a, b, d, k, 'Método de la Secante', '📈'),
        'punto_fijo':     lambda a, b, d, k: _raiz_generica(a, b, d, k, 'Punto Fijo', '🔄'),
        'muller':         lambda a, b, d, k: _raiz_generica(a, b, d, k, 'Método de Müller', '🧮'),
        'bairstow':       lambda a, b, d, k: _raiz_generica(a, b, d, k, 'Método de Bairstow', '✂️'),
        'horner_newton':  lambda a, b, d, k: _raiz_generica(a, b, d, k, 'Horner-Newton', '📝'),
    }

    fn = dispatch.get(tipo)
    if fn:
        fn(tab_r, tab_d, datos, dark)
