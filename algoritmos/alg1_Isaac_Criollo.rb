require 'set'

conjunto_numeros = Set.new([1, 2, 3, 4, 5])

indice = 0
arreglo_numeros = conjunto_numeros.to_a

while indice < arreglo_numeros.size
  puts "Número: #{arreglo_numeros[indice]}"
  indice += 1
end