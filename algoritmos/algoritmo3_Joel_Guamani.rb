# Sistema de reservas usando Hash
def sistema_reservas
    reservas = {} # Hash para guardar reservas (clave: ID, valor: datos de reserva)
    
    loop do
        puts "\n1. Nueva reserva | 2. Consultar reserva | 3. Salir"
        opcion = gets.to_i
        
        case opcion
        when 1
            begin
                puts "ID de reserva (ej: R100):"
                id = gets.strip.upcase
                raise "ID debe empezar con 'R' seguido de números" unless id.match?(/^R\d+$/)
                
                puts "Nombre del cliente:"
                nombre = gets.strip
                raise "Nombre no puede estar vacío" if nombre.empty?
                
                puts "Fecha de entrada (DD-MM-AAAA):"
                fecha_entrada = gets.strip
                raise "Formato de fecha incorrecto" unless fecha_entrada.match?(/^\d{2}-\d{2}-\d{4}$/)
                
                puts "Noches (máx 30):"
                noches = Integer(gets) rescue nil
                raise "Noches debe ser un número entre 1 y 30" if noches.nil? || noches <= 0 || noches > 30
                
                reservas[id] = {
                nombre: nombre,
                fecha_entrada: fecha_entrada,
                noches: noches,
                estado: "confirmada"
                }
                
                puts "Reserva #{id} registrada para #{nombre}."
            rescue => e
                puts " Error: #{e.message}"
            end
        
        when 2
            puts "ID de reserva a consultar:"
            id = gets.strip.upcase
            reserva = reservas[id]
            
            if reserva
                puts "\n Detalles de reserva #{id}:"
                puts "• Cliente: #{reserva[:nombre]}"
                puts "• Fecha entrada: #{reserva[:fecha_entrada]}"
                puts "• Noches: #{reserva[:noches]}"
                puts "• Estado: #{reserva[:estado]}"
            else
                puts "Reserva no encontrada."
        end
        
        when 3
            break
        
        else
            puts "Opción no válida."
        end
    end
end

sistema_reservas
