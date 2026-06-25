import math

import numpy as np
import sympy as sp


def parse_matrix(text):
    rows = []
    for raw in text.replace(";", "\n").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.replace(",", " ").split()
        rows.append([float(p) for p in parts])
    if not rows:
        raise ValueError("La matriz esta vacia.")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Todas las filas de la matriz deben tener la misma cantidad de columnas.")
    matrix = np.array(rows, dtype=float)
    if not np.all(np.isfinite(matrix)):
        raise ValueError("La matriz no puede contener nan, inf o -inf.")
    if matrix.size == 0:
        raise ValueError("La matriz esta vacia.")
    return matrix


def parse_vector(text):
    parts = text.replace(",", " ").replace(";", " ").split()
    if not parts:
        raise ValueError("El vector esta vacio.")
    vector = np.array([float(p) for p in parts], dtype=float)
    if not np.all(np.isfinite(vector)):
        raise ValueError("El vector no puede contener nan, inf o -inf.")
    return vector


def parse_points(text):
    points = []
    for raw in text.replace(";", "\n").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.replace(",", " ").split()
        if len(parts) != 2:
            raise ValueError("Cada punto debe tener exactamente dos valores: x y.")
        points.append((float(parts[0]), float(parts[1])))
    if len(points) < 2:
        raise ValueError("Ingresa al menos dos puntos.")
    if not all(math.isfinite(x) and math.isfinite(y) for x, y in points):
        raise ValueError("Los puntos no pueden contener nan, inf o -inf.")
    xs = [p[0] for p in points]
    if len(set(xs)) != len(xs):
        raise ValueError("Los valores de x no deben repetirse.")
    return points


def parse_positive_tolerance(value):
    tol = float(value)
    if not math.isfinite(tol) or tol <= 0:
        raise ValueError("La tolerancia debe ser un numero real mayor que 0.")
    return tol


def parse_positive_int(value, name):
    number = float(value)
    if not math.isfinite(number) or number <= 0 or not number.is_integer():
        raise ValueError(f"{name} debe ser un entero positivo.")
    return int(number)


def parse_non_negative_int(value, name):
    number = float(value)
    if not math.isfinite(number) or number < 0 or not number.is_integer():
        raise ValueError(f"{name} debe ser un entero no negativo.")
    return int(number)


def parse_optional_finite(value, name):
    if value is None or str(value).strip() == "":
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} debe ser un numero real finito.")
    return number


def _format_number(value, digits=8):
    if isinstance(value, complex):
        if abs(value.imag) < 1e-10:
            return f"{value.real:.{digits}g}"
        return f"{value.real:.{digits}g} {value.imag:+.{digits}g}j"
    return f"{float(value):.{digits}g}"


def _as_rows(matrix):
    return [[_format_number(v) for v in row] for row in np.asarray(matrix)]


class MetodoLU:
    def calcular(self, matriz_str, vector_str):
        try:
            a = parse_matrix(matriz_str)
            b = parse_vector(vector_str)
            if a.shape[0] != a.shape[1]:
                return {"error": "LU requiere una matriz cuadrada."}
            if b.size != a.shape[0]:
                return {"error": "El vector b debe tener la misma cantidad de filas que A."}

            n = a.shape[0]
            u = a.copy()
            l = np.eye(n)
            p = np.eye(n)

            for k in range(n - 1):
                pivot = k + np.argmax(np.abs(u[k:, k]))
                if abs(u[pivot, k]) < 1e-12:
                    return {"error": "La matriz es singular o tiene pivote cero. No se puede factorizar."}
                if pivot != k:
                    u[[k, pivot]] = u[[pivot, k]]
                    p[[k, pivot]] = p[[pivot, k]]
                    if k > 0:
                        l[[k, pivot], :k] = l[[pivot, k], :k]
                for i in range(k + 1, n):
                    l[i, k] = u[i, k] / u[k, k]
                    u[i] = u[i] - l[i, k] * u[k]

            if abs(u[-1, -1]) < 1e-12:
                return {"error": "La matriz es singular o tiene pivote cero. No se puede factorizar."}

            pb = p @ b
            y = np.linalg.solve(l, pb)
            x = np.linalg.solve(u, y)
            return {
                "exito": True,
                "P": _as_rows(p),
                "L": _as_rows(l),
                "U": _as_rows(u),
                "y": [_format_number(v) for v in y],
                "solucion": [_format_number(v) for v in x],
            }
        except Exception as e:
            return {"error": f"Error en factorizacion LU: {e}"}


