from fpdf import FPDF  
from datetime import datetime
from pathlib import Path

class FileStorage:
    def __init__(self):
        self.storage_dir = Path("legal_documents")
        self.storage_dir.mkdir(exist_ok=True)

    def save_local(self, filename, content):
        """Save file to local storage"""
        file_path = self.storage_dir / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        return str(file_path)

class ContractPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'RESIDENTIAL RENTAL AGREEMENT', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_rental_agreement(details):
    storage = FileStorage()
    pdf = ContractPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    pdf.cell(0, 10, f'This agreement made on {datetime.now().strftime("%B %d, %Y")}', 0, 1)
    pdf.cell(0, 10, 'BETWEEN:', 0, 1)
    pdf.cell(0, 10, f'Landlord: {details["landlord_name"]}', 0, 1)
    pdf.cell(0, 10, f'Tenant(s): {details["tenant_names"]}', 0, 1)
    
    pdf.ln(10)
    pdf.cell(0, 10, 'PROPERTY:', 0, 1)
    pdf.multi_cell(0, 10, f'Address: {details["property_address"]}')
    
    pdf.ln(10)
    pdf.cell(0, 10, 'TERMS AND CONDITIONS:', 0, 1)
    pdf.multi_cell(0, 10, f'1. Term: {details["lease_term"]}')
    pdf.multi_cell(0, 10, f'2. Rent: ${details["monthly_rent"]} per month')
    pdf.multi_cell(0, 10, f'3. Security Deposit: ${details["security_deposit"]}')
    
    filename = f'rental_agreement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    file_path = storage.save_local(filename, pdf.output(dest='S').encode('latin-1'))
    
    return filename, file_path

if __name__ == "__main__":
    # Example usage
    contract_details = {
        "landlord_name": "John Doe",
        "tenant_names": "Jane Smith",
        "property_address": "123 Main St",
        "monthly_rent": "1500",
        "lease_term": "12 months",
        "security_deposit": "2000"
    }
    
    filename, file_path = generate_rental_agreement(contract_details)
    print(f"Agreement generated: {file_path}") 