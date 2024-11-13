import io
import xlsxwriter
from odoo import models
from odoo.exceptions import UserError

class BuyerOfferReportXLSX(models.AbstractModel):
    _name = 'report.estate.buyer_offer_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, data):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        buyer_ids = data.get('buyer_ids')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        worksheet = workbook.add_worksheet('Buyer Offer Report')
        title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 12, 'border': 0})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'bg_color': '#3a90d6', 'font_color': 'white'})
        date_format = workbook.add_format({'align': 'left', 'num_format': 'yyyy-mm-dd'})
        number_format = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})

        # Set title and date range
        worksheet.merge_range('A3:I3', 'Buyer Offer Report', title_format)
        worksheet.write('C5', 'Date From', title_format)
        worksheet.write('D5', start_date.strftime('%d/%m/%Y'), date_format)
        worksheet.write('F5', 'Date To', title_format)
        worksheet.write('G5', end_date.strftime('%d/%m/%Y'), date_format)
        # Set width
        worksheet.set_column('A:A', 20)  # Buyer name
        worksheet.set_column('B:B', 25)  # Email
        worksheet.set_column('C:G', 16)  # Other columns
        worksheet.set_column('H:I', 20)  # Max/Min Price Offer

        # Headers
        headers = [
            'Buyer', 'Email', 'Property Accepted', 'Property Sold',
            'Property Cancel', 'Offer Accepted', 'Offer Rejected',
            'Max Offer Price', 'Min Offer Price'
        ]
        for col, header in enumerate(headers):
            worksheet.write(7, col, header, header_format)

        # Query and write data
        query = """
            SELECT 
                partner.name AS buyer_name,
                partner.email AS buyer_email,
                COUNT(CASE WHEN prop.state = 'offer_accepted' THEN 1 END) AS state_accepted_count,
                COUNT(CASE WHEN prop.state = 'sold' THEN 1 END) AS state_sold_count,
                COUNT(CASE WHEN prop.state = 'canceled' THEN 1 END) AS state_cancel_count,
                COUNT(CASE WHEN offer.status = 'accepted' THEN 1 END) AS offer_accepted_count,
                COUNT(CASE WHEN offer.status = 'refused' THEN 1 END) AS offer_rejected_count,
                MAX(offer.price) AS max_offer_price,
                MIN(offer.price) AS min_offer_price
            FROM 
                estate_property prop
            JOIN 
                estate_property_offer offer ON offer.property_id = prop.id
            JOIN 
                res_partner partner ON partner.id = prop.partner_id
            WHERE 
                prop.date_availability BETWEEN %s AND %s
        """
        params = [start_date, end_date]

        # Add buyer filter if buyer_ids is provided
        if buyer_ids:
            query += " AND prop.partner_id = ANY(%s)"
            params.append(buyer_ids)

        query += " GROUP BY partner.name, partner.email"

        try:
            self.env.cr.execute(query, params)
            results = self.env.cr.fetchall()
        except Exception as e:
            raise UserError(f"An error occurred while fetching data: {str(e)}")

        row = 8
        for report in results:
            worksheet.write(row, 0, report[0])  # Buyer Name
            worksheet.write(row, 1, report[1])  # Buyer Email
            worksheet.write(row, 2, report[2], number_format)  # Properties Accepted
            worksheet.write(row, 3, report[3], number_format)  # Properties Sold
            worksheet.write(row, 4, report[4], number_format)  # Properties Canceled
            worksheet.write(row, 5, report[5], number_format)  # Offers Accepted
            worksheet.write(row, 6, report[6], number_format)  # Offers Rejected
            worksheet.write(row, 7, report[7], number_format)  # Max Offer Price
            worksheet.write(row, 8, report[8], number_format)  # Min Offer Price
            row += 1

        workbook.close()
        output.seek(0)

        return output.getvalue()
