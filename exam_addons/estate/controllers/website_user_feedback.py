from odoo import http
from odoo.http import request


class WebsiteUserFeedbackController(http.Controller):

    @http.route('/feedback_submit', type='http', auth='public', website=True, csrf=False)
    def submit_feedback(self, description=None, **kwargs):
        if description:
            request.env['website.user.feedback'].sudo().create({
                'description': description,
            })
            return request.render('estate.feedback_thanks_template')

        return request.redirect('/#feedback_form_error')