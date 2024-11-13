from odoo import http
from odoo.http import request
from datetime import datetime

class BuyerOfferReportController(http.Controller):

    @http.route('/buyer_offer_report_xlsx', type='http', auth='user', csrf=False)
    def buyer_offer_report_xlsx(self, **kwargs):
        # Capture the parameters from the URL
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        buyer_ids = kwargs.get('buyer_ids')

        # Validate dates
        if not start_date or not end_date:
            return "Start date and end date are required."

        # Convert start_date and end_date to date objects
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."

        # Convert buyer_ids to a list of integers if provided
        if buyer_ids:
            buyer_ids = [int(buyer_id) for buyer_id in buyer_ids.split(',')]
        else:
            buyer_ids = None

        # Prepare the context for the report
        data = {
            'start_date': start_date_obj,
            'end_date': end_date_obj,
            'buyer_ids': buyer_ids,  # Pass list of IDs or None if no buyers selected
        }

        # Generate the XLSX report
        report = request.env['report.estate.buyer_offer_report_xlsx']
        file_content = report.generate_xlsx_report(data)

        # Return the file as an attachment
        filename = 'Buyer_Offer_Report.xlsx'
        response = request.make_response(
            file_content,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={filename}')
            ]
        )

        return response
