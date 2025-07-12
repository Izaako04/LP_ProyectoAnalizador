def verificar_edad
  persona_semantica = {nombre: "Pedro", edad: 20}

  if persona_semantica[:edad] >= 18
    mensaje = "#{persona_semantica[:nombre]} es mayor de edad."
  else
    mensaje = "#{persona_semantica[:nombre]} es menor de edad."
  end
end

puts mensaje
