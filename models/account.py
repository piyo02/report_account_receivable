from odoo import api, fields, models
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class ReportAccountReceivable(models.TransientModel):
    _name = "report.account.receivable"

    date = fields.Date(string='Tanggal', required=True, default=datetime.today())
    overdue_check = fields.Boolean(string='Jatuh Tempo')
    overdue_day = fields.Integer(default='0', string='Hari Jatuh Tempo')
    city_ids = fields.Many2many("vit.kota", string='Kota', required=False)


    @api.multi
    def print_report_account_receivable(self):
        groupby_dict = {}

        if len(self.city_ids) == 0:
            self.city_ids = self.env['vit.kota'].search([])

        for city in self.city_ids:
            partners = self.env['res.partner'].search([('kota_id.name', '=', city.name)])
                        
            partner_detail = []
            for partner in partners:
                end_date = self.date

                if self.overdue_check:
                    _date = fields.Date.from_string(self.date)
                    if isinstance(_date, basestring):
                        _date = fields.Date.from_string(_date)
                    
                    end_date = date(month=_date.month, year=_date.year, day=_date.day)+timedelta(days=self.overdue_day)
                    # end_date = (datetime.strptime(self.date, '%Y-%m-%d')+relativedelta(days =+ self.overdue_day))
                    invoices = self.env['account.invoice'].search([ 
                        ('date_due', '>=', self.date), 
                        ('date_due', '<=', end_date), 
                        ('state', '=', 'open'), 
                        ('type', '=', 'out_invoice'), 
                        ('partner_id.name', '=', partner.display_name) 
                    ],
                    order="date_invoice asc")

                else:
                    invoices = self.env['account.invoice'].search([ 
                        ('date_invoice', '<=', self.date), 
                        ('state', '=', 'open'), 
                        ('type', '=', 'out_invoice'), 
                        ('partner_id.name', '=', partner.display_name) 
                    ],
                    order="date_invoice asc")

                partner_temp = []
                partner_invoices = []
                partner_temp.append(partner.display_name) #0
                partner_temp.append(partner.credit_limit) #1
                for invoice in invoices:
                    partner_invoice = []
                    partner_invoice.append(invoice.date_invoice) #0
                    partner_invoice.append(invoice.number) #1
                    partner_invoice.append(invoice.date_due) #2
                    partner_invoice.append(invoice.origin) #3
                    partner_invoice.append(invoice.amount_total_signed ) #4
                    partner_invoice.append(invoice.residual_signed ) #5
                    partner_invoice.append(invoice.user_id.name) #6
                    partner_invoices.append(partner_invoice)

                partner_temp.append(partner_invoices)
                partner_temp.append(partner.risk_total) #3
                
                partner_temp.append(partner.risk_invoice_open) #4
                if len(partner_invoices) > 0:
                    partner_detail.append(partner_temp) #2

            if len(partner_detail) > 0:
                groupby_dict[city.name] = partner_detail

        datas = {
            'ids': self.ids,
            'model': 'report.account.receivable',
            'form': groupby_dict,
            'date': self.date,
            'end_date': str(end_date),
        }
        return self.env['report'].get_action(self,'report_account_receivable.report_temp', data=datas)

    
    def _prepare_report_account_receivable(self):
        self.ensure_one()
        return {
            'ids': self.ids,
            'model': 'report.account.receivable',
            'data': groupby_dict,
            'date': self.date,
            'end_date': str(end_date),
        }

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env['report_trial_balance_qweb']
        report = model.create(self._prepare_report_account_receivable())
        return report.print_report(report_type)
