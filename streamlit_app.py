import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io
import os
import streamlit as st


st.title("Application for Wasif Khan")


def extract_images_from_pdf(input_pdf_path):
    images = []
    try:
        doc = fitz.open(input_pdf_path)
        print(f"Opened PDF: {input_pdf_path}")

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            print(f"Found {len(image_list)} images on page {page_num + 1}")

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                images.append((image, page_num + 1))  # Store the image and its page number
                print(f"Extracted image {img_index + 1} on page {page_num + 1}")

    except Exception as e:
        print(f"Error extracting images: {e}")
    
    return images

def create_pdf_with_images(images, output_pdf_path):
    try:
        c = canvas.Canvas(output_pdf_path, pagesize=letter)
        width, height = letter
        print(f"Creating PDF: {output_pdf_path}")

        for img_index, (img, page_num) in enumerate(images):
            img_width, img_height = img.size
            aspect_ratio = img_height / img_width
            resized_height = int(width * aspect_ratio)

            if resized_height > height:
                resized_height = height
                resized_width = int(height / aspect_ratio)
            else:
                resized_width = width

            img = img.resize((int(resized_width), int(resized_height)))
            temp_image_path = f"temp_image_{img_index}.png"
            img.save(temp_image_path)

            x = (width - resized_width) / 2
            y = (height - resized_height) / 2

            c.drawImage(temp_image_path, x, y, resized_width, resized_height)
            c.showPage()
            print(f"Added image {img_index + 1} from page {page_num} to PDF")

        c.save()
        print(f"Saved PDF: {output_pdf_path}")
        
        # Remove temporary image files
        for img_index in range(len(images)):
            os.remove(f"temp_image_{img_index}.png")
            print(f"Removed temporary image file temp_image_{img_index}.png")

    except Exception as e:
        print(f"Error creating PDF: {e}")

def main():
    st.title("PDF Image Extractor and Selector")

    input_pdf_file = st.file_uploader("Upload your PDF file", type="pdf")
    if input_pdf_file is not None:
        input_pdf_file_path = os.path.join("temp_input.pdf")
        with open(input_pdf_file_path, "wb") as f:
            f.write(input_pdf_file.read())

        extracted_images = extract_images_from_pdf(input_pdf_file_path)

        if extracted_images:
            selected_images = []
            for img_index, (image, page_num) in enumerate(extracted_images):
                st.image(image, caption=f"Page {page_num}", use_column_width=True)
                if st.checkbox(f"Include image from page {page_num}", key=img_index):
                    selected_images.append((image, page_num))

            if st.button("Create PDF"):
                output_pdf_file_path = "output.pdf"
                create_pdf_with_images(selected_images, output_pdf_file_path)
                st.success("PDF created successfully!")
                with open(output_pdf_file_path, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name="selected_images.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    main()

