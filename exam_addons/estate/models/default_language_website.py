from odoo import models

class Website(models.Model):
    _inherit = 'website'
    _description = "Set Default Language Website"


    def _active_languages(self):
        return self.env['res.lang'].search([]).ids

    def _default_language(self):
        lang_code = "vi_VN"

        def_lang_id = self.env['res.lang']._lang_get_id(lang_code)
        active_languages = self._active_languages()

        return def_lang_id or (active_languages[82] if len(active_languages) > 82 else active_languages[0])

    # def set_default_language(self):
    #     website = self.env['website'].search([], limit=1)
    #     vi_lang = self.env['res.lang'].search([('code', '=', 'vi_VN')], limit=1)
    #     if vi_lang:
    #         website.write({'default_lang_id': vi_lang.id})