class MetodoGaussJordan:
    MAX_PASOS = 14  # Límite de pasos a registrar (evita listas enormes)

    def calcular(self, matriz_str, vector_str):
        try:
            a = parse_matrix(matriz_str)
            b = parse_vector(vector_str)
            if a.shape[0] != b.size:
                return {"error": "El vector b debe tener la misma cantidad de filas que A."}
            aug = np.column_stack([a, b])
            rows, cols = aug.shape
            pivot_row = 0
            pivots = []
            pasos = []  # Lista de {'operacion': str, 'matriz': list}

            for col in range(cols - 1):
                pivot = pivot_row + np.argmax(np.abs(aug[pivot_row:, col]))
                if abs(aug[pivot, col]) < 1e-12:
                    continue

                # 1. Intercambio de filas
                if pivot != pivot_row:
                    aug[[pivot_row, pivot]] = aug[[pivot, pivot_row]]
                    if len(pasos) < self.MAX_PASOS:
                        pasos.append({
                            'operacion': f'F{pivot_row+1} \u2194 F{pivot+1}  (intercambio de pivote)',
                            'matriz': _as_rows(aug.copy()),
                        })

                # 2. Normalización del pivote
                divisor = aug[pivot_row, col]
                aug[pivot_row] = aug[pivot_row] / divisor
                if len(pasos) < self.MAX_PASOS:
                    pasos.append({
                        'operacion': f'F{pivot_row+1} \u2190 F{pivot_row+1} / ({_format_number(divisor)})',
                        'matriz': _as_rows(aug.copy()),
                    })

                # 3. Eliminación de todas las demás filas
                for r in range(rows):
                    if r != pivot_row:
                        factor = aug[r, col]
                        aug[r] = aug[r] - factor * aug[pivot_row]
                        if abs(factor) > 1e-12 and len(pasos) < self.MAX_PASOS:
                            sign = '-' if factor >= 0 else '+'
                            pasos.append({
                                'operacion': (
                                    f'F{r+1} \u2190 F{r+1} '
                                    f'{sign} ({_format_number(abs(factor))})\u00b7F{pivot_row+1}'
                                ),
                                'matriz': _as_rows(aug.copy()),
                            })

                pivots.append(col)
                pivot_row += 1
                if pivot_row == rows:
                    break

            rank_a = np.linalg.matrix_rank(a)
            rank_aug = np.linalg.matrix_rank(np.column_stack([a, b]))
            if rank_a < rank_aug:
                tipo = "Sistema incompatible: no tiene solucion."
            elif rank_a == a.shape[1]:
                tipo = "Sistema compatible determinado: solucion unica."
            else:
                tipo = "Sistema compatible indeterminado: infinitas soluciones."

            solucion = None
            if rank_a == rank_aug == a.shape[1]:
                solucion = [_format_number(v) for v in aug[:, -1]]

            return {
                "exito": True,
                "tipo": tipo,
                "rref": _as_rows(aug),
                "solucion": solucion,
                "pasos": pasos,
            }
        except Exception as e:
            return {"error": f"Error en Gauss-Jordan: {e}"}


class MetodoRoucheFrobenius:
    def calcular(self, matriz_str, vector_str):
        try:
            a = parse_matrix(matriz_str)
            b = parse_vector(vector_str)
            if a.shape[0] != b.size:
                return {"error": "El vector b debe tener la misma cantidad de filas que A."}
            aug = np.column_stack([a, b])
            rango_a = int(np.linalg.matrix_rank(a))
            rango_aug = int(np.linalg.matrix_rank(aug))
            n_incognitas = a.shape[1]
            if rango_a != rango_aug:
                conclusion = "Sistema incompatible: no tiene solucion."
            elif rango_a == n_incognitas:
                conclusion = "Sistema compatible determinado: tiene solucion unica."
            else:
                conclusion = "Sistema compatible indeterminado: tiene infinitas soluciones."
            return {
                "exito": True,
                "rango_a": rango_a,
                "rango_aug": rango_aug,
                "incognitas": n_incognitas,
                "conclusion": conclusion,
            }
        except Exception as e:
            return {"error": f"Error en Rouche-Frobenius: {e}"}


