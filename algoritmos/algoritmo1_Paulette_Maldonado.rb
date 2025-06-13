# Sistema de gestión de inventario con validación de tipos y errores
def gestion_inventario
    inventario = []

    loop do
        puts "\n1. Agregar | 2. Buscar | 3. Eliminar | 4. Salir"
        opcion = gets.to_i
        
        case opcion
        when 1
            begin
                puts "Nombre del producto:"
                nombre = gets.strip
                raise "Nombre no puede estar vacío" if nombre.empty?
                
                puts "Precio (USD):"
                precio = Float(gets) rescue nil
                raise "Precio debe ser un número" if precio.nil?
                
                puts "Stock:"
                stock = Integer(gets) rescue nil
                raise "Stock debe ser entero" if stock.nil?
                
                producto = { nombre: nombre, precio: precio, stock: stock }
                inventario << producto
                puts "Producto añadido: #{producto[:nombre]}"
            rescue => e
                puts "Error: #{e.message}"
        end
        
        when 2
            puts "Buscar por nombre:"
            busqueda = gets.strip.downcase
            resultados = inventario.select { |p| p[:nombre].downcase.include?(busqueda) }
            
            if resultados.empty?
                puts "No se encontraron productos."
            else
                resultados.each { |p| puts "#{p[:nombre]} | $#{p[:precio]} | Stock: #{p[:stock]}" }
            end
            
        when 3
            puts "Eliminar por nombre:"
            nombre = gets.strip
            inventario.reject! { |p| p[:nombre].downcase == nombre.downcase }
            puts "Producto eliminado."
            
        when 4
            break
            
        else
            puts "Opción no válida."
        end
    end
end

gestion_inventario
