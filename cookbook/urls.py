from werkzeug.routing import Rule

from cookbook import cookbook
from . import views


cookbook.add_url_rule('/', view_func=views.home_page)
cookbook.add_url_rule('/<username>/', view_func=views.profile_page)
cookbook.add_url_rule('/messages/<username>/', view_func=views.message_page)

cookbook.add_url_rule('/new_messages/<username>/', view_func=views.new_messages)
cookbook.add_url_rule('/view_messsage/', view_func=views.view_message, methods=['POST'])
cookbook.add_url_rule('/add_messaage/', view_func=views.add_message, methods=['POST'])

cookbook.add_url_rule('/recipes/', view_func=views.recipes_page)
cookbook.add_url_rule('/contact/', view_func=views.contact_page)
cookbook.add_url_rule('/initdb/', view_func=views.initdb)
cookbook.add_url_rule('/uploads/<filename>/', view_func=views.uploaded_file, methods=['GET'], endpoint='uploads')
cookbook.add_url_rule('/upload/', view_func=views.upload_profile_image, methods=['GET', 'POST'])
cookbook.add_url_rule('/login/', view_func=views.login, methods=['POST'])
cookbook.add_url_rule('/logout/', view_func=views.logout)
