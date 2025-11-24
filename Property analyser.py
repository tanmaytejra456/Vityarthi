import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# --- Configuration and Data Persistence ---

# File path for saving broker data (simulating a database)
DATA_FILE = 'brokers.json'

def load_brokers():
    """Loads broker data from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Return empty list if file is corrupted or empty
                return []
    return []

def save_brokers(brokers):
    """Saves broker data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(brokers, f, indent=4)

# --- Core Business Logic Functions ---

def calculate_land_value_logic(area, price_per_sqft):
    """
    Module 1 Logic: Calculates total land value.
    Handles input validation and ensures positive values.
    """
    try:
        area_dec = Decimal(str(area))
        price_dec = Decimal(str(price_per_sqft))
        
        if area_dec <= 0 or price_dec <= 0:
            return "Error: Area and Price must be positive numbers."

        total_value = area_dec * price_dec
        
        # Rounding to 2 decimal places for financial calculations
        total_value = total_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return f"Total Land Value: ₹{total_value:,.2f}"
    except Exception:
        return "Error: Please enter valid numerical inputs."

def calculate_property_tax_logic(annual_value, tax_rate, rebate):
    """
    Module 2 Logic: Calculates net payable property tax.
    """
    try:
        annual_val_dec = Decimal(str(annual_value))
        tax_rate_dec = Decimal(str(tax_rate))
        rebate_dec = Decimal(str(rebate))

        if annual_val_dec < 0 or tax_rate_dec < 0 or rebate_dec < 0:
            return "Error: Values cannot be negative."

        # Tax = (Annual Value * Tax Rate / 100)
        gross_tax = annual_val_dec * (tax_rate_dec / 100)

        # Apply Rebate
        rebate_amount = gross_tax * (rebate_dec / 100)
        net_tax = gross_tax - rebate_amount
        
        # Rounding for presentation
        net_tax = net_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return (f"Gross Annual Tax: ₹{gross_tax:,.2f}\n"
                f"Rebate Applied ({rebate_dec}%): ₹{rebate_amount:,.2f}\n"
                f"Net Payable Tax: ₹{net_tax:,.2f}")
    except Exception:
        return "Error: Please enter valid numerical inputs."

