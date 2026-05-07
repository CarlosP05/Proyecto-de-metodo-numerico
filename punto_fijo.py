import sympy as sp

class MetodoPuntoFijo:
    def __init__(self):
        self.x = sp.Symbol('x')

    def calcular(self, g_str, x0, tolerancia):
        """
        Calcula la raíz usando Iteración de Punto Fijo.
        Evalúa el criterio de convergencia |g'(x)| < 1.
        """
        try:
            # Interpretar g(x)
            g_expr = sp.sympify(g_str)
            # Calcular la derivada g'(x) automáticamente
            dg_expr = sp.diff(g_expr, self.x)
            
            g = sp.lambdify(self.x, g_expr, 'numpy')
            dg = sp.lambdify(self.x, dg_expr, 'numpy')
        except Exception as e:
            return {"error": f"Error al interpretar la función g(x): {e}"}

        iteraciones = []
        x_anterior = x0
        i = 1
        error_actual = 100.0
        
        # --- NUEVO: EVALUAR CRITERIO DE CONVERGENCIA ---
        derivada_x0 = abs(dg(x0))
        advertencia = ""
        # Si la derivada es mayor o igual a 1, advertimos que va a fallar
        if derivada_x0 >= 1:
            advertencia = f"¡CUIDADO! |g'(x0)| = {derivada_x0:.4f}. Como es >= 1, el método va a diverger."

        # Guardar iteración 0
        iteraciones.append({
            "Iteración": 0,
            "xi": x0,
            "g(xi)": g(x0),
            "|g'(xi)|": derivada_x0,
            "Error (%)": None
        })

        # Bucle principal
        while True:
            try:
                x_nuevo = g(x_anterior)
            except Exception as e:
                return {"error": f"Error matemático al evaluar g(x): {e}"}
            
            if x_nuevo != 0:
                error_actual = abs((x_nuevo - x_anterior) / x_nuevo) * 100
            else:
                error_actual = 100.0
                
            derivada_actual = abs(dg(x_nuevo))

            iteraciones.append({
                "Iteración": i,
                "xi": x_nuevo,
                "g(xi)": g(x_nuevo),
                "|g'(xi)|": derivada_actual,
                "Error (%)": error_actual
            })

            # Condición de parada
            if error_actual <= tolerancia or x_nuevo == x_anterior:
                break

            x_anterior = x_nuevo
            i += 1

            if i > 50:
                mensaje_error = advertencia + "\nEl método diverge. Se detuvo en la iteración 50." if advertencia else "El método diverge o es muy lento. Se detuvo en la iteración 50."
                return {"error": mensaje_error}

        return {
            "exito": True,
            "raiz_aproximada": x_nuevo,
            "total_iteraciones": i,
            "advertencia": advertencia,
            "tabla_iteraciones": iteraciones
        }