class MetodoJacobi:
    def calcular(self, matriz_str, vector_str, x0_str, tolerancia, max_iter=100):
        try:
            a = parse_matrix(matriz_str)
            b = parse_vector(vector_str)
            x = parse_vector(x0_str)
            if a.shape[0] != a.shape[1]:
                return {"error": "Jacobi requiere una matriz cuadrada."}
            if b.size != a.shape[0] or x.size != a.shape[0]:
                return {"error": "b y x0 deben tener la misma dimension que A."}
            if np.any(np.abs(np.diag(a)) < 1e-12):
                return {"error": "Jacobi no puede usar una diagonal con ceros."}
            tolerancia = parse_positive_tolerance(tolerancia)
            max_iter = parse_positive_int(max_iter, "El maximo de iteraciones")

            d = np.diag(a)
            r = a - np.diagflat(d)
            iteraciones = []
            advertencia = ""
            if not np.all(np.abs(np.diag(a)) > (np.sum(np.abs(a), axis=1) - np.abs(np.diag(a)))):
                advertencia = "La matriz no es diagonalmente dominante; Jacobi puede divergir."

            for i in range(1, max_iter + 1):
                x_new = (b - r @ x) / d
                denom = np.maximum(np.abs(x_new), 1e-12)
                error = float(np.max(np.abs((x_new - x) / denom)) * 100)
                iteraciones.append([i, *[_format_number(v) for v in x_new], _format_number(error)])
                if error <= tolerancia:
                    return {
                        "exito": True,
                        "advertencia": advertencia,
                        "solucion": [_format_number(v) for v in x_new],
                        "iteraciones": iteraciones,
                    }
                x = x_new

            return {"error": f"Jacobi no converge en {max_iter} iteraciones. {advertencia}".strip()}
        except Exception as e:
            return {"error": f"Error en Jacobi: {e}"}


class MetodoRegresionCuadratica:
    def calcular(self, puntos_str):
        try:
            points = parse_points(puntos_str)
            if len(points) < 3:
                return {"error": "La regresion cuadratica requiere al menos 3 puntos."}
            xs = np.array([p[0] for p in points], dtype=float)
            ys = np.array([p[1] for p in points], dtype=float)
            coefs = np.polyfit(xs, ys, 2)
            pred = np.polyval(coefs, xs)
            ss_res = float(np.sum((ys - pred) ** 2))
            ss_tot = float(np.sum((ys - np.mean(ys)) ** 2))
            r2 = 1.0 if ss_tot == 0 else 1 - ss_res / ss_tot
            filas = [[_format_number(x), _format_number(y), _format_number(yh), _format_number(y - yh)]
                     for x, y, yh in zip(xs, ys, pred)]
            # LaTeX del polinomio para el renderer gráfico
            x_sym = sp.Symbol('x')
            poly_sym = coefs[0]*x_sym**2 + coefs[1]*x_sym + coefs[2]
            latex_ec = sp.latex(sp.nsimplify(poly_sym, rational=False, tolerance=1e-8))
            return {
                "exito": True,
                "coeficientes": [_format_number(v) for v in coefs],
                "ecuacion": f"y = ({_format_number(coefs[0])})x**2 + ({_format_number(coefs[1])})x + ({_format_number(coefs[2])})",
                "latex_ecuacion": latex_ec,
                "r2": _format_number(r2),
                "tabla": filas,
            }
        except Exception as e:
            return {"error": f"Error en regresion cuadratica: {e}"}


