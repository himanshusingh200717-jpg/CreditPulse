from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def create_pdf(filename, content_lines):
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750
    for line in content_lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()

os.makedirs("dummy_docs", exist_ok=True)

# 1. Bank Statement
bank_content = [
    "--- STATE BANK OF INDIA ---",
    "Account Holder: Rahul Kumar",
    "Account Number: XXXXXXXX1234",
    "Statement Period: Jan 1, 2026 to Mar 31, 2026",
    "",
    "Date       | Description         | Amount | Type",
    "05-Jan-26  | UPI/Swiggy          |  -250  | DR",
    "10-Jan-26  | Client Payment      | +25000 | CR",
    "15-Jan-26  | UPI/Grocery         |  -500  | DR",
    "02-Feb-26  | Client Payment      | +28000 | CR",
    "10-Feb-26  | UPI/Rent            | -12000 | DR",
    "05-Mar-26  | Client Payment      | +26000 | CR",
    "",
    "Summary:",
    "Total Credits (3 months): INR 79,000",
    "Average Monthly Inflow: INR 26,333",
    "No overdrafts. Good spending discipline."
]
create_pdf("dummy_docs/bank_statement.pdf", bank_content)

# 2. Rent Agreement
rent_content = [
    "--- RENTAL AGREEMENT ---",
    "Date: 01-Jan-2025",
    "Landlord: Mr. Sharma",
    "Tenant: Rahul Kumar",
    "",
    "Property: 123 Main St, Bangalore",
    "Rent Amount: INR 12,000 per month",
    "Term: 11 months",
    "",
    "The tenant has continuously resided here for the past 24 months.",
    "Rent has been paid on time without any delays.",
    "Payment streak: 24 months."
]
create_pdf("dummy_docs/rent_agreement.pdf", rent_content)

# 3. GST Invoice
gst_content = [
    "--- TAX INVOICE ---",
    "GSTIN: 29ABCDE1234F1Z5",
    "Business Name: Rahul Tech Services",
    "Date: 15-Mar-2026",
    "",
    "Bill To: Acme Corp",
    "Description: Web Development Services",
    "Amount: INR 50,000",
    "IGST (18%): INR 9,000",
    "Total Amount: INR 59,000",
    "",
    "Annual Declared Revenue (YTD): INR 600,000",
    "Tax Compliance Status: Regular",
    "Filing Streak: 12 months on time."
]
create_pdf("dummy_docs/gst_invoice.pdf", gst_content)

print("Dummy PDFs created in dummy_docs/")
