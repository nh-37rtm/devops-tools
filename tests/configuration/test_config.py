
import os

import pydantic
import pytest
import sys
from pydantic import ValidationError
import json

#from HpiLogging import HpiLogger as logging
import logging

from configuration.config_file_loader import ConfigFileLoader
from configuration.json_config_loader import JsonConfigFileLoader
from configuration.env_config_loader import EnvConfigLoader
from configuration.env_config_file_loader import EnvConfigFileLoader
from configuration.composite_config_loader import CompositeConfigLoader
# from configuration.vault_config_loader import VaultConfigLoader, VaultConf

from models.exceptions import DevopsException

from tests.configuration.sets.test_model import TestModel, TestEnvModel
import typing as t

from dotenv import dotenv_values

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s %(message)s')


# class TUVaultConfigLoader(VaultConfigLoader):
#     def __init__(self):

#         vault_conf = VaultConf(
#                 mount_point='dummy_mp',
#                 role_id = 'dummy_id',
#                 secret_id = 'dummy_secret_id',
#                 url= 'dummy_url')

#         VaultConfigLoader.__init__(self, dict, vault_conf=vault_conf, 
#             secrets_path=['qualif/app/splunk_qualif'], auto_connect= False)
#         with open('tests/configuration/sets/vault_set.json', encoding= 'utf-8') as vault_set:
#             self._vault_cache = json.load(vault_set)
#         self._load_as_dict()


@pytest.fixture
def startup() -> None:
    logging.info('starting up test inside folder : %s ...', os.getcwd())

def test_logs() -> None:
    logging.debug('starting up test inside folder : %s ...', os.getcwd())
    logging.info('starting up test inside folder : %s ...', os.getcwd())
    logging.warning('starting up test inside folder : %s ...', os.getcwd())

def test_file_exists() -> None:
    loader = ConfigFileLoader(TestModel, 'tests/configuration/sets/test.json')
    assert loader is not None

def test_json_load() -> None:

    loader = JsonConfigFileLoader(TestModel, 'tests/configuration/sets/test.json')
    config = loader.load_config()
    logging.info(config.a_property)

def test_json_load_missing() -> None:
    with pytest.raises(ValidationError) as exception:
        loader = JsonConfigFileLoader(TestModel, 'tests/configuration/sets/test_missing.json')
        config = loader.load_config()
        logging.info(config.a_property)

def test_validation() -> None:
    with pytest.raises(ValidationError) as exception:
        validate = TestModel(a_property= 'test')
        logging.info(exception)
        assert validate is not None

def test_validation2() -> None:

    with pytest.raises(ValidationError) as exception:
        obj = { "a_property": 'test'}
        t: type = TestModel
        t = pydantic.parse_obj_as(t, obj)
        logging.info(t.a_property)


def test_env_validation():

    os.environ['DEVOPS_SPLUNK__URL'] = 'toto'
    os.environ['DEVOPS_SPLUNK__HECURL'] = 'toto2'
    env_loader = EnvConfigLoader(
        TestEnvModel,os.environ,
        'DEVOPS_')
    env_loader.load_config()
    env = dotenv_values('tests/configuration/sets/test.env')
    logging.info('env file : %s', env)


def test_env_file_validation():

    env_loader = EnvConfigFileLoader(
        TestEnvModel, 'tests/configuration/sets/test.env',
        'DEVOPS_')
    config = env_loader.load_config()
    
    logging.info('env file : %s', config)



def test_composite_loader():


    env_file_loader = EnvConfigFileLoader(
        TestEnvModel, 'tests/configuration/sets/test.env',
        'DEVOPS_SPLUNK__')
    
    toto = env_file_loader.load_as_dict()

    os.environ['DEVOPS_SPLUNK__URL'] = 'toto'
    os.environ['DEVOPS_SPLUNK__HECURL'] = 'toto2'
    os.environ['DEVOPS_SPLUNK2__ANOTHER__SUBVARIABLE'] = 'toto7'

    env_loader = EnvConfigLoader(
        TestEnvModel,os.environ,
        'DEVOPS_SPLUNK__')
    
    env_loader_2 = EnvConfigLoader(
        TestEnvModel,os.environ,
        'DEVOPS_SPLUNK2__')

    # loader = CompositeConfigLoader(t.Dict, [ env_file_loader, env_loader ])
    loader = CompositeConfigLoader(t.Dict, [env_file_loader, env_loader, env_loader_2 ])

    _dict = loader.load_as_dict()

    assert _dict['url'] == 'toto'
    assert _dict['another']['subvariable'] == 'toto7'


def _test_vault_config_loader_vr1():

    with open('tests/configuration/sets/conf_with_vault_ref1.json', encoding= 'utf-8') as t_set:

        vault_loader = TUVaultConfigLoader()
        dict_t_set = json.load(t_set)
        r_values = vault_loader.retrieve_secrets_from_vault(dict_t_set)
        assert r_values['splunk_infos']['ec_token'] == 'ec_token_value'

def _test_vault_config_loader_vr2():

    with open('tests/configuration/sets/conf_with_vault_ref2.json', encoding= 'utf-8') as t_set:
        
        vault_loader = TUVaultConfigLoader()
        dict_t_set = json.load(t_set)
        r_values = vault_loader.retrieve_secrets_from_vault(dict_t_set)
        assert r_values['splunk_infos']['ec_token'] == 'ec_token_value'


def _test_composite_loader_continue_fail():

    env_file_loader = EnvConfigFileLoader(
        TestEnvModel, 'tests/configuration/sets/test.env',
        'DEVOPS_SPLUNK__')

    bad_vault_conf = VaultConf(
            mount_point='dummy',
            role_id = 'dummy',
            secret_id = 'dummy',
            url= 'http://dummy.fr')
    
    loader_on_error = VaultConfigLoader(dict, bad_vault_conf, 'dummy', auto_connect= False)

    # loader = CompositeConfigLoader(t.Dict, [ env_file_loader, env_loader ])

    with pytest.raises(DevopsException) as exception:
        loader = CompositeConfigLoader(t.Dict, [loader_on_error, env_file_loader ], continue_on_fail_loading= False).load_config()


# def test_composite_loader_continue():
    
#     good_loader = EnvConfigFileLoader(
#         TestEnvModel, 'tests/configuration/sets/test.env',
#         'DEVOPS_SPLUNK__')

#     bad_vault_conf = VaultConf(
#             mount_point='dummy',
#             role_id = 'dummy',
#             secret_id = 'dummy',
#             url= 'http://dummy.fr')
    
#     loader_on_error = VaultConfigLoader(dict, bad_vault_conf, 'dummy', auto_connect= False)

#     # loader = CompositeConfigLoader(t.Dict, [ env_file_loader, env_loader ])
#     config = CompositeConfigLoader(t.Dict, [loader_on_error, good_loader ]).load_config()
#     assert 'url' in config
#     assert config['url'] == 'ENV_VAR'
