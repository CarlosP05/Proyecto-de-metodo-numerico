import sympy as sp

class MetodoSecante:
    def __init__(self):
        self.x = sp.Symbol('x')

    def calcular(self, funcion_str, x0, x1, tolerancia):
        """
        Calcula la raíz usando el Método de la Secante.
        """
        try:
            # Interpretar la función original
            f_expr = sp.sympify(funcion_str)
            f = sp.lambdify(self.x, f_expr, 'numpy') 
        except Exception as e:
            return {"error": f"Error al interpretar la función: {e}"}

        iteraciones = []
        
        # Evaluamos los dos primeros puntos
        f_x0 = f(x0)
        f_x1 = f(x1)

        # Agregamos los puntos iniciales a nuestra tabla visual
        iteraciones.append({
            "Iteración": 0,
            "xi_anterior": None,
            "xi": x0,
            "f(xi)": f_x0,
            "Error (%)": None
        })
        iteraciones.append({
            "Iteración": 1,
            "xi_anterior": x0,
            "xi": x1,
            "f(xi)": f_x1,
            "Error (%)": None
        })

        x_anterior = x0
        x_actual = x1
        f_anterior = f_x0
        f_actual = f_x1
        i = 2 # Empezamos a calcular desde la iteración 2

        # Bucle principal
        while True:
            # Proteger contra división por cero
            if f_actual - f_anterior == 0:
                return {"error": "Error: La diferencia entre f(xi) y f(xi-1) es cero. División por cero."}

            # --- FÓRMULA DE LA SECANTE ---
            x_nuevo = x_actual - (f_actual * (x_actual - x_anterior)) / (f_actual - f_anterior)
            f_nuevo = f(x_nuevo)
            
            # Cálculo del Error Relativo Porcentual
            if x_nuevo != 0:
                error_actual = abs((x_nuevo - x_actual) / x_nuevo) * 100
            else:
                error_actual = 100.0

            iteraciones.append({
                "Iteración": i,
                "xi_anterior": x_actual,
                "xi": x_nuevo,
                "f(xi)": f_nuevo,
                "Error (%)": error_actual
            })

            # Condición de parada
            if error_actual <= tolerancia or f_nuevo == 0:
                break

            # Preparar la siguiente iteración (desplazamos los valores)
            x_anterior = x_actual
            f_anterior = f_actual
            x_actual = x_nuevo
            f_actual = f_nuevo
            i += 1

            if i > 50: 
                return {"error": "El método diverge. No se encontró la raíz después de 50 iteraciones."}

        return {
            "exito": True,
            "raiz_aproximada": x_nuevo,
            "total_iteraciones": i,
            "tabla_iteraciones": iteraciones
        }