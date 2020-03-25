{
    'name': 'Raju',
    'version': '0.1',
    'category': 'Purchases',
    'website': 'https://www.odoo.com/page/purchase',
    'description': "Hello",
    'data': [
    	'view.xml',
        'views/templates.xml',
        'security/ir.model.access.csv'
    ],
    'depends': ['website'],
     'installable': True,
    'auto_install': False,
    'qweb': ['static/xml/dashboard.backend.xml']
}