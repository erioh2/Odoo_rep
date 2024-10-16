import base64
from odoo import models, fields, api
from odoo.exceptions import UserError
import pdfkit
from jinja2 import Template

class AccountMove(models.Model):
    _inherit = 'account.move'

    pdf_generated = fields.Boolean(string="PDF Generated", default=False)
    pdf_file = fields.Binary(string="Generated PDF", attachment=True)
    pdf_filename = fields.Char(string="PDF Filename")

    def action_generate_pdf(self):
        self.ensure_one()
        if self.state != 'posted':
            raise UserError("La factura debe estar confirmada antes de generar el PDF.")

        datos = {
            "nombre_cliente": self.partner_id.name or "N/A",
            "direccion": self.partner_id.contact_address or "N/A",  
            "numero_factura": self.name or "N/A",
            "fecha": self.invoice_date.strftime("%d/%m/%Y") if self.invoice_date else "N/A",
            "total": f"{self.amount_total:.2f} {self.currency_id.symbol}",
            "termino_pago": self.invoice_payment_term_id.name or "N/A",
            "lineas_factura": self.invoice_line_ids,
        }

        pdf_content = self.generar_recibo(datos)
        
        self.pdf_file = base64.b64encode(pdf_content)
        self.pdf_filename = f"invoice_{self.name.replace('/', '_')}.pdf"
        self.pdf_generated = True

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/pdf_file/{self.pdf_filename}?download=true',
            'target': 'self',
        }

    def generar_recibo(self, datos):
        plantilla_html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Serif&display=swap" rel="stylesheet">
            <style>
                body {
                    font-family: 'Noto Serif', serif;
                    margin: 0;
                    padding: 20px;
                }
                h1 {
                    font-weight: bold;
                    font-size: 24px;
                }
                p {
                    margin: 5px 0;
                    font-size: 16px;
                }
                .details {
                    border: 1px solid #ccc;
                    padding: 10px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Factura</h1>
            <div class="details">
                <p><strong>Nombre del Cliente:</strong> {{ nombre_cliente }}</p>
                <p><strong>Dirección:</strong> {{ direccion }}</p>
                <p><strong>Número de Factura:</strong> {{ numero_factura }}</p>
                <p><strong>Fecha:</strong> {{ fecha }}</p>
                <p><strong>Total:</strong> {{ total }}</p>
                <p><strong>Término de Pago:</strong> {{ termino_pago }}</p>
            </div>
            <h2>Detalles de la Factura:</h2>
            <ul>
                {% for line in lineas_factura %}
                    <li>{{ line.product_id.name }} - {{ line.quantity }} x {{ line.price_unit }} {{ line.currency_id.symbol }} = {{ line.price_subtotal }}</li>
                {% endfor %}
            </ul>
        </body>
        </html>
        """

        template = Template(plantilla_html)

        html_renderizado = template.render(
            nombre_cliente=datos['nombre_cliente'],
            direccion=datos['direccion'],
            numero_factura=datos['numero_factura'],
            fecha=datos['fecha'],
            total=datos['total'],
            termino_pago=datos['termino_pago'],
            lineas_factura=datos['lineas_factura'],
        )

        opciones = {
            'page-size': 'A4',
            'encoding': 'UTF-8',
        }

        pdf_content = pdfkit.from_string(html_renderizado, False, options=opciones)
        return pdf_content

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def _get_pdf_report(self):
        return self.env.ref('account.account_invoices')
