# --- Ejemplo (1): Código Correcto ---
puts "\n[1] Ejemplo Correcto:"
puts "\nIteración con FOR:"

palabras = ["Ruby", "Parser", "PLY", "Analizador"]

for palabra in palabras
  puts "Palabra: #{palabra} (Longitud: #{palabra.length})"
end
