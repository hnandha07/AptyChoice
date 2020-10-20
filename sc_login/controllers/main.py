import ast
from odoo.addons.web.controllers.main import Home
import pytz
import datetime
import logging

import odoo
import odoo.modules.registry
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)


#----------------------------------------------------------
# Odoo Web web Controllers
#----------------------------------------------------------
class LoginHome(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        param_obj = request.env['ir.config_parameter'].sudo()
        request.params['disable_footer'] = ast.literal_eval(param_obj.get_param('login_form_disable_footer')) or False
        request.params['disable_database_manager'] = ast.literal_eval(
            param_obj.get_param('login_form_disable_database_manager')) or False

        change_background = ast.literal_eval(param_obj.get_param('login_form_change_background_by_hour')) or False
        if change_background:
            config_login_timezone = param_obj.get_param('login_form_change_background_timezone')
            tz = config_login_timezone and pytz.timezone(config_login_timezone) or pytz.utc
            current_hour = datetime.datetime.now(tz=tz).hour or 10

            if (current_hour >= 0 and current_hour < 3) or (current_hour >= 18 and current_hour < 24):  # Night
                request.params['background_src'] = param_obj.get_param('login_form_background_night') or ''
            elif current_hour >= 3 and current_hour < 7:  # Dawn
                request.params['background_src'] = param_obj.get_param('login_form_background_dawn') or ''
            elif current_hour >= 7 and current_hour < 16:  # Day
                request.params['background_src'] = param_obj.get_param('login_form_background_day') or ''
            else:  # Dusk
                request.params['background_src'] = param_obj.get_param('login_form_background_dusk') or ''
        else:
            request.params['background_src'] = param_obj.get_param('login_form_background_default') or ''
        return super(LoginHome, self).web_login(redirect, **kw)
