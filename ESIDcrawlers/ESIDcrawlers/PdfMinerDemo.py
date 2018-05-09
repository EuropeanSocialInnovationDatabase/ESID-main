import requests
import pdfminer
from cStringIO import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


def pdfparser(data):

    fp = file(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data = retstr.getvalue()

    return data

r = requests.get("https://s3.amazonaws.com/pushbullet-uploads/ujzNDwQrsR2-epZ1TmlDHWwQCLfMTW4qwBDppQ8XuX5V/Project%20Summary.pdf")
pdf = r.content
output = file("temp.pdf",'wb')
output.write(pdf)
output.close()
text = pdfparser("temp.pdf")
print text
