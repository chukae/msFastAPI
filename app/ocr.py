import pathlib
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
BASE_DIR = pathlib.Path(__file__).parent

IMAGE_DIR = BASE_DIR /"images"

img_path= IMAGE_DIR/"2021-11-22.png"
img = Image.open(img_path)

preds = pytesseract.image_to_string(img)
predictions = [x for x in preds.split("/n")]
print(predictions)
print(BASE_DIR)