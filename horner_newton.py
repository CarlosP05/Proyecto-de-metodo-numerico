import sympy as sp

class MetodoHornerNewton:
    def __init__(self):
        self.x = sp.Symbol('x')

    def calcular(self, funcion_str, x0, tolerancia):
        """
        Calcula una raíz de un polinomio usando el Método de Horner-Newton.
        Usa divisiones sintéticas para evaluar P(x) y P'(x).
        """
        try:
            # 1. Extraer los coeficientes del polinomio
            f_expr = sp.sympify(funcion_str)
            poly = sp.Poly(f_expr, self.x)
            a = poly.all_coeffs()  # Lista de coeficientes [a_n, a_{n-1}, ..., a_0]
            a = [float(c) for c in a]
        except Exception as e:
            return {"error": f"Error al leer el polinomio: {e}"}

        n = len(a) - 1 # Grado del polinomio
        if n < 1:
            return {"error": "Se requiere un polinomio de grado 1 o mayor."}

        x_anterior = float(x0)
        iteraciones = []
        i = 1
        error_actual = 100.0

        # 2. Bucle principal
        while True:
            # Arreglos para el esquema de Horner
            b = [0.0] * (n + 1)
            c = [0.0] * n  # El arreglo c tiene un elemento menos

            # 3. Aplicar el algoritmo de Horner (División sintética doble)
            b[0] = a[0]
            c[0] = b[0]

            for j in range(1, n + 1):
                # Calculamos b_j = a_j + x * b_{j-1}
                b[j] = a[j] + x_anterior * b[j-1]
                
                # Calculamos c_j = b_j + x * c_{j-1} (solo hasta n-1)
                if j < n:
                    c[j] = b[j] + x_anterior * c[j-1]

            # Según tu pizarra: P(x) = b_n  y  P'(x) = c_{n-1}
            bn = b[n]
            cn_1 = c[n-1]

            # Protección contra división por cero si la derivada es horizontal
            if cn_1 == 0:
                return {"error": "Error: La derivada P'(x) (o c_n-1) se hizo cero."}

            # 4. Fórmula de Newton usando los resultados de Horner
            x_nuevo = x_anterior - (bn / cn_1)

            # 5. Cálculo del Error Relativo Porcentual
            if x_nuevo != 0:
                error_actual = abs((x_nuevo - x_anterior) / x_nuevo) * 100
            else:
                error_actual = 100.0

            # Guardar la iteración para la tabla visual
            iteraciones.append({
                "Iteración": i,
                "xi": x_anterior,
                "P(xi) [bn]": bn,
                "P'(xi) [cn-1]": cn_1,
                "Error (%)": error_actual
            })

            # 6. Condición de parada
            if error_actual <= tolerancia or bn == 0:
                break

            x_anterior = x_nuevo
            i += 1

            if i > 50:
                return {"error": "El método diverge o es muy lento. Se detuvo en la iteración 50."}

        return {
            "exito": True,
            "raiz_aproximada": x_nuevo,
            "total_iteraciones": i,
            "tabla_iteraciones": iteraciones
        }