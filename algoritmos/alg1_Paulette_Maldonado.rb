# --- Ejemplo (1): Código Correcto ---
puts "\n[1] Ejemplo Correcto:"
numeros_correctos = [1, 2, 3, 4, 5]

def sumar_arreglo_correcto(arreglo)
  suma = 0
  for num in arreglo
    suma = suma + num
  end
  return suma
end

resultado_correcto = sumar_arreglo_correcto(numeros_correctos)
puts "La suma es: #{resultado_correcto}"
