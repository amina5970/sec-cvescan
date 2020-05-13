import cvescan.constants as const
from cvescan.errors import DistribIDError, PkgCountError
from cvescan.sysinfo import SysInfo
import io
import lsb_release
import logging
import os
import pytest
import subprocess
import sys

class MockSubprocess:
    def __init__(self):
        self.out = """Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
||/ Name                                            Version                                     Architecture Description
+++-===============================================-===========================================-============-===============================================================================
ii  2to3                                            3.7.5-1                                     all          2to3 binary using python3
ii  accountsservice                                 0.6.55-0ubuntu10                            amd64        query and manipulate user account information
ii  accountwizard                                   4:19.04.3-0ubuntu1                          amd64        wizard for KDE PIM applications account setup
ii  acl                                             2.2.53-4                                    amd64        access control list - utilities
ii  acpi-support                                    0.143                                       amd64        scripts for handling many ACPI events
rc  acpid                                           1:2.0.31-1ubuntu2                           amd64        Advanced Configuration and Power Interface event daemon
ii  adduser                                         3.118ubuntu1                                all          add and remove users and groups
ii  adwaita-icon-theme                              3.34.0-1ubuntu1                             all          default icon theme of GNOME (small subset)
ii  afl                                             2.52b-5ubuntu1                              amd64        instrumentation-driven fuzzer for binary formats
"""
        self.error = None
        self.returncode = 0

    def communicate(self):
        return (self.out, self.error)

class MockResponses:
    def __init__(self):
        self.sys_argv = list("cvescan")
        self.os_path_dirname = "/test"
        self.os_path_abspath = "/test"
        self.environ_snap_user_common = None
        self.get_distro_information_raises = False
        self.get_distro_information = {"ID": "Ubuntu", "CODENAME": "trusty"}
        self.lsb_release_file = "tests/assets/lsb-release"
        self.dpkg_popen = MockSubprocess()

def apply_mock_responses(monkeypatch, mock_responses):
    monkeypatch.setattr(sys, "argv",  mock_responses.sys_argv)
    monkeypatch.setattr(os.path, "dirname", lambda x: mock_responses.os_path_dirname)
    monkeypatch.setattr(os.path, "abspath", lambda x: mock_responses.os_path_abspath)
    if mock_responses.environ_snap_user_common == None:
        monkeypatch.delenv("SNAP_USER_COMMON", raising=False)
    else:
        monkeypatch.setenv("SNAP_USER_COMMON", mock_responses.environ_snap_user_common)

    if mock_responses.get_distro_information_raises == True:
        monkeypatch.setattr(lsb_release, "get_distro_information", raise_mock_exception)
    else:
        monkeypatch.setattr(lsb_release, "get_distro_information", lambda: mock_responses.get_distro_information)

    monkeypatch.setattr(const, "LSB_RELEASE_FILE", mock_responses.lsb_release_file)
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: mock_responses.dpkg_popen)

def raise_mock_exception():
    raise Exception("Mock Exception")


@pytest.fixture
def null_logger():
    logger = logging.getLogger("cvescan.null")
    if not logger.hasHandlers():
        logger.addHandler(logging.NullHandler())

    return logger

def test_scriptdir(monkeypatch, null_logger):
    mock_responses = MockResponses()
    apply_mock_responses(monkeypatch, mock_responses)

    sysinfo = SysInfo(null_logger)
    assert sysinfo.scriptdir == "/test"

def test_xslt_file(monkeypatch, null_logger):
    mock_responses = MockResponses()
    apply_mock_responses(monkeypatch, mock_responses)

    sysinfo = SysInfo(null_logger)
    assert sysinfo.xslt_file == "/test/text.xsl"

def test_is_snap_false(monkeypatch, null_logger):
    mock_responses = MockResponses()
    apply_mock_responses(monkeypatch, mock_responses)

    sysinfo = SysInfo(null_logger)
    assert not sysinfo.is_snap
    assert sysinfo.snap_user_common is None

def test_is_snap_true(monkeypatch, null_logger):
    mock_responses = MockResponses()
    mock_responses.environ_snap_user_common = "/home/test/snap"
    apply_mock_responses(monkeypatch, mock_responses)

    sysinfo = SysInfo(null_logger)
    assert sysinfo.is_snap
    assert sysinfo.snap_user_common == "/home/test/snap"

def test_get_codename_lsb_module(monkeypatch, null_logger):
    mock_responses = MockResponses()
    apply_mock_responses(monkeypatch, mock_responses)

    sysinfo = SysInfo(null_logger)
    assert sysinfo.distrib_codename == "trusty"

def test_get_codename_lsb_module_empty(monkeypatch, null_logger):
    mock_responses = MockResponses()
    mock_responses.get_distro_information = {}
    apply_mock_responses(monkeypatch, mock_responses)

    with pytest.raises(DistribIDError) as di:
        sysinfo = SysInfo(null_logger)

    assert "UNKNOWN" in str(di)

def test_get_codename_lsb_module_other(monkeypatch, null_logger):
    mock_responses = MockResponses()
    mock_responses.get_distro_information = {"ID": "something_else"}
    apply_mock_responses(monkeypatch, mock_responses)

    with pytest.raises(DistribIDError) as di:
        sysinfo = SysInfo(null_logger)

    assert "something_else" in str(di)

def test_get_codename_from_file(monkeypatch, null_logger):
    mock_responses = MockResponses()
    mock_responses.get_distro_information_raises = True
    apply_mock_responses(monkeypatch, mock_responses)

    sysinfo = SysInfo(null_logger)
    assert sysinfo.distrib_codename == "trusty"

def test_get_codename_from_not_ubuntu(monkeypatch, null_logger):
    mock_responses = MockResponses()
    mock_responses.get_distro_information_raises = True
    #mock_responses.lsb_file_contents = "DISTRIB_ID=something_else\nDISTRIB_CODENAME=trusty"
    mock_responses.lsb_release_file = "tests/assets/lsb-release-not-ubuntu"
    apply_mock_responses(monkeypatch, mock_responses)

    with pytest.raises(DistribIDError) as di:
        sysinfo = SysInfo(null_logger)

    assert "not-ubuntu" in str(di)

def test_package_count(monkeypatch, null_logger):
    mock_responses = MockResponses()
    apply_mock_responses(monkeypatch, mock_responses)

    sysinfo = SysInfo(null_logger)
    assert sysinfo.package_count == 8

def test_package_count_errir(monkeypatch, null_logger):
    mock_responses = MockResponses()
    ms = MockSubprocess()
    ms.returncode = 1
    mock_responses.dpkg_popen = ms
    apply_mock_responses(monkeypatch, mock_responses)

    with pytest.raises(PkgCountError) as pce:
        sysinfo = SysInfo(null_logger)