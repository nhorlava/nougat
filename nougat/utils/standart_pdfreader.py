# To read the PDF
import PyPDF2
# To analyze the PDF layout and extract text
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# To extract text from tables in PDF
import pdfplumber
# To extract the images from the PDFs
from PIL import Image
from pdf2image import convert_from_path
# To perform OCR to extract text from images 
import pytesseract 
# To remove the additional created files
import os
from tqdm import tqdm
from nougat.postprocessing import postprocess
import re

# Create function to extract text

def text_extraction(element):
    # Extracting the text from the in line text element
    line_text = element.get_text()
    
    # Find the formats of the text
    # Initialize the list with all the formats appeared in the line of text
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            # Iterating through each character in the line of text
            for character in text_line:
                if isinstance(character, LTChar):
                    # Append the font name of the character
                    line_formats.append(character.fontname)
                    # Append the font size of the character
                    line_formats.append(character.size)
    # Find the unique font sizes and names in the line
    format_per_line = list(set(line_formats))
    
    # Return a tuple with the text in each line along with its format
    return (line_text, format_per_line)

# Extracting tables from the page

def extract_table(pdf_path, page_num, table_num):
    # Open the pdf file
    pdf = pdfplumber.open(pdf_path)
    # Find the examined page
    table_page = pdf.pages[page_num]
    # Extract the appropriate table
    table = table_page.extract_tables()[table_num]
    
    return table

# Convert table into appropriate fromat
def table_converter(table):
    table_string = ''
    # Iterate through each row of the table
    for row_num in range(len(table)):
        row = table[row_num]
        # Remove the line breaker from the wrapted texts
        cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
        # Convert the table into a string 
        table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
    # Removing the last line break
    table_string = table_string[:-1]
    return table_string

# Create a function to check if the element is in any tables present in the page
def is_element_inside_any_table(element, page ,tables):
    x0, y0up, x1, y1up = element.bbox
    # Change the cordinates because the pdfminer counts from the botton to top of the page
    y0 = page.bbox[3] - y1up
    y1 = page.bbox[3] - y0up
    for table in tables:
        tx0, ty0, tx1, ty1 = table.bbox
        if tx0 <= x0 <= x1 <= tx1 and ty0 <= y0 <= y1 <= ty1:
            return True
    return False

# Create a function to check if the element is in any tables present in the page
def is_any_text_inside_image(image, page ,texts):
    x0, y0up, x1, y1up = image.bbox
    # Change the cordinates because the pdfminer counts from the botton to top of the page
    y0 = page.bbox[3] - y1up
    y1 = page.bbox[3] - y0up
    for text in texts:
        tx0, ty0, tx1, ty1 = text.bbox
        if x0 <= tx0 <= tx1 <= x1 and y0 <= ty0 <= ty1 <= y1:
            return True
    return False

# Function to find the table for a given element
def find_table_for_element(element, page ,tables):
    x0, y0up, x1, y1up = element.bbox
    # Change the cordinates because the pdfminer counts from the botton to top of the page
    y0 = page.bbox[3] - y1up
    y1 = page.bbox[3] - y0up
    for i, table in enumerate(tables):
        tx0, ty0, tx1, ty1 = table.bbox
        if tx0 <= x0 <= x1 <= tx1 and ty0 <= y0 <= y1 <= ty1:
            return i  # Return the index of the table
    return None  

# Create a function to crop the image elements from PDFs
def crop_image(element, pageObj):
    # Get the coordinates to crop the image from PDF
    [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
    # Crop the page using coordinates (left, bottom, right, top)
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # Save the cropped page to a new PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # Save the cropped PDF to a new file
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)

# Create a function to convert the PDF to images
def convert_to_images(input_file,):
    images = convert_from_path(input_file)
    image = images[0]
    output_file = 'PDF_image.png'
    image.save(output_file, 'PNG')

# Create a function to read text from images
def image_to_text(image_path):
    # Read the image
    img = Image.open(image_path)
    # Extract the text from the image
    text = pytesseract.image_to_string(img)
    return text

