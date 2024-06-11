import numpy as np
import pandas as pd
import pickle


with open(r'C:\Users\Dell\Desktop\invoices_new.pkl', 'rb') as file:
    data = pickle.load(file)

with open(r'C:\Users\Dell\Desktop\expired_invoices.txt', 'r') as file:
    expired = file.read()


print(data)
print(type(data))

print(expired)
print(type(expired))


class DataExtractor:

    def __init__(self, invoices_file, expired_inv_file):   # constructor for invoices
        self.invoices_file = invoices_file
        self.expired_inv_file = expired_inv_file
        self.invoices_data = None
        self.expired_ids = None


    # loading the invoices data and the expired invoices' IDs
    def load_data(self):
        with open(self.invoices_file, 'rb') as file:
            self.invoices_data = pickle.load(file)

        with open(self.expired_inv_file, 'r') as file:
            self.expired_ids = file.read()


    # checking if the quantity is int, converting if otherwise (str)
    def convert_quantity(self, quantity):
        if isinstance(quantity, int):
            return quantity
        if quantity.isdigit():
            return int(quantity)
        word_to_num = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
            'eighteen': 18, 'nineteen': 19, 'twenty': 20
        }
        return word_to_num.get(quantity.lower(), 0)

    def transform_data(self, output_file):
        flat_data = []
        invoice_type = {0: 'Material', 1: 'Equipment', 2: 'Service', 3: 'Other'}

        for invoice in self.invoices_data:
            invoice_id = invoice['id']
            # created_on = pd.to_datetime(invoice['created_on'])

            try:
                created_on = pd.to_datetime(invoice['created_on'])
            except ValueError as e:
                print(f"Skipping invoice {invoice_id} due to invalid date format: {e}")
                continue  # Skip this invoice and move to the next one

            if 'items' in invoice:
                items = invoice['items']
                invoice_total = sum(item['item']['unit_price'] * self.convert_quantity(item['quantity']) for item in items)
            else:
                invoice_total = 0  # setting some default value

            is_expired = str(invoice_id) in self.expired_ids

            if 'items' in invoice:
                for item in invoice['items']:
                    invoiceitem_id = item['item']['id']
                    invoiceitem_name = item['item']['name']
                    item_type = invoice_type.get(item['item']['type'], 'Other')
                    unit_price = item['item']['unit_price']
                    quantity = self.convert_quantity(item['quantity'])
                    total_price = unit_price * quantity
                    percentage_in_invoice = total_price / invoice_total if invoice_total != 0 else 0.0


                    flat_data.append({
                    'invoice_id': invoice_id,
                    'created_on': created_on,
                    'invoiceitem_id': invoiceitem_id,
                    'invoiceitem_name': invoiceitem_name,
                    'type': item_type,
                    'unit_price': unit_price,
                    'total_price': total_price,
                    'percentage_in_invoice': percentage_in_invoice,
                    'is_expired': is_expired
                    })

        df = pd.DataFrame(flat_data)
        df.to_csv(output_file, index=False)  # Export DataFrame to CSV file


data_extractor = DataExtractor(r'C:\Users\Dell\Desktop\invoices_new.pkl',
                               r'C:\Users\Dell\Desktop\expired_invoices.txt')
data_extractor.load_data()
# flat_data_df = data_extractor.transform_data()
# print(flat_data_df.head())
data_extractor.transform_data('invoices_processed.csv')
