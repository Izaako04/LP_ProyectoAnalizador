require 'set'

conjunto_sintactico = Set.new([1, 2, 3, 4, 5])

indice = 0
arreglo_sintactico = conjunto_sintactico.to_a

while indice < arreglo_sintactico.size
  puts "Número: #{arreglo_sintactico[indice]}"
  indice += 1