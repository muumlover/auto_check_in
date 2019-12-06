import importlib
import logging
import os
import pathlib
import sys

from aiohttp import web

from ac_api import AcApi
from setter.ac_api_setter import ac_api_set
from setter.module_setter import module_set, module_dir
from setter.resource_setter import resource_set
from setter.router_setter import router_set

sys.path.append(".")


class Module:
    name = ''
    path = ''
    lib = None
    loaded = False
    enable = False
    message = ''

    def __init__(self, name, path, lib, loaded, enable, message):
        self.name = name
        self.path = path
        self.lib = lib
        self.loaded = loaded
        self.enable = enable
        self.message = message


class BoardApplication(web.Application):
    module_all = {}
    module_loaded = {}
    module_enable = {}

    def __init__(self):
        super().__init__()
        self._api = AcApi('board', self)
        with self._api.data_manager('module') as module:
            if 'enable' not in module:
                module['enable'] = []
            if 'module_manager' not in module['enable']:
                module['enable'] += ['module_manager']
            for module_name in os.listdir(pathlib.Path('.') / module_dir):
                if module_name in self.module_all:
                    continue
                module_path = f'{module_dir}.{module_name}'
                module_lib = None
                if module_name in module['enable']:
                    module_lib = importlib.import_module(module_path)
                    if 'id' not in module_lib.plug_info:
                        del sys.modules[module_path]
                        continue
                self.module_all[module_name] = Module(
                    name=module_name,
                    path=module_path,
                    lib=module_lib,
                    loaded=False,
                    enable=module_name in module['enable'],
                    message=''
                )

    def enable_module(self, plug_name):
        with self._api.data_manager('module') as module:
            if plug_name not in module['enable']:
                module['enable'].append(plug_name)

    def disable_module(self, plug_name):
        with self._api.data_manager('module') as module:
            if plug_name in module['enable']:
                module['enable'].remove(plug_name)

    # def load_module(self, module):
    #     if module.loaded:
    #         module.message = '插件已加载'
    #         return None
    #     lib = importlib.import_module(module['module'])
    #     if 'id' not in lib.plug_info:
    #         module['message'] = '配置错误，缺少plug_info.id'
    #         self.unload_module(module)
    #         return None
    #     lib.app['board'] = self
    #     lib.app['board_api'] = AcApi(lib.plug_info['id'], lib.app)
    #     module['loaded'] = True
    #     module['lib'] = lib
    #     module['message'] = '插件加载成功'
    #     self.module_loaded[module['name']] = module
    #     return lib

    # def reload_module(self, module):
    #     if not module['loaded']:
    #         return
    #     lib = importlib.reload(module['module'])
    #     lib.app['board'] = self
    #     lib.app['board_api'] = AcApi(lib.plug_info['id'], lib.app)
    #     module['loaded'] = True
    #     module['lib'] = lib
    #     return lib

    # def unload_module(self, module):
    #     del sys.modules[module['module']]
    #     module['loaded'] = False
    #     module['lib'] = None
    #     self.module_loaded.pop(module['name'])

    pass


app = BoardApplication()

resource_set(app)
router_set(app)
ac_api_set(app)
module_set(app)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)s: %(asctime)s [%(pathname)s:%(lineno)d] %(message)s',
        level=logging.INFO
    )
    web.run_app(app)
