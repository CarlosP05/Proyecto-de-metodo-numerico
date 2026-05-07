import sympy as sp
import numpy as np

class MetodoReglaFalsa:
    def __init__(self):
        self.x = sp.Symbol('x')

    def calcular(self, funcion_str, a, b, tolerancia):
        """
        Calcula la raíz usando el Método de Regla Falsa.
        """
        # 1. Convertir la función
        try:
            f_expr = sp.sympify(funcion_str)
            f = sp.lambdify(self.x, f_expr, 'numpy') 
        except Exception as e:
            return {"error": f"Error al interpretar la función matemática: {e}"}

        # 2. Verificar existencia de la raíz
        if f(a) * f(b) >= 0:
            return {"error": "El intervalo [a, b] no es válido. Asegúrate de que f(a) * f(b) < 0."}

        iteraciones = []
        error_actual = 100.0
        c_anterior = 0
        i = 1

        # 3. Bucle principal
        while True:
            fa = f(a)
            fb = f(b)
            
            # Protección extra: evitar división por cero si f(a) y f(b) llegan a ser iguales
            if fa - fb == 0:
                return {"error": "Error: División por cero. f(a) - f(b) es igual a 0."}

            # --- NUEVO: FÓRMULA DE REGLA FALSA ---
            c = b - (fb * (a - b)) / (fa - fb)
            fc = f(c)
            
            # Cálculo del Error Relativo Porcentual
            if i > 1:
                if c != 0:
                    error_actual = abs((c - c_anterior) / c) * 100
                else:
                    error_actual = 100.0

            iteraciones.append({
                "Iteración": i,
                "a": a,
                "b": b,
                "c": c,
                "f(c)": fc,
                "Error (%)": error_actual if i > 1 else None
            })

            # Condición de parada
            if (i > 1 and error_actual <= tolerancia) or fc == 0:
                break

            # Reasignación de intervalos
            if fa * fc < 0:
                b = c  
            else:
                a = c  

            c_anterior = c
            i += 1

            if i > 200:
                break

        return {
            "exito": True,
            "raiz_aproximada": c,
            "total_iteraciones": len(iteraciones),
            "tabla_iteraciones": iteraciones
        }