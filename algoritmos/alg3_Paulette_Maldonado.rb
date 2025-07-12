numeros_semanticos = ["uno", "dos", "tres", "cuatro", "cinco"]

def sumar_arreglo_semantico(arreglo)
  suma = 0
  for num in arreglo
    suma = suma + num
  end
  return "La suma es: " + suma
end