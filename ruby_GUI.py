import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import datetime
from ruby_lexer import lexer
from ruby_sintax import parser, tabla_variables, errores_semanticos, errores_sintacticos, metodos_definidos, analizar_archivo_ruby, realizar_analisis_semantico
import json

class RubyAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ruby Analyzer - Professional Code Analysis Tool")
        self.root.geometry("1400x800")
        
        # Colores pasteles modernos
        self.colors = {
            'bg_main': '#F5F7FA',           # Gris muy claro
            'bg_secondary': '#FFFFFF',       # Blanco
            'accent': "#94D4F4",            # Lavanda
            'accent_hover': "#5BBFE3",      # Lavanda oscuro
            'success': '#68D391',           # Verde menta
            'error': '#FC8181',             # Rosa coral
            'warning': '#F6E05E',           # Amarillo pastel
            'info': "#65B2F1",              # Azul cielo
            'text_primary': '#2D3748',      # Gris oscuro
            'text_secondary': '#718096',     # Gris medio
            'border': '#E2E8F0'             # Gris claro para bordes
        }
        
        self.root.configure(bg=self.colors['bg_main'])
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para el Notebook
        style.configure('Pastel.TNotebook', 
                       background=self.colors['bg_main'],
                       borderwidth=0)
        style.configure('Pastel.TNotebook.Tab',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       padding=[20, 10],
                       borderwidth=0)
        style.map('Pastel.TNotebook.Tab',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        # Estilo para los botones
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 10])
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_hover'])])
        
    def create_widgets(self):
        # Header con gradiente simulado
        self.create_header()
        
        # Contenedor principal
        main_container = tk.Frame(self.root, bg=self.colors['bg_main'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Panel izquierdo - Editor
        left_panel = tk.Frame(main_container, bg=self.colors['bg_main'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_editor_panel(left_panel)
        
        # Panel derecho - Resultados
        right_panel = tk.Frame(main_container, bg=self.colors['bg_main'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_results_panel(right_panel)
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Crear header con diseño moderno"""
        header_frame = tk.Frame(self.root, bg=self.colors['accent'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Contenedor interno para centrar contenido
        inner_header = tk.Frame(header_frame, bg=self.colors['accent'])
        inner_header.pack(expand=True)
        
        # Título
        title_label = tk.Label(inner_header, 
                              text="Ruby Code Analyzer",
                              font=("Segoe UI", 24, "bold"),
                              bg=self.colors['accent'],
                              fg="white")
        title_label.pack(pady=(20, 5))
        
    def create_editor_panel(self, parent):
        """Crear panel del editor con botones"""
        # Frame para el editor
        editor_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief=tk.FLAT, bd=1)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título del panel
        title_frame = tk.Frame(editor_frame, bg=self.colors['bg_secondary'])
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        tk.Label(title_frame,
                text="Ruby Code Editor",
                font=("Segoe UI", 14, "bold"),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        # Botones de acción
        button_frame = tk.Frame(editor_frame, bg=self.colors['bg_secondary'])
        button_frame.pack(fill=tk.X, padx=15, pady=5)
        
        buttons_config = [
            ("📁 Open File", self.open_file, self.colors['info']),
            ("▶️ Analyze", self.analyze, self.colors['success']),
            ("🗑️ Clear", self.clear_all, self.colors['error']),
            ("💾 Export Report", self.export_report, self.colors['warning'])
        ]
        
        for text, command, color in buttons_config:
            btn = tk.Button(button_frame,
                           text=text,
                           command=command,
                           bg=color,
                           fg="white",
                           font=("Segoe UI", 10, "bold"),
                           relief=tk.FLAT,
                           padx=15,
                           pady=8,
                           cursor="hand2")
            btn.pack(side=tk.LEFT, padx=5)
            
            # Efecto hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.darken_color(b['bg'])))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        
        # Editor de código
        editor_container = tk.Frame(editor_frame, bg=self.colors['border'])
        editor_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.editor = scrolledtext.ScrolledText(editor_container,
                                               font=("Consolas", 11),
                                               bg=self.colors['bg_main'],
                                               fg=self.colors['text_primary'],
                                               insertbackground=self.colors['accent'],
                                               selectbackground=self.colors['info'],
                                               wrap=tk.WORD,
                                               relief=tk.FLAT,
                                               padx=10,
                                               pady=10)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Agregar números de línea (simulado con texto)
        self.editor.insert(1.0, """# Ejemplo de código Ruby
def saludar(nombre)
  puts "Hola, #{nombre}!"
end

saludar("Mundo")""")
        
    def create_results_panel(self, parent):
        """Crear panel de resultados con pestañas"""
        results_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief=tk.FLAT, bd=1)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = tk.Frame(results_frame, bg=self.colors['bg_secondary'])
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(title_frame,
                text="Analysis Results",
                font=("Segoe UI", 14, "bold"),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        # Notebook con pestañas
        notebook = ttk.Notebook(results_frame, style='Pastel.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Pestaña de análisis léxico
        self.lexical_frame = self.create_analysis_tab(notebook, "🔤 Lexical Analysis")
        notebook.add(self.lexical_frame, text="🔤 Lexical")
        
        # Pestaña de análisis sintáctico
        self.syntactic_frame = self.create_analysis_tab(notebook, "🌳 Syntactic Analysis")
        notebook.add(self.syntactic_frame, text="🌳 Syntactic")
        
        # Pestaña de análisis semántico
        self.semantic_frame = self.create_analysis_tab(notebook, "🧠 Semantic Analysis")
        notebook.add(self.semantic_frame, text="🧠 Semantic")
        
        # Pestaña de reporte
        self.report_frame = self.create_analysis_tab(notebook, "📊 Complete Report")
        notebook.add(self.report_frame, text="📊 Report")
        
    def create_analysis_tab(self, parent, title):
        """Crear una pestaña de análisis"""
        frame = tk.Frame(parent, bg=self.colors['bg_main'])
        
        # Título de la sección
        title_label = tk.Label(frame,
                              text=title,
                              font=("Segoe UI", 12, "bold"),
                              bg=self.colors['bg_main'],
                              fg=self.colors['text_primary'])
        title_label.pack(pady=(10, 5))
        
        # Área de texto
        text_frame = tk.Frame(frame, bg=self.colors['border'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame,
                                               font=("Consolas", 10),
                                               bg="white",
                                               fg=self.colors['text_primary'],
                                               wrap=tk.WORD,
                                               relief=tk.FLAT,
                                               state=tk.DISABLED,
                                               padx=10,
                                               pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Guardar referencia al widget de texto
        frame.text_widget = text_widget
        
        return frame
        
    def create_status_bar(self):
        """Crear barra de estado"""
        self.status_bar = tk.Label(self.root,
                                  text="✨ Ready to analyze Ruby code",
                                  bg=self.colors['text_primary'],
                                  fg="white",
                                  font=("Segoe UI", 10),
                                  anchor=tk.W,
                                  padx=20,
                                  pady=8)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def darken_color(self, color):
        """Oscurecer un color para efectos hover"""
        # Convertir hex a RGB
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        # Oscurecer
        darker = tuple(int(c * 0.85) for c in rgb)
        # Convertir de vuelta a hex
        return '#{:02x}{:02x}{:02x}'.format(*darker)
        
    def open_file(self):
        """Abrir archivo Ruby"""
        file_path = filedialog.askopenfilename(
            title="Open Ruby File",
            filetypes=[("Ruby files", "*.rb"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.editor.delete(1.0, tk.END)
                    self.editor.insert(1.0, content)
                self.update_status(f"📁 Loaded: {file_path.split('/')[-1]}", "info")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
                
    def analyze(self):
        """Realizar análisis completo"""
        code = self.editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter some Ruby code to analyze")
            return
            
        self.update_status("🔄 Analyzing code...", "info")
        self.root.update()
        
        try:
            # Limpiar resultados anteriores
            self.clear_results()
            
            # Reiniciar estado
            global errores_sintacticos, errores_semanticos, tabla_variables, metodos_definidos
            errores_sintacticos = []
            errores_semanticos = []
            tabla_variables.clear()
            metodos_definidos.clear()
            
            # Análisis léxico
            self.perform_lexical_analysis(code)
            
            # Análisis sintáctico
            ast = self.perform_syntactic_analysis(code)
            
            # Análisis semántico
            self.perform_semantic_analysis(ast)
            
            # Generar reporte
            self.generate_report()
            
            # Actualizar estado
            total_errors = len(errores_sintacticos) + len(errores_semanticos)
            if total_errors == 0:
                self.update_status("✅ Analysis completed successfully!", "success")
            else:
                self.update_status(f"⚠️ Analysis completed with {total_errors} error(s)", "warning")
                
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.update_status("❌ Analysis failed", "error")
            
    def perform_lexical_analysis(self, code):
        """Realizar análisis léxico"""
        text_widget = self.lexical_frame.text_widget
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        # Reiniciar lexer
        lexer.lineno = 1
        lexer.input(code)
        
        # Analizar tokens
        tokens_found = []
        token_count = {}
        
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens_found.append((tok.type, tok.value, tok.lineno))
            token_count[tok.type] = token_count.get(tok.type, 0) + 1
            
        # Mostrar resultados
        text_widget.insert(tk.END, "=== LEXICAL ANALYSIS RESULTS ===\n\n")
        text_widget.insert(tk.END, f"Total tokens found: {len(tokens_found)}\n\n")
        
        # Resumen por tipo de token
        text_widget.insert(tk.END, "Token Summary:\n")
        text_widget.insert(tk.END, "-" * 40 + "\n")
        for token_type, count in sorted(token_count.items()):
            text_widget.insert(tk.END, f"{token_type:<20} : {count:>5}\n")
            
        # Detalle de tokens
        text_widget.insert(tk.END, "\n\nDetailed Token List:\n")
        text_widget.insert(tk.END, "-" * 60 + "\n")
        text_widget.insert(tk.END, f"{'Line':<6} {'Token Type':<20} {'Value':<30}\n")
        text_widget.insert(tk.END, "-" * 60 + "\n")
        
        for token_type, value, line in tokens_found[:50]:  # Mostrar primeros 50
            value_str = str(value)[:30]
            text_widget.insert(tk.END, f"{line:<6} {token_type:<20} {value_str:<30}\n")
            
        if len(tokens_found) > 50:
            text_widget.insert(tk.END, f"\n... and {len(tokens_found) - 50} more tokens\n")
            
        text_widget.config(state=tk.DISABLED)
        
    def perform_syntactic_analysis(self, code):
        """Realizar análisis sintáctico"""
        text_widget = self.syntactic_frame.text_widget
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        text_widget.insert(tk.END, "=== SYNTACTIC ANALYSIS RESULTS ===\n\n")
        
        # Reiniciar lexer
        lexer.lineno = 1
        
        # Parsear
        ast = None
        try:
            ast = parser.parse(code, lexer=lexer)
            
            if errores_sintacticos:
                text_widget.insert(tk.END, "❌ Syntax Errors Found:\n")
                text_widget.insert(tk.END, "-" * 60 + "\n")
                for error in errores_sintacticos:
                    text_widget.insert(tk.END, f"• {error}\n")
            else:
                text_widget.insert(tk.END, "✅ Syntax Analysis: PASSED\n\n")
                text_widget.insert(tk.END, "✓ No syntax errors found\n")
                text_widget.insert(tk.END, "✓ Code structure is valid\n")
                text_widget.insert(tk.END, "✓ All constructs are properly formed\n\n")
                
                # Mostrar AST simplificado
                if ast:
                    text_widget.insert(tk.END, "\nAbstract Syntax Tree (simplified):\n")
                    text_widget.insert(tk.END, "-" * 40 + "\n")
                    ast_str = self.format_ast(ast, indent=0)
                    text_widget.insert(tk.END, ast_str[:1000])  # Primeros 1000 caracteres
                    if len(ast_str) > 1000:
                        text_widget.insert(tk.END, "\n... (truncated)")
                        
        except Exception as e:
            text_widget.insert(tk.END, f"❌ Parse Error: {str(e)}\n")
            
        text_widget.config(state=tk.DISABLED)
        return ast
        
    def perform_semantic_analysis(self, ast):
        """Realizar análisis semántico"""
        text_widget = self.semantic_frame.text_widget
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        text_widget.insert(tk.END, "=== SEMANTIC ANALYSIS RESULTS ===\n\n")
        
        # Realizar análisis solo si no hay errores sintácticos
        if not errores_sintacticos and ast:
            realizar_analisis_semantico(ast)
            
        # Variables encontradas
        if tabla_variables:
            text_widget.insert(tk.END, f"📊 Variables Found ({len(tabla_variables)}):\n")
            text_widget.insert(tk.END, "-" * 40 + "\n")
            for var, info in tabla_variables.items():
                if isinstance(info, dict):
                    text_widget.insert(tk.END, f"• {var:<15} : {info.get('tipo', 'unknown'):<10} (context: {info.get('contexto', 'global')})\n")
                else:
                    text_widget.insert(tk.END, f"• {var:<15} : {type(info).__name__}\n")
                    
        # Métodos definidos
        if metodos_definidos:
            text_widget.insert(tk.END, f"\n📌 Methods Defined ({len(metodos_definidos)}):\n")
            text_widget.insert(tk.END, "-" * 40 + "\n")
            for method, info in metodos_definidos.items():
                params = info.get('params', [])
                text_widget.insert(tk.END, f"• {method}({', '.join(params)})\n")
                
        # Errores semánticos
        if errores_semanticos:
            text_widget.insert(tk.END, f"\n❌ Semantic Errors ({len(errores_semanticos)}):\n")
            text_widget.insert(tk.END, "-" * 40 + "\n")
            for error in errores_semanticos:
                text_widget.insert(tk.END, f"• {error}\n")
        else:
            text_widget.insert(tk.END, "\n✅ Semantic Analysis: PASSED\n")
            text_widget.insert(tk.END, "✓ No semantic errors detected\n")
            text_widget.insert(tk.END, "✓ All variables are properly used\n")
            text_widget.insert(tk.END, "✓ Type consistency maintained\n")
            
        text_widget.config(state=tk.DISABLED)
        
    def generate_report(self):
        """Generar reporte completo"""
        text_widget = self.report_frame.text_widget
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        # Header del reporte
        text_widget.insert(tk.END, "=" * 70 + "\n")
        text_widget.insert(tk.END, "                    RUBY CODE ANALYSIS REPORT\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")
        
        # Información general
        text_widget.insert(tk.END, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        text_widget.insert(tk.END, f"Analyzer: Ruby Code Analyzer v1.0\n\n")
        
        # Resumen ejecutivo
        total_errors = len(errores_sintacticos) + len(errores_semanticos)
        status = "PASSED ✅" if total_errors == 0 else f"FAILED ❌ ({total_errors} errors)"
        
        text_widget.insert(tk.END, "EXECUTIVE SUMMARY\n")
        text_widget.insert(tk.END, "-" * 30 + "\n")
        text_widget.insert(tk.END, f"Overall Status: {status}\n")
        text_widget.insert(tk.END, f"Lines of Code: {len(self.editor.get(1.0, tk.END).strip().split(chr(10)))}\n")
        text_widget.insert(tk.END, f"Syntax Errors: {len(errores_sintacticos)}\n")
        text_widget.insert(tk.END, f"Semantic Errors: {len(errores_semanticos)}\n")
        text_widget.insert(tk.END, f"Variables Declared: {len(tabla_variables)}\n")
        text_widget.insert(tk.END, f"Methods Defined: {len(metodos_definidos)}\n\n")
        
        # Detalles de errores
        if errores_sintacticos:
            text_widget.insert(tk.END, "SYNTAX ERRORS\n")
            text_widget.insert(tk.END, "-" * 30 + "\n")
            for i, error in enumerate(errores_sintacticos, 1):
                text_widget.insert(tk.END, f"{i}. {error}\n")
            text_widget.insert(tk.END, "\n")
            
        if errores_semanticos:
            text_widget.insert(tk.END, "SEMANTIC ERRORS\n")
            text_widget.insert(tk.END, "-" * 30 + "\n")
            for i, error in enumerate(errores_semanticos, 1):
                text_widget.insert(tk.END, f"{i}. {error}\n")
            text_widget.insert(tk.END, "\n")
            
        # Análisis de código
        if tabla_variables or metodos_definidos:
            text_widget.insert(tk.END, "CODE ANALYSIS\n")
            text_widget.insert(tk.END, "-" * 30 + "\n")
            
            if tabla_variables:
                text_widget.insert(tk.END, "\nVariables:\n")
                for var, info in tabla_variables.items():
                    if isinstance(info, dict):
                        text_widget.insert(tk.END, f"  - {var} ({info.get('tipo', 'unknown')})\n")
                    else:
                        text_widget.insert(tk.END, f"  - {var}\n")
                        
            if metodos_definidos:
                text_widget.insert(tk.END, "\nMethods:\n")
                for method, info in metodos_definidos.items():
                    params = info.get('params', [])
                    text_widget.insert(tk.END, f"  - {method}({', '.join(params)})\n")
                    
        # Recomendaciones
        text_widget.insert(tk.END, "\n\nRECOMMENDATIONS\n")
        text_widget.insert(tk.END, "-" * 30 + "\n")
        if total_errors == 0:
            text_widget.insert(tk.END, "✓ Code is clean and ready for execution\n")
            text_widget.insert(tk.END, "✓ Consider adding comments for better documentation\n")
            text_widget.insert(tk.END, "✓ Review variable names for clarity\n")
        else:
            text_widget.insert(tk.END, "! Fix all syntax errors before proceeding\n")
            text_widget.insert(tk.END, "! Review semantic errors for logic issues\n")
            text_widget.insert(tk.END, "! Consider refactoring problematic sections\n")
            
        text_widget.config(state=tk.DISABLED)
        
    def format_ast(self, node, indent=0):
        """Formatear AST para visualización"""
        if node is None:
            return ""
            
        result = ""
        spaces = "  " * indent
        
        if isinstance(node, tuple):
            result += f"{spaces}{node[0]}\n"
            for child in node[1:]:
                result += self.format_ast(child, indent + 1)
        elif isinstance(node, list):
            for item in node:
                result += self.format_ast(item, indent)
        else:
            result += f"{spaces}{repr(node)}\n"
            
        return result
        
    def clear_results(self):
        """Limpiar todos los resultados"""
        for frame in [self.lexical_frame, self.syntactic_frame, self.semantic_frame, self.report_frame]:
            frame.text_widget.config(state=tk.NORMAL)
            frame.text_widget.delete(1.0, tk.END)
            frame.text_widget.config(state=tk.DISABLED)
            
    def clear_all(self):
        """Limpiar todo"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all content?"):
            self.editor.delete(1.0, tk.END)
            self.clear_results()
            tabla_variables.clear()
            errores_sintacticos.clear()
            errores_semanticos.clear()
            metodos_definidos.clear()
            self.update_status("🧹 All content cleared", "info")
            
    def export_report(self):
        """Exportar reporte a archivo"""
        report_content = self.report_frame.text_widget.get(1.0, tk.END).strip()
        if not report_content:
            messagebox.showwarning("Warning", "No report to export. Please run analysis first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                messagebox.showinfo("Success", f"Report exported successfully to:\n{file_path}")
                self.update_status("💾 Report exported successfully", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
                
    def update_status(self, message, status_type="info"):
        """Actualizar barra de estado con colores"""
        colors = {
            "info": self.colors['info'],
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "error": self.colors['error']
        }
        
        bg_color = colors.get(status_type, self.colors['text_primary'])
        self.status_bar.config(text=f"  {message}", bg=bg_color)

def main():
    root = tk.Tk()
    app = RubyAnalyzerGUI(root)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()