def get_paper_content(pdf_path, page_number:int = 0):
    # Create the dictionary to extract text from each image
    image_content = []
    page_content = []
    
    text_from_tables = []
    # Initialize the number of the examined tables
    table_in_page= -1
    pdf = pdfplumber.open(pdf_path)
    
    with open(pdf_path, 'rb') as pdfFileObj:
         
        pdfReaded = PyPDF2.PdfReader(pdfFileObj)
            
        # Create a boolean variable for image detection
       
        page= [el for el in extract_pages(pdf_path, page_numbers = [page_number])][0]
        # We extract the pages from the PDF
        # for pagenum, page in enumerate(pages):
        
        # Initialize the variables needed for the text extraction from the page
        pageObj = pdfReaded.pages[page_number]
        
        # Find the examined page
        page_tables = pdf.pages[page_number]
        # Find the number of tables in the page
        tables = page_tables.find_tables()
        if len(tables)!=0:
            table_in_page = 0
    
        # Extracting the tables of the page
        for table_num in range(len(tables)):
            # Extract the information of the table
            table = extract_table(pdf_path, page_number, table_num)
            # Convert the table information in structured string format
            table_string = table_converter(table)
            # Append the table string into a list
            text_from_tables.append(table_string)
    
        # Find all the elements
        page_elements = [(element.y1, element) for element in page._objs]
        # Sort all the element as they appear in the page 
        page_elements.sort(key=lambda a: a[0], reverse=True)
    
        text_elements = [component[1] for component in page_elements if isinstance(component[1], LTTextContainer)]
        # Find the elements that composed a page
        for i,component in enumerate(page_elements):
            # Extract the element of the page layout
            element = component[1]
    
            # Check the elements for tables
            if table_in_page == -1:
                pass
            else:
                if is_element_inside_any_table(element, page ,tables):
                    table_found = find_table_for_element(element,page ,tables)
                    if table_found == table_in_page and table_found != None:    
                        page_content.append(text_from_tables[table_in_page])
                        table_in_page+=1
                    # Pass this iteration because the content of this element was extracted from the tables
                    continue
    
            if not is_element_inside_any_table(element,page,tables):
    
                # Check if the element is text element
                if isinstance(element, LTTextContainer):
                    # Use the function to extract the text and format for each text element
                    (line_text, format_per_line) = text_extraction(element)
                    # Append the text of each line to the page text
                    page_content.append(line_text)
    
    
                # Check the elements for images
                if isinstance(element, LTFigure):
                    if is_any_text_inside_image(element, page, text_elements):
                        continue
                    else:
                    
                    # Crop the image from PDF
                        crop_image(element, pageObj)
                        # Convert the croped pdf to image
                        convert_to_images('cropped_image.pdf')
                        # Extract the text from image
                        image_text = image_to_text('PDF_image.png')
                        page_content.append(image_text)
                   
            
    page_content = ''.join(page_content)
    page_content = clean_text(page_content)
    return page_content

def clean_text(text):
    # Define a regular expression pattern for sentence boundaries.
    # This pattern considers '.', '!', and '?' as sentence delimiters, followed by a space or end of string.
    text = text.strip()
    text = re.sub(r'([ \t\n])\1+', r'\1', text)
    sentence_pattern = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s')
    
    # Use the pattern to split the text into sentences.
    sentences = sentence_pattern.split(text)
    
    # Remove any extra whitespace around sentences and handle hyphenated line breaks.
    cleaned_sentences = []
    for sentence in sentences:
        # Remove newline characters and hyphenated line breaks.
        
        cleaned_sentence = sentence.replace('- \n', '').replace('-\n ', '').replace('-\n', '').replace('\n', ' ').replace("\x0c", "")
        # Strip leading and trailing whitespace.
        cleaned_sentence = cleaned_sentence.strip()
        if cleaned_sentence:
            cleaned_sentences.append(cleaned_sentence)
    
    cleaned_sentences = " ".join(cleaned_sentences)
    postprocess_sentences = postprocess(cleaned_sentences)
    
    return postprocess_sentences


if __name__ == "__main__":
    # from merag.notebooks.standart_pdfreader import get_paper_content
    # filepath = "/home/nhorlava/Documents/Projects/merag/data/papers/(23) In search of an anti-elephant confronting the human inability to forget inadmissible evidence.pdf"
    filepath = "/home/nhorlava/Documents/Projects/merag/data/papers/(50) Juries and the rules of evidence.pdf"
    
    
    res = get_paper_content(filepath, page_number = 14)
    print(res)
