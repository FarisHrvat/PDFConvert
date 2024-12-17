import tkinter as tk
from tkinter import filedialog, ttk
import fitz
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from pathlib import Path
import sys
import tempfile

class PDFConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Image PDF Converter")
        self.root.geometry("700x220")

        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="Input PDF:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        ttk.Label(main_frame, text="Output Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_name = tk.StringVar(value="converted")
        ttk.Entry(main_frame, textvariable=self.output_name, width=50).grid(row=1, column=1, padx=5)
        ttk.Label(main_frame, text=".pdf").grid(row=1, column=2, sticky=tk.W)

        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=3, pady=20)

        self.status_var = tk.StringVar(value="Ready to convert")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=3)

        self.convert_btn = ttk.Button(main_frame, text="Convert", command=self.convert)
        self.convert_btn.grid(row=4, column=0, columnspan=3, pady=20)

    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.input_path.set(filename)

    def get_desktop_path(self):
        return str(Path.home() / "Desktop")

    def convert(self):
        if not self.input_path.get():
            self.status_var.set("Please select an input file")
            return
            
        self.convert_btn.state(['disabled'])
        self.status_var.set("Converting...")
        self.progress['value'] = 0
        self.root.update()
        
        try:
            output_path = os.path.join(
                self.get_desktop_path(),
                f"{self.output_name.get()}.pdf"
            )

            self.progress['value'] = 20
            self.root.update()
            
            original_chars, converted_chars = self.convert_pdf_to_image_pdf(
                self.input_path.get(),
                output_path
            )
            
            self.progress['value'] = 100
            self.status_var.set(f"Conversion complete! Saved to Desktop")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.convert_btn.state(['!disabled'])
            
    def convert_pdf_to_image_pdf(self, input_pdf_path, output_pdf_path):
        original_chars = self.count_pdf_characters(input_pdf_path)
        pdf_document = fitz.open(input_pdf_path)
        
        # Create a temporary directory using tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []
            for page_num in range(pdf_document.page_count):
                self.progress['value'] = 20 + (40 * (page_num / pdf_document.page_count))
                self.root.update()
                
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                image_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
                pix.save(image_path)
                image_paths.append(image_path)

            c = canvas.Canvas(output_pdf_path, pagesize=letter)
            
            for i, image_path in enumerate(image_paths):
                self.progress['value'] = 60 + (30 * (i / len(image_paths)))
                self.root.update()
                
                img = Image.open(image_path)
                
                aspect = img.width / img.height
                if aspect > letter[0] / letter[1]:
                    img_width = letter[0] - 40
                    img_height = img_width / aspect
                else:
                    img_height = letter[1] - 40
                    img_width = img_height * aspect
                    
                x = (letter[0] - img_width) / 2
                y = (letter[1] - img_height) / 2
                
                c.drawImage(image_path, x, y, width=img_width, height=img_height)
                c.showPage()
                
            c.save()
            
        pdf_document.close()
        
        converted_chars = self.count_pdf_characters(output_pdf_path)
        
        return original_chars, converted_chars
    
    def count_pdf_characters(self, pdf_path):
        pdf_document = fitz.open(pdf_path)
        total_chars = 0
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text = page.get_text()
            total_chars += len(text)
            
        pdf_document.close()
        return total_chars

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFConverterGUI(root)
    root.mainloop()
