from odoo import api, models


class ReportSalesSalespersonWise(models.AbstractModel):
    _name = 'report.report_account_receivable.report_temp'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'date': data['date'],
            'end_date': data['end_date'],
        }
        print "===================docargs",docargs
        return self.env['report'].render('report_account_receivable.report_temp', docargs)
