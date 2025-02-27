from nearai.agents.environment import Environment
from fpdf import FPDF  
from datetime import datetime
import json
import os
import requests
from pathlib import Path

class FileStorage:
    def __init__(self):
        self.storage_dir = Path("legal_documents")
        self.storage_dir.mkdir(exist_ok=True)
        
        self.cloud_storage_key = os.getenv("CLOUD_STORAGE_KEY")
        self.cloud_storage_url = os.getenv("CLOUD_STORAGE_URL")

    def save_local(self, filename, content):
        """Save file to local storage"""
        file_path = self.storage_dir / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        return str(file_path)

    def upload_to_cloud(self, file_path):
        """Upload file to cloud storage (example using generic REST API)"""
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                headers = {'Authorization': f'Bearer {self.cloud_storage_key}'}
                
                response = requests.post(
                    self.cloud_storage_url,
                    files=files,
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json().get('url')
                else:
                    raise Exception(f"Upload failed: {response.status_code}")
        except Exception as e:
            print(f"Cloud upload failed: {str(e)}")
            return None

    def get_sharing_link(self, file_path):
        """Generate sharing link for the file"""
        # Try cloud upload first
        if self.cloud_storage_key and self.cloud_storage_url:
            cloud_url = self.upload_to_cloud(file_path)
            if cloud_url:
                return cloud_url
        
        # Fallback to local file path
        return f"file://{file_path}"

class ContractPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'RESIDENTIAL RENTAL AGREEMENT', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_rental_agreement(details, storage):
    pdf = ContractPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    pdf.cell(0, 10, f'This agreement made on {details.get("date", datetime.now().strftime("%B %d, %Y"))}', 0, 1)
    pdf.cell(0, 10, 'BETWEEN:', 0, 1)
    pdf.cell(0, 10, f'Landlord: {details.get("landlord_name", "")}', 0, 1)
    pdf.cell(0, 10, f'Tenant(s): {details.get("tenant_names", "")}', 0, 1)
    
    pdf.ln(10)
    pdf.cell(0, 10, 'PROPERTY:', 0, 1)
    pdf.multi_cell(0, 10, f'Address: {details.get("property_address", "")}')
    
    pdf.ln(10)
    pdf.cell(0, 10, 'TERMS AND CONDITIONS:', 0, 1)
    pdf.multi_cell(0, 10, f'1. Term: {details.get("lease_term", "")}')
    pdf.multi_cell(0, 10, f'2. Rent: ${details.get("monthly_rent", "")} per month')
    pdf.multi_cell(0, 10, f'3. Security Deposit: ${details.get("security_deposit", "")}')
    
    filename = f'rental_agreement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    file_path = storage.save_local(filename, pdf.output(dest='S').encode('latin-1'))
    
    share_link = storage.get_sharing_link(file_path)
    
    return filename, share_link

def run(env: Environment):
    storage = FileStorage()
    
    prompt = {
        "role": "system",
        "content": """I am a legal services assistant that can generate rental agreements and other legal documents.
        I can create:
        - Residential Rental Agreements (PDF format)
        - Commercial Lease Agreements
        - Room Rental Agreements
        - Sublease Agreements
        
        IMPORTANT DISCLAIMER: I am an AI assistant and not a licensed attorney. 
        All generated documents:
        - Are for informational purposes only
        - Should be reviewed by a qualified legal professional
        - Must comply with local laws and regulations
        
        To generate a rental agreement, please provide the following information:
        - Landlord name
        - Tenant name(s)
        - Property address
        - Monthly rent amount
        - Lease term
        - Security deposit amount"""
    }

    messages = env.list_messages()
    user_query = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), "")

    if "generate rental agreement" in user_query.lower():
        try:
            details_prompt = """Please extract the following details from the user's message in JSON format:
            {
                "landlord_name": "",
                "tenant_names": "",
                "property_address": "",
                "monthly_rent": "",
                "lease_term": "",
                "security_deposit": "",
                "date": ""
            }"""
            
            details_response = env.completion([{"role": "system", "content": details_prompt}, 
                                            {"role": "user", "content": user_query}])
            
            contract_details = json.loads(details_response)
            
            filename, share_link = generate_rental_agreement(contract_details, storage)
            
            response = f"""✅ Rental Agreement Generated!

📄 Your document has been created: {filename}
🔗 Access your document here: {share_link}

⚠️ IMPORTANT REMINDERS:
1. Review the document carefully
2. Consult with a legal professional before signing
3. Ensure compliance with local laws
4. Keep copies for all parties
5. Document will be available for 7 days

Need any modifications to the agreement?"""

        except Exception as e:
            response = f"""⚠️ I couldn't generate the agreement: {str(e)}
            
Please provide the following information:
1. Landlord's full name
2. Tenant's full name(s)
3. Complete property address
4. Monthly rent amount
5. Lease term (e.g., 12 months)
6. Security deposit amount

Example: "Generate rental agreement for landlord John Doe, tenant Jane Smith, 
property at 123 Main St, rent $1500/month, 12-month lease, $2000 security deposit" """
    
    else:
        response = """Welcome! I can help you generate a rental agreement in PDF format.

To get started, please say "Generate rental agreement" and provide:
- Landlord name
- Tenant name(s)
- Property address
- Monthly rent amount
- Lease term
- Security deposit amount

Example: "Generate rental agreement for landlord John Doe, tenant Jane Smith, 
property at 123 Main St, rent $1500/month, 12-month lease, $2000 security deposit" """

    env.add_reply(response)
    env.request_user_input()

run(env) 