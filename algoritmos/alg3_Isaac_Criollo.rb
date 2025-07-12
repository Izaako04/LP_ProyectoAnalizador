require 'set'

conjunto_semantico = Set.new(["a", "b", "c"])

indice = "cero"
arreglo_semantico = conjunto_semantico.to_a

while indice < arreglo_semantico.size
  puts "Letra: #{arreglo_semantico[indice]}"
  indice += 1
end
