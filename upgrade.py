# -*- python -*-
"""This is a template upgrade script.

The purpose is both to cover the most common use-case (updating all modules)
and to provide an example of how this works.
"""

from akoto import Helper

def run(session, logger):
    """Update all modules."""
    if session.is_initialization:
        logger.warn("Usage of upgrade script for initialization detected. "
                    "You should consider customizing the present upgrade "
                    "script to add modules install commands. The present "
                    "script is at : %s (byte-compiled form)",
                    __file__)
        return
    helper = Helper(session, company_id=1, lang='fr_FR')
    if session.db_version < '1.0.0':
        helper.install_main_lang()
        helper.install_feature('default')
        helper.install_feature(
            'accounting',
            date_start='2014-01-01',
            date_stop='2014-01-01')
        helper.install_feature('sale_stock')
        helper.install_feature('pos')
        session.install_modules([
            'pos_sale_order',
            'product_subproduct',
            'pos_product_template',
            'sale_embedded_configuration',
#            'account_statement_sale_order',
            ])
        session.cr.commit()
