import pdfkit

def page_to_pdf(url):
    filename = 'notebook.pdf'
    pdfkit.from_url(url, 'notebook.pdf')

    return filename
