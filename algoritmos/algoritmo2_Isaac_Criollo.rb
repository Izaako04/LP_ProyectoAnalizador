require 'set'

def procesar_datos
    datos = Set.new
    
    puts "Ingrese datos numéricos (separados por espacios):"
    entrada = gets.split
    
    entrada.each do |dato|
        if dato.match?(/^-?\d+\.?\d*$/) # Admite negativos y flotantes
        datos.add(dato.include?('.') ? dato.to_f : dato.to_i)
        else
        puts "'#{dato}' no es un número válido. Se omitirá."
        end
    end
    
    unless datos.empty?
        puts "\n Resultados:"
        puts "• Total: #{datos.size} elementos"
        puts "• Máximo: #{datos.max}"
        puts "• Mínimo: #{datos.min}"
        puts "• Suma: #{datos.sum}"
        puts "• Promedio: #{datos.sum / datos.size}"
    else
        puts " No se ingresaron datos válidos."
    end
end

procesar_datos