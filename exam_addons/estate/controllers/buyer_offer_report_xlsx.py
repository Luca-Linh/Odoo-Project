from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.exceptions import UserError

class BuyerOfferReportController(http.Controller):

    @http.route('/buyer_offer_report_xlsx', type='http', auth='user', csrf=False)
    def buyer_offer_report_xlsx(self, **kwargs):
        # Capture the parameters from the URL
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        buyer_id = kwargs.get('buyer_id')

        # Validate dates
        if not start_date or not end_date:
            return "Start date and end date are required."

        try:
            # Convert start_date and end_date to date objects
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."

        # Ensure the start date is not later than the end date
        if start_date_obj > end_date_obj:
            return "Start date cannot be later than end date."

        # Handle buyer selection: either one buyer or none
        if buyer_id:
            buyer_id = int(buyer_id)
            buyer = request.env['res.partner'].sudo().browse(buyer_id)
            if not buyer.exists():
                return "Invalid buyer selected."
            buyer_ids_list = [buyer_id]  # Only one buyer selected
        else:
            # If no buyer is selected, fetch all partners (no filtering)
            buyer_ids_list = [partner.id for partner in request.env['res.partner'].sudo().search([])]

        # Prepare the context for the report
        data = {
            'start_date': start_date_obj,
            'end_date': end_date_obj,
            'buyer_ids': buyer_ids_list if buyer_ids_list else None,  # If no buyer_ids, pass None
        }

        # Generate the XLSX report
        report = request.env['report.estate.buyer_offer_report_xlsx']
        file_content = report.generate_xlsx_report(data)

        # Return the file as an attachment
        filename = 'Buyer_Offer_Report.xlsx'
        response = request.make_response(file_content,
                                         headers=[('Content-Type',
                                                   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                                  ('Content-Disposition', f'attachment; filename={filename}')])

        return response