def generate_agreement_logic(tenant_name, landlord_name, property_address, rent_amount, deposit_amount, start_date, term_months):
    """
    Module 3 Logic: Generates standardized rental agreement text.
    """
    if not all([tenant_name, landlord_name, property_address, rent_amount, deposit_amount, start_date, term_months]):
        return "Error: All fields must be filled for agreement generation."

    try:
        rent_amount_dec = Decimal(str(rent_amount))
        deposit_amount_dec = Decimal(str(deposit_amount))
        term_months_int = int(term_months)
        
        if rent_amount_dec <= 0 or deposit_amount_dec < 0 or term_months_int <= 0:
            return "Error: Financial values and term must be positive."

        agreement_date = datetime.now().strftime("%B %d, %Y")
        term_text = f"{term_months_int} months" if term_months_int != 1 else "one month"
        
        # Calculate approximate end date for documentation purposes
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        # A proper end date calculation is complex, so we'll approximate the start date + term
        # Simple approximation for Tkinter demo:
        end_date_approx = start_dt.replace(month=(start_dt.month + term_months_int) % 12 or 12, 
                                           year=start_dt.year + (start_dt.month + term_months_int - 1) // 12)
        end_date_str = end_date_approx.strftime("%B %d, %Y")

        rent_formatted = f"₹{rent_amount_dec:,.2f}"
        deposit_formatted = f"₹{deposit_amount_dec:,.2f}"

        agreement_text = f"""
RENTAL AGREEMENT

This Rental Agreement (hereinafter "Agreement") is made and entered into on this {agreement_date}, by and between:

1. LANDLORD: {landlord_name}
2. TENANT: {tenant_name}

PROPERTY DETAILS:
The property is located at:
{property_address}

TERM:
The term of this Agreement shall be for {term_text}, commencing on {start_dt.strftime("%B %d, %Y")} and approximately ending on {end_date_str}.

RENT:
The monthly rent shall be {rent_formatted}, payable in advance on the first day of each calendar month.

SECURITY DEPOSIT:
The Tenant shall pay the Landlord a Security Deposit of {deposit_formatted} upon signing this Agreement.

TERMINATION:
Either party may terminate this agreement by providing a written notice of one calendar month.

IN WITNESS WHEREOF, the parties have executed this Agreement:

_________________________                 _________________________
LANDLORD SIGNATURE                      TENANT SIGNATURE
(Name: {landlord_name})                        (Name: {tenant_name})
        """
        return agreement_text.strip()
    except ValueError:
        return "Error: Please check date format or ensure rent/deposit are valid numbers."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Tkinter Application Class ---

class RealEstateApp:
    def __init__(self, master):
        self.master = master
        master.title("Real Estate Utility Hub (Python/Tkinter)")
        master.geometry("800x650")
        master.resizable(True, True)

        # Apply modern styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', font=('Inter', 12, 'bold'))
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=6)
        style.configure('TLabel', font=('Inter', 10))

        # Main Notebook (Tabbed Interface)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- Create Tabs ---
        self.create_calculation_tab()
        self.create_broker_tab()
        self.create_agreement_tab()

        # Load broker data on startup
        self.brokers = load_brokers()
        self.update_broker_list()
        
    # --- UI Components and Handlers for Calculation Tab ---
    def create_calculation_tab(self):
        tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab, text=" Valuation & Tax ")

        # Configure grid for responsiveness
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        
        ttk.Label(tab, text="Property Calculation Module", font=('Inter', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky='w')

        # 1. Land Value Calculator
        frame_land = ttk.LabelFrame(tab, text="Land Value Calculator", padding="15")
        frame_land.grid(row=1, column=0, sticky='nsew', padx=5, pady=10)
        frame_land.columnconfigure(0, weight=1)

        ttk.Label(frame_land, text="Area (Sq. Feet):").grid(row=0, column=0, pady=5, sticky='w')
        self.land_area_entry = ttk.Entry(frame_land, font=('Inter', 10))
        self.land_area_entry.grid(row=1, column=0, sticky='ew', pady=5)

        ttk.Label(frame_land, text="Price per Sq. Ft (₹):").grid(row=2, column=0, pady=5, sticky='w')
        self.price_per_sqft_entry = ttk.Entry(frame_land, font=('Inter', 10))
        self.price_per_sqft_entry.grid(row=3, column=0, sticky='ew', pady=5)

        ttk.Button(frame_land, text="Calculate Value", command=self.handle_calculate_land_value).grid(row=4, column=0, sticky='ew', pady=(10, 5))
        
        self.land_value_result_label = ttk.Label(frame_land, text="Result: -", foreground='blue', wraplength=350)
        self.land_value_result_label.grid(row=5, column=0, pady=5, sticky='w')

        # 2. Property Tax Calculator
        frame_tax = ttk.LabelFrame(tab, text="Annual Property Tax Calculator", padding="15")
        frame_tax.grid(row=1, column=1, sticky='nsew', padx=5, pady=10)
        frame_tax.columnconfigure(0, weight=1)

        ttk.Label(frame_tax, text="Annual Property Value (₹):").grid(row=0, column=0, pady=5, sticky='w')
        self.annual_value_entry = ttk.Entry(frame_tax, font=('Inter', 10))
        self.annual_value_entry.grid(row=1, column=0, sticky='ew', pady=5)

        ttk.Label(frame_tax, text="Tax Rate (%):").grid(row=2, column=0, pady=5, sticky='w')
        self.tax_rate_entry = ttk.Entry(frame_tax, font=('Inter', 10))
        self.tax_rate_entry.insert(0, "12") # Default value
        self.tax_rate_entry.grid(row=3, column=0, sticky='ew', pady=5)

        ttk.Label(frame_tax, text="Rebate (%):").grid(row=4, column=0, pady=5, sticky='w')
        self.rebate_entry = ttk.Entry(frame_tax, font=('Inter', 10))
        self.rebate_entry.insert(0, "0") # Default value
        self.rebate_entry.grid(row=5, column=0, sticky='ew', pady=5)

        ttk.Button(frame_tax, text="Calculate Tax", command=self.handle_calculate_property_tax).grid(row=6, column=0, sticky='ew', pady=(10, 5))
        
        self.property_tax_result_label = ttk.Label(frame_tax, text="Result: -", foreground='darkgreen', wraplength=350)
        self.property_tax_result_label.grid(row=7, column=0, pady=5, sticky='w')


    def handle_calculate_land_value(self):
        area = self.land_area_entry.get()
        price_per_sqft = self.price_per_sqft_entry.get()
        result = calculate_land_value_logic(area, price_per_sqft)
        
        if result.startswith("Error"):
            self.land_value_result_label.config(text=result, foreground='red')
        else:
            self.land_value_result_label.config(text=result, foreground='blue')

    def handle_calculate_property_tax(self):
        annual_value = self.annual_value_entry.get()
        tax_rate = self.tax_rate_entry.get()
        rebate = self.rebate_entry.get()
        result = calculate_property_tax_logic(annual_value, tax_rate, rebate)

        if result.startswith("Error"):
            self.property_tax_result_label.config(text=result, foreground='red')
        else:
            self.property_tax_result_label.config(text=result, foreground='darkgreen')

    # --- UI Components and Handlers for Broker Tab (Data Persistence) ---
    def create_broker_tab(self):
        tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab, text=" Broker Information ")
        
        tab.columnconfigure(0, weight=1)

        ttk.Label(tab, text="Broker Information Management", font=('Inter', 16, 'bold')).grid(row=0, column=0, pady=(0, 15), sticky='w')
        ttk.Label(tab, text="Data is saved locally in 'brokers.json' file.", foreground='gray').grid(row=1, column=0, pady=(0, 10), sticky='w')

        # Add Broker Frame
        frame_add = ttk.LabelFrame(tab, text="Add New Broker", padding="15")
        frame_add.grid(row=2, column=0, sticky='ew', pady=10)
        frame_add.columnconfigure(1, weight=1)
        
        ttk.Label(frame_add, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.broker_name_entry = ttk.Entry(frame_add, font=('Inter', 10))
        self.broker_name_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(frame_add, text="Contact:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.broker_contact_entry = ttk.Entry(frame_add, font=('Inter', 10))
        self.broker_contact_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Button(frame_add, text="Save Broker", command=self.add_broker).grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 5))

        # View Broker Frame
        frame_list = ttk.LabelFrame(tab, text="Saved Brokers", padding="15")
        frame_list.grid(row=3, column=0, sticky='nsew', pady=10)
        tab.rowconfigure(3, weight=1) # Make broker list frame expandable
        frame_list.columnconfigure(0, weight=1)

        self.broker_list_text = tk.Text(frame_list, height=10, wrap='word', font=('Inter', 10))
        self.broker_list_text.grid(row=0, column=0, sticky='nsew', pady=5)
        
        # Scrollbar for broker list
        broker_scrollbar = ttk.Scrollbar(frame_list, command=self.broker_list_text.yview)
        broker_scrollbar.grid(row=0, column=1, sticky='ns')
        self.broker_list_text['yscrollcommand'] = broker_scrollbar.set
        
        ttk.Button(frame_list, text="Delete Selected Broker", command=self.delete_broker).grid(row=1, column=0, sticky='w', pady=(10, 5))

    def add_broker(self):
        name = self.broker_name_entry.get().strip()
        contact = self.broker_contact_entry.get().strip()

        if not name or not contact:
            messagebox.showerror("Input Error", "Please enter both name and contact information.")
            return

        new_broker = {
            'id': str(uuid.uuid4()),
            'name': name,
            'contact': contact,
            'added_on': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.brokers.append(new_broker)
        save_brokers(self.brokers)
        self.update_broker_list()
        
        self.broker_name_entry.delete(0, tk.END)
        self.broker_contact_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Broker '{name}' saved successfully.")

    def update_broker_list(self):
        self.broker_list_text.delete('1.0', tk.END)
        if not self.brokers:
            self.broker_list_text.insert(tk.END, "No brokers saved yet.")
            return

        for idx, broker in enumerate(self.brokers):
            # Display format: [Broker ID] Name - Contact
            line = f"[{idx+1}] {broker['name']} - {broker['contact']} (ID: {broker['id'][:8]})\n"
            self.broker_list_text.insert(tk.END, line)

    def delete_broker(self):
        # Get the selected line number (1-based index)
        try:
            selected_line_index = self.broker_list_text.index(tk.INSERT)
            # Extract the integer line number
            line_num = int(selected_line_index.split('.')[0])
            
            # Convert 1-based index to 0-based list index
            broker_index = line_num - 1
            
            if 0 <= broker_index < len(self.brokers):
                broker_name = self.brokers[broker_index]['name']
                del self.brokers[broker_index]
                save_brokers(self.brokers)
                self.update_broker_list()
                messagebox.showinfo("Success", f"Broker '{broker_name}' deleted.")
            else:
                messagebox.showwarning("Selection Error", "Please click on a valid line to select a broker for deletion.")
        except:
            messagebox.showwarning("Selection Error", "Please click on a valid line to select a broker for deletion.")


    # --- UI Components and Handlers for Agreement Tab ---
    def create_agreement_tab(self):
        tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab, text=" Rental Agreement ")
        
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(3, weight=1) # Make agreement output area expandable

        ttk.Label(tab, text="Rental Agreement Generator", font=('Inter', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky='w')

        # Input Frame (Left/Top)
        frame_input = ttk.LabelFrame(tab, text="Agreement Details", padding="15")
        frame_input.grid(row=1, column=0, sticky='new', padx=5, pady=10, columnspan=2)
        frame_input.columnconfigure(1, weight=1)

        labels = ["Tenant Name:", "Landlord Name:", "Property Address:", "Monthly Rent (₹):", "Security Deposit (₹):", "Start Date (YYYY-MM-DD):", "Term (Months):"]
        self.agreement_entries = {}
        for i, label_text in enumerate(labels):
            ttk.Label(frame_input, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(frame_input, font=('Inter', 10))
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            # Use specific keys for easier data retrieval
            key = label_text.split('(')[0].replace(':', '').strip().lower().replace(' ', '_')
            self.agreement_entries[key] = entry
            
        ttk.Button(frame_input, text="Generate Agreement Text", command=self.handle_generate_agreement).grid(row=len(labels), column=0, columnspan=2, sticky='ew', pady=(15, 5))

        # Output Frame (Bottom)
        frame_output = ttk.LabelFrame(tab, text="Generated Agreement Text", padding="15")
        frame_output.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=5, pady=10)
        frame_output.columnconfigure(0, weight=1)
        frame_output.rowconfigure(0, weight=1)

        self.agreement_text_area = tk.Text(frame_output, height=15, wrap='word', font=('Monospace', 10))
        self.agreement_text_area.grid(row=0, column=0, sticky='nsew', pady=5)
        
        agreement_scrollbar = ttk.Scrollbar(frame_output, command=self.agreement_text_area.yview)
        agreement_scrollbar.grid(row=0, column=1, sticky='ns')
        self.agreement_text_area['yscrollcommand'] = agreement_scrollbar.set
        
        ttk.Button(frame_output, text="Copy Text to Clipboard", command=self.copy_agreement_text).grid(row=1, column=0, sticky='w', pady=(5, 0))


    def handle_generate_agreement(self):
        data = {key: entry.get().strip() for key, entry in self.agreement_entries.items()}

        result = generate_agreement_logic(
            data.get('tenant_name'),
            data.get('landlord_name'),
            data.get('property_address'),
            data.get('monthly_rent'),
            data.get('security_deposit'),
            data.get('start_date'),
            data.get('term')
        )

        self.agreement_text_area.delete('1.0', tk.END)
        if result.startswith("Error"):
            self.agreement_text_area.insert(tk.END, result)
            messagebox.showerror("Error", result)
        else:
            self.agreement_text_area.insert(tk.END, result)
            messagebox.showinfo("Success", "Agreement text generated.")

    def copy_agreement_text(self):
        text_to_copy = self.agreement_text_area.get('1.0', tk.END).strip()
        if text_to_copy and not text_to_copy.startswith("Error"):
            self.master.clipboard_clear()
            self.master.clipboard_append(text_to_copy)
            messagebox.showinfo("Success", "Agreement text copied to clipboard.")
        else:
            messagebox.showwarning("Copy Failed", "Nothing to copy or agreement is invalid.")


if __name__ == '__main__':
    root = tk.Tk()
    app = RealEstateApp(root)
    root.mainloop()