class MetodoMinimosCuadrados:
    def calcular(self, puntos_str, grado):
        try:
            points = parse_points(puntos_str)
            grado = parse_non_negative_int(grado, "El grado")
            if grado < 1:
                return {"error": "El grado debe ser 1 o mayor."}
            if len(points) <= grado:
                return {"error": "Se necesitan mas puntos que el grado del polinomio."}
            xs = np.array([p[0] for p in points], dtype=float)
            ys = np.array([p[1] for p in points], dtype=float)
            coefs = np.polyfit(xs, ys, grado)
            pred = np.polyval(coefs, xs)
            ss_res = float(np.sum((ys - pred) ** 2))
            ss_tot = float(np.sum((ys - np.mean(ys)) ** 2))
            r2 = 1.0 if ss_tot == 0 else 1 - ss_res / ss_tot
            terms = []
            for i, coef in enumerate(coefs):
                power = grado - i
                if power == 0:
                    terms.append(f"({_format_number(coef)})")
                elif power == 1:
                    terms.append(f"({_format_number(coef)})x")
                else:
                    terms.append(f"({_format_number(coef)})x**{power}")
            filas = [[_format_number(x), _format_number(y), _format_number(yh), _format_number(y - yh)]
                     for x, y, yh in zip(xs, ys, pred)]
            # LaTeX del polinomio para el renderer gráfico
            x_sym = sp.Symbol('x')
            poly_sym = sum(c * x_sym**(grado - i) for i, c in enumerate(coefs))
            latex_ec = sp.latex(sp.nsimplify(poly_sym, rational=False, tolerance=1e-8))
            return {
                "exito": True,
                "coeficientes": [_format_number(v) for v in coefs],
                "ecuacion": "y = " + " + ".join(terms),
                "latex_ecuacion": latex_ec,
                "r2": _format_number(r2),
                "tabla": filas,
            }
        except Exception as e:
            return {"error": f"Error en minimos cuadrados: {e}"}


class MetodoNewtonDiferenciasDivididas:
    def calcular(self, puntos_str, evaluar_en=None):
        try:
            points = parse_points(puntos_str)
            xs = [p[0] for p in points]
            coef = [p[1] for p in points]
            n = len(points)
            tabla = [[None for _ in range(n)] for _ in range(n)]
            for i in range(n):
                tabla[i][0] = coef[i]
            for j in range(1, n):
                for i in range(n - j):
                    tabla[i][j] = (tabla[i + 1][j - 1] - tabla[i][j - 1]) / (xs[i + j] - xs[i])
            coefs = [tabla[0][j] for j in range(n)]
            x = sp.Symbol("x")
            poly = coefs[0]
            term = 1
            for i in range(1, n):
                term *= (x - xs[i - 1])
                poly += coefs[i] * term
            poly = sp.expand(poly)
            valor = None
            xv = parse_optional_finite(evaluar_en, "El punto a evaluar")
            if xv is not None:
                valor = _format_number(poly.subs(x, xv))
            return {
                "exito": True,
                "coeficientes": [_format_number(v) for v in coefs],
                "polinomio": str(poly),
                "latex_poly": sp.latex(poly),
                "valor": valor,
                "eval_x": _format_number(xv) if xv is not None else None,
                "tabla": [[_format_number(v) if v is not None else "" for v in row] for row in tabla],
            }
        except Exception as e:
            return {"error": f"Error en diferencias divididas: {e}"}


class MetodoInterpolacionLagrange:
    def calcular(self, puntos_str, evaluar_en=None):
        try:
            points = parse_points(puntos_str)
            x = sp.Symbol("x")
            poly = 0
            for i, (xi, yi) in enumerate(points):
                li = 1
                for j, (xj, _) in enumerate(points):
                    if i != j:
                        li *= (x - xj) / (xi - xj)
                poly += yi * li
            poly = sp.expand(poly)
            valor = None
            xv = parse_optional_finite(evaluar_en, "El punto a evaluar")
            if xv is not None:
                valor = _format_number(poly.subs(x, xv))
            return {
                "exito": True,
                "polinomio": str(poly),
                "latex_poly": sp.latex(poly),
                "valor": valor,
                "eval_x": _format_number(xv) if xv is not None else None,
            }
        except Exception as e:
            return {"error": f"Error en interpolacion: {e}"}


