puts "\n[2] Ejemplo Sintácticamente Incorrecto:"
numeros_sintacticos = [1, 2, 3, 4, 5]

def sumar_arreglo_sintactico(arreglo)
  suma = 0
  for num arreglo  # falta 'in'
    suma = suma + num
  end
  return suma
end