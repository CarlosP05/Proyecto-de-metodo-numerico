import sympy as sp

class MetodoNewton:
    def __init__(self):
        self.x = sp.Symbol('x')

    def calcular(self, funcion_str, x0, tolerancia):
        """
        Calcula la raíz usando el Método de Newton-Raphson.
        """
        try:
            # 1. Interpretar la función original
            f_expr = sp.sympify(funcion_str)
            
            # 2. CALCULAR LA DERIVADA AUTOMÁTICAMENTE
            df_expr = sp.diff(f_expr, self.x)
            
            # Convertir ambas a funciones evaluables numéricamente
            f = sp.lambdify(self.x, f_expr, 'numpy') 
            df = sp.lambdify(self.x, df_expr, 'numpy')
        except Exception as e:
            return {"error": f"Error al interpretar la función: {e}"}

        iteraciones = []
        error_actual = 100.0
        x_anterior = x0
        i = 1

        # Agregar el valor inicial a la tabla (Iteración 0)
        iteraciones.append({
            "Iteración": 0,
            "xi": x0,
            "f(xi)": f(x0),
            "f'(xi)": df(x0),
            "Error (%)": None
        })

        # 3. Bucle principal
        while True:
            f_xi = f(x_anterior)
            df_xi = df(x_anterior)

            # Proteger contra división por cero (si la tangente es totalmente horizontal)
            if df_xi == 0:
                return {"error": "Error: La derivada se hizo cero. El método falla en este punto."}

            # --- FÓRMULA DE NEWTON-RAPHSON ---
            x_nuevo = x_anterior - (f_xi / df_xi)
            
            # Cálculo del Error Relativo Porcentual
            if x_nuevo != 0:
                error_actual = abs((x_nuevo - x_anterior) / x_nuevo) * 100
            else:
                error_actual = 100.0

            iteraciones.append({
                "Iteración": i,
                "xi": x_nuevo,
                "f(xi)": f(x_nuevo),
                "f'(xi)": df(x_nuevo),
                "Error (%)": error_actual
            })

            # Condición de parada
            if error_actual <= tolerancia or f(x_nuevo) == 0:
                break

            x_anterior = x_nuevo
            i += 1

            # Límite de seguridad para evitar bucles infinitos si diverge
            if i > 50: 
                return {"error": "El método diverge. No se encontró la raíz después de 50 iteraciones."}

        return {
            "exito": True,
            "raiz_aproximada": x_nuevo,
            "total_iteraciones": i,
            "derivada_str": str(df_expr), # Devolvemos la derivada en texto para mostrarla
            "tabla_iteraciones": iteraciones
        }