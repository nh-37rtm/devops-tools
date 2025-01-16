from .config_file_loader import ConfigLoader
from typing import TypeVar, Type, Tuple
from devops_tools.logger import HpiLogger
from queue import SimpleQueue
from devops_tools.models.exceptions import DevopsException
# from configuration.vault_config_loader import VaultConfigLoader

T = TypeVar('T')
NoneType = type(None)

class CompositeConfigLoader(ConfigLoader[T]):
    """
        Allow to merge multiple configuration loader to one
    """

    _chained_config_loaders: list[ConfigLoader] = None
    _sources_index: list[str] = None
    _continue_on_fail_loading: bool = None


    def __init__(self, mode_type: Type[T], chained_config_loaders: list[ConfigLoader],
                 continue_on_fail_loading: bool = True):
        """
            Contructor

            mode_type:Type[T] 
                Model type to validate with
            chained_config_loaders:list[ConfigLoader]  
                List of config loader to use in order for override
        """
        ConfigLoader.__init__(self, mode_type)
        self._chained_config_loaders = chained_config_loaders
        self._sources_index = list(),
        self._continue_on_fail_loading = continue_on_fail_loading

    def _load_as_dict(self):

        # this merge elements in order for all config loaders specified
        for loader in self._chained_config_loaders:

            try:
                partial_config = loader.load_as_dict()
            except Exception as exception:
                if self._continue_on_fail_loading:
                    HpiLogger.exception(exception, exc_info=True)
                    continue
                else:
                    raise DevopsException(f'Error on initializing config loader {loader.__class__}', ) from exception

            HpiLogger.info('composing configuration with %s loader ...', type(loader).__name__)

            class QueueElementContext():

                source: object
                target: object = None
                # target_ref: object = None
                key: str = None
                full_key_path = list = None

                def __init__(self, source, target, key,
                              # target_ref, 
                              full_key_path):
                    self.source = source
                    self.target = target
                    self.key = key
                    # self.target_ref = target_ref
                    self.full_key_path = full_key_path
                    

            queue: SimpleQueue[QueueElementContext] = SimpleQueue()

            queue.put(QueueElementContext(partial_config, 
                                          self._data_as_dict,
                                          None,
                                          list()))

            while not queue.empty():

                ec  = queue.get()

                if isinstance(ec.source, dict):
                    for key, value in ec.source.items():

                        path = ec.full_key_path.copy()
                        path.append(key)

                        if key in ec.target:

                            HpiLogger.warning(
                                'merge/override key : "%s" with the value from "%s" loader source!',
                                '.'.join(path),
                                type(loader).__name__)

                            if isinstance(value, dict):
                                queue.put(
                                    QueueElementContext(
                                        value,
                                        ec.target[key],
                                        key,
                                        path
                                    ))
                                continue

                        ec.target[key] = value
                        
                else:
                    ec.target = ec.source

            HpiLogger.debug('current composition result is : %s ', self._data_as_dict)

        # if self._vault_conf_loader is not None:
        #     try:
        #         HpiLogger.info('vault config loader exists, resolving vault placeholders ...')
        #         self._data_as_dict = self._vault_conf_loader.retrieve_secrets_from_vault(self._data_as_dict)
        #     except Exception as exception:
        #         HpiLogger.exception(exception, exc_info=True)

    

