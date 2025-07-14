numeros_semanticos = ["uno", "dos", "tres", "cuatro", "cinco"]
def encontrar_numero(numeros_semanticos)
  resultado = ""
  for num in numeros_semanticos
    if num == "tres"
      resultado = num
    else
      resultado = "no encontrado"
    end
  end
  return "El resultado es: " + resultado
end

puts encontrar_numero(numeros_semanticos)
