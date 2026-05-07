import sympy as sp
import numpy as np
import cmath  # Librería crucial para manejar raíces cuadradas de números negativos (complejos)

class MetodoMuller:
    def __init__(self):
        self.x = sp.Symbol('x')

    def calcular(self, funcion_str, x0, x1, x2, tolerancia):
        """
        Calcula la raíz de un polinomio usando el Método de Müller.
        Es capaz de encontrar raíces reales y complejas.
        """
        try:
            # 1. Interpretar la función matemática
            f_expr = sp.sympify(funcion_str)
            f_base = sp.lambdify(self.x, f_expr, 'numpy')
            
            # Envolvemos la función para asegurarnos de que acepte y devuelva números complejos
            def f(val):
                return complex(f_base(complex(val)))
                
        except Exception as e:
            return {"error": f"Error al interpretar la función: {e}"}

        # Convertimos los valores iniciales a formato complejo
        x0 = complex(x0)
        x1 = complex(x1)
        x2 = complex(x2)

        iteraciones = []
        i = 1
        error_actual = 100.0

        # 2. Bucle principal de Müller
        while True:
            # Cálculos de diferencias (como en tus apuntes)
            h0 = x1 - x0
            h1 = x2 - x1
            
            # Protección contra división por cero si dos puntos son iguales
            if h0 == 0 or h1 == 0:
                return {"error": "Error: Los puntos iniciales no pueden ser iguales."}

            d0 = (f(x1) - f(x0)) / h0
            d1 = (f(x2) - f(x1)) / h1

            # Coeficientes de la parábola
            a = (d1 - d0) / (h1 + h0)
            b = a * h1 + d1
            c = f(x2)

            # 3. Fórmula de Müller (resolver la cuadrática)
            discriminante = cmath.sqrt(b**2 - 4*a*c)

            # Elegir el signo que maximice el denominador (para mayor precisión)
            den_suma = b + discriminante
            den_resta = b - discriminante
            
            if abs(den_suma) > abs(den_resta):
                denominador = den_suma
            else:
                denominador = den_resta

            if denominador == 0:
                return {"error": "Error: El denominador se hizo cero."}

            # Calcular la nueva aproximación x3
            dx = -2 * c / denominador
            x3 = x2 + dx

            # 4. Calcular el Error Relativo Porcentual
            if abs(x3) != 0:
                error_actual = abs(dx / x3) * 100
            else:
                error_actual = 100.0

            # Formatear números para la tabla (limpiar parte imaginaria si es muy pequeña)
            def limpiar_complejo(num):
                if abs(num.imag) < 1e-10: return f"{num.real:.6f}"
                return f"{num.real:.4f} + {num.imag:.4f}j"

            iteraciones.append({
                "Iteración": i,
                "x0": limpiar_complejo(x0),
                "x1": limpiar_complejo(x1),
                "x2": limpiar_complejo(x2),
                "x3": limpiar_complejo(x3),
                "f(x3)": limpiar_complejo(f(x3)),
                "Error (%)": error_actual
            })

            # Condición de parada
            if error_actual <= tolerancia or abs(f(x3)) == 0:
                break

            # 5. Preparar la siguiente iteración (desplazamiento)
            x0 = x1
            x1 = x2
            x2 = x3
            i += 1

            # Seguro contra bucles infinitos
            if i > 100:
                return {"error": "El método diverge o es muy lento. Se detuvo en la iteración 100."}

        # Resultado final limpio
        raiz_final = x3 if abs(x3.imag) > 1e-10 else x3.real

        return {
            "exito": True,
            "raiz_aproximada": raiz_final,
            "total_iteraciones": i,
            "tabla_iteraciones": iteraciones
        }