class MetodoNewtonSENL:
    def calcular(self, ecuaciones_str, variables_str, x0_str, tolerancia, max_iter=50):
        try:
            variables = [v.strip() for v in variables_str.replace(";", ",").split(",") if v.strip()]
            if not variables:
                return {"error": "Indica las variables, por ejemplo: x,y."}
            symbols = sp.symbols(variables)
            if len(variables) == 1:
                symbols = (symbols,)
            local = {name: sym for name, sym in zip(variables, symbols)}
            equations = [line.strip() for line in ecuaciones_str.splitlines() if line.strip()]
            if len(equations) != len(symbols):
                return {"error": "La cantidad de ecuaciones debe coincidir con la cantidad de variables."}
            exprs = [sp.sympify(eq, locals=local) for eq in equations]
            f_expr = sp.Matrix(exprs)
            j_expr = f_expr.jacobian(symbols)
            f = sp.lambdify(symbols, f_expr, "numpy")
            jac = sp.lambdify(symbols, j_expr, "numpy")
            x_vec = parse_vector(x0_str)
            if x_vec.size != len(symbols):
                return {"error": "x0 debe tener un valor inicial por cada variable."}
            tolerancia = parse_positive_tolerance(tolerancia)
            max_iter = parse_positive_int(max_iter, "El maximo de iteraciones")

            iteraciones = []
            for i in range(1, max_iter + 1):
                args = tuple(float(v) for v in x_vec)
                f_val = np.array(f(*args), dtype=float).reshape(-1)
                j_val = np.array(jac(*args), dtype=float)
                if not np.all(np.isfinite(f_val)) or not np.all(np.isfinite(j_val)):
                    return {"error": "El sistema produjo nan o inf. Cambia los valores iniciales."}
                delta = np.linalg.solve(j_val, -f_val)
                x_new = x_vec + delta
                error = float(np.linalg.norm(delta, ord=np.inf) * 100)
                iteraciones.append([i, *[_format_number(v) for v in x_new], _format_number(error)])
                if error <= tolerancia:
                    return {
                        "exito": True,
                        "variables": variables,
                        "solucion": [_format_number(v) for v in x_new],
                        "iteraciones": iteraciones,
                    }
                x_vec = x_new
            return {"error": f"Newton para SENL no converge en {max_iter} iteraciones."}
        except np.linalg.LinAlgError:
            return {"error": "La matriz Jacobiana es singular. Cambia los valores iniciales."}
        except Exception as e:
            return {"error": f"Error en Newton para SENL: {e}"}
class MetodoGaussSeidel:
    def calcular(self, matriz_str, vector_str, x0_str, tolerancia, max_iter=100):
        try:
            # 1. Parseo seguro de entradas
            a = parse_matrix(matriz_str)
            b = parse_vector(vector_str)
            x = parse_vector(x0_str)
            
            # 2. Validaciones matemáticas críticas
            if a.shape[0] != a.shape[1]:
                return {"error": "Gauss-Seidel requiere una matriz cuadrada."}
            if b.size != a.shape[0] or x.size != a.shape[0]:
                return {"error": "b y x0 deben tener la misma dimension que A (el mismo número de elementos)."}
            
            # Protección contra división por cero
            if np.any(np.abs(np.diag(a)) < 1e-12):
                return {"error": "Gauss-Seidel no puede usar una diagonal con ceros. Reordena las filas de tus ecuaciones."}
                
            tolerancia = parse_positive_tolerance(tolerancia)
            max_iter = parse_positive_int(max_iter, "El maximo de iteraciones")

            n = a.shape[0]
            iteraciones = []
            advertencia = ""
            
            # Advertencia de convergencia (Matriz Diagonalmente Dominante)
            diag_abs = np.abs(np.diag(a))
            row_sums = np.sum(np.abs(a), axis=1) - diag_abs
            if not np.all(diag_abs > row_sums):
                advertencia = "La matriz no es diagonalmente dominante; el método de Gauss-Seidel podría divergir."

            x_ant = x.copy()
            
            # 3. Bucle Iterativo de Gauss-Seidel
            for i in range(1, max_iter + 1):
                x_new = x_ant.copy()
                
                for j in range(n):
                    # Aquí está la magia: usa x_new (lo recién calculado) y x_ant (lo viejo restante)
                    sum1 = np.dot(a[j, :j], x_new[:j])
                    sum2 = np.dot(a[j, j+1:], x_ant[j+1:])
                    x_new[j] = (b[j] - sum1 - sum2) / a[j, j]
                    
                # 4. Cálculo de Error Relativo Porcentual
                denom = np.maximum(np.abs(x_new), 1e-12) # Evitar división por cero
                error = float(np.max(np.abs((x_new - x_ant) / denom)) * 100)
                
                iteraciones.append([i, *[_format_number(v) for v in x_new], _format_number(error)])
                
                if error <= tolerancia:
                    return {
                        "exito": True,
                        "advertencia": advertencia,
                        "solucion": [_format_number(v) for v in x_new],
                        "iteraciones": iteraciones,
                    }
                x_ant = x_new.copy()

            return {"error": f"Gauss-Seidel no converge en {max_iter} iteraciones. {advertencia}".strip()}
            
        except Exception as e:
            return {"error": f"Error inesperado en Gauss-Seidel: {e}"}

