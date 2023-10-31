import pybars

from app.server.utils import file_utils


async def get_template(file_path, **kwargs):
    template_string = await file_utils.read_file(file_path)
    compiler = pybars.Compiler()
    template = compiler.compile(str(template_string, 'utf-8'))
    return template(kwargs)


async def otp(**kwargs):
    template_string = await file_utils.read_file('app/server/templates/admin_otp.html')
    compiler = pybars.Compiler()
    template = compiler.compile(str(template_string, 'utf-8'))
    return template(kwargs)
