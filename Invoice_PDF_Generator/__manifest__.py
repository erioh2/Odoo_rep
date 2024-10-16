{
    'name': 'Invoice PDF Generator',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Generate and download custom PDF for invoices',
    'depends': ['account'],
    'external_dependencies': {
        'python': ['pdfkit', 'Jinja2'],
    },
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}