class MetodoTrazadoresCubicos:
    def calcular(self, puntos_str, evaluar_en=None):
        try:
            points = parse_points(puntos_str)
            
            # Validación Ninja 1: Mínimo de puntos
            if len(points) < 3:
                return {"error": "Los trazadores cúbicos requieren al menos 3 puntos para generar curvas suaves."}
                
            # Validación Ninja 2: Ordenar los puntos por el eje X automáticamente
            # (Por si el usuario los ingresa en desorden)
            points = sorted(points, key=lambda p: p[0])
            
            xs = np.array([p[0] for p in points], dtype=float)
            ys = np.array([p[1] for p in points], dtype=float)
            n = len(points) - 1
            
            # Diferencias entre puntos (h)
            h = np.diff(xs)
            
            # Construcción del sistema tridiagonal (Vector alpha)
            alpha = np.zeros(n)
            for i in range(1, n):
                alpha[i] = (3.0 / h[i]) * (ys[i+1] - ys[i]) - (3.0 / h[i-1]) * (ys[i] - ys[i-1])
                
            # Resolución del sistema tridiagonal para encontrar los coeficientes "c"
            l = np.ones(n + 1)
            mu = np.zeros(n + 1)
            z = np.zeros(n + 1)
            
            for i in range(1, n):
                l[i] = 2.0 * (xs[i+1] - xs[i-1]) - h[i-1] * mu[i-1]
                mu[i] = h[i] / l[i]
                z[i] = (alpha[i] - h[i-1] * z[i-1]) / l[i]
                
            l[n] = 1.0
            z[n] = 0.0
            c = np.zeros(n + 1)
            b = np.zeros(n)
            d = np.zeros(n)
            
            # Sustitución hacia atrás para encontrar "b" y "d"
            for j in range(n - 1, -1, -1):
                c[j] = z[j] - mu[j] * c[j+1]
                b[j] = (ys[j+1] - ys[j]) / h[j] - h[j] * (c[j+1] + 2.0 * c[j]) / 3.0
                d[j] = (c[j+1] - c[j]) / (3.0 * h[j])
                
            a = ys[:-1]
            
            # Generar los polinomios de forma visual
            ecuaciones = []
            x_sym = sp.Symbol('x')
            for j in range(n):
                # Fórmula matemática del trazador: S(x) = a + b(x-xi) + c(x-xi)^2 + d(x-xi)^3
                term_x = x_sym - xs[j]
                poly = a[j] + b[j]*term_x + c[j]*(term_x**2) + d[j]*(term_x**3)
                poly_expand = sp.expand(poly) # Sympy hace el álgebra para simplificarlo
                rango = f"{_format_number(xs[j])} <= x <= {_format_number(xs[j+1])}"
                
                ecuaciones.append({
                    "intervalo": rango,
                    "polinomio": str(poly_expand),
                    "latex_poly": sp.latex(poly_expand),
                    "a": a[j], "b": b[j], "c": c[j], "d": d[j]
                })
                
            # Evaluación de un punto específico
            valor = None
            xv = parse_optional_finite(evaluar_en, "El punto a evaluar")
            if xv is not None:
                # Validación Ninja 3: Prohibir extrapolar fuera del rango
                if xv < xs[0] or xv > xs[-1]:
                    return {"error": f"El valor a evaluar (x={xv}) está fuera del rango de los datos ingresados [{xs[0]}, {xs[-1]}]."}
                
                # Buscar en qué intervalo cae la 'x' pedida
                for j in range(n):
                    if xs[j] <= xv <= xs[j+1]:
                        term_x = xv - xs[j]
                        v = a[j] + b[j]*term_x + c[j]*(term_x**2) + d[j]*(term_x**3)
                        valor = _format_number(v)
                        break
                        
            return {
                "exito": True,
                "ecuaciones": ecuaciones,
                "valor": valor,
                "evaluado_en": _format_number(xv) if xv is not None else None
            }
            
        except Exception as e:
            return {"error": f"Error inesperado en trazadores cúbicos: {e}"}