import re

from pygitguardian.iac_models import (
    IaCDiffScanEntities,
    IaCDiffScanResult,
    IaCFileResult,
    IaCVulnerability,
)

from ggshield.verticals.iac.collection.iac_diff_scan_collection import (
    IaCDiffScanCollection,
)
from ggshield.verticals.iac.output.iac_text_output_handler import IaCTextOutputHandler


POLICY_DOC_URL = "https://docs.gitguardian.com/iac-scanning/policies/GG_IAC_0021"


def _generate_iac_file_result() -> IaCFileResult:
    return IaCFileResult(
        filename="FILENAME.tf",
        incidents=[
            IaCVulnerability(
                policy="Unrestricted ingress traffic leave assets exposed to remote attacks",
                policy_id="GG_IAC_0021",
                line_start=0,
                line_end=1,
                description="Having open ingress means that your asset is exposed[...]",
                component="azurerm_network_security_group.bad_sg",
                severity="HIGH",
                documentation_url=POLICY_DOC_URL,
            )
        ],
    )


def test_iac_scan_diff_no_vuln_not_verbose():
    """
    GIVEN a response from the GIM api after a iac scan diff
    WHEN verbose mode is not enabled
    THEN output should display version, new incidents and scan summary
    """
    output_handler = IaCTextOutputHandler(False)
    output = output_handler._process_diff_scan_impl(
        IaCDiffScanCollection(
            id="ID",
            result=IaCDiffScanResult(
                id="ID",
                type="TYPE",
                iac_engine_version="1.0.0",
                entities_with_incidents=IaCDiffScanEntities(
                    new=[], unchanged=[], deleted=[]
                ),
            ),
        )
    )

    assert_iac_diff_version_displayed(output)
    assert_iac_diff_no_new_incident_message(output)
    assert_iac_diff_summary_displayed(output)


def test_iac_scan_diff_vuln_not_verbose():
    """
    GIVEN a response from the GIM api after a iac scan diff
    WHEN verbose mode is not enabled
    THEN output should display version, new incidents and scan summary
    """
    output_handler = IaCTextOutputHandler(False)
    output = output_handler._process_diff_scan_impl(
        IaCDiffScanCollection(
            id="ID",
            result=IaCDiffScanResult(
                id="ID",
                type="TYPE",
                iac_engine_version="1.0.0",
                entities_with_incidents=IaCDiffScanEntities(
                    new=[_generate_iac_file_result()],
                    unchanged=[_generate_iac_file_result()],
                    deleted=[_generate_iac_file_result()],
                ),
            ),
        )
    )

    assert_iac_diff_version_displayed(output)
    assert re.search(r"FILENAME\.tf.*1 new incident detected", output)
    assert_iac_diff_summary_displayed(output, new=1, unchanged=1, deleted=1)
    assert_documentation_url_displayed(output, POLICY_DOC_URL)


def test_iac_scan_diff_no_vuln_verbose():
    """
    GIVEN a response from the GIM api after a iac scan diff
    WHEN verbose mode is enabled
    THEN output should display version, new incidents, unchanged incidents, deleted incidents, and scan summary
    """
    output_handler = IaCTextOutputHandler(True)
    output = output_handler._process_diff_scan_impl(
        IaCDiffScanCollection(
            id="ID",
            result=IaCDiffScanResult(
                id="ID",
                type="TYPE",
                iac_engine_version="1.0.0",
                entities_with_incidents=IaCDiffScanEntities(
                    new=[], unchanged=[], deleted=[]
                ),
            ),
        )
    )

    assert_iac_diff_version_displayed(output)
    assert_iac_diff_no_incident_message(output)
    assert_iac_diff_summary_displayed(output)


def test_iac_scan_diff_vuln_verbose():
    """
    GIVEN a response from the GIM api after a iac scan diff
    WHEN verbose mode is enabled
    THEN output should display version, new incidents, unchanged incidents, deleted incidents, and scan summary
    """
    output_handler = IaCTextOutputHandler(True)
    output = output_handler._process_diff_scan_impl(
        IaCDiffScanCollection(
            id="ID",
            result=IaCDiffScanResult(
                id="ID",
                type="TYPE",
                iac_engine_version="1.0.0",
                entities_with_incidents=IaCDiffScanEntities(
                    new=[_generate_iac_file_result()],
                    unchanged=[_generate_iac_file_result()],
                    deleted=[_generate_iac_file_result()],
                ),
            ),
        )
    )

    assert_iac_diff_version_displayed(output)
    assert re.search(r"FILENAME\.tf.*1 new incident detected", output)
    assert_iac_diff_summary_displayed(output, new=1, unchanged=1, deleted=1)
    assert_documentation_url_displayed(output, POLICY_DOC_URL)


def assert_iac_diff_version_displayed(output: str):
    assert re.search(r"iac-engine-version: \d\.\d{1,3}\.\d", output)


def assert_iac_diff_no_incident_message(output: str):
    assert re.search(r"No incidents have been found", output)


def assert_iac_diff_no_new_incident_message(output: str):
    assert re.search(r"No new incidents have been found", output)


def assert_iac_diff_summary_displayed(output: str, new=0, unchanged=0, deleted=0):
    assert re.search(r"\[-\] " + str(deleted) + " incidents? deleted", output)
    assert re.search(r"\[~\] " + str(unchanged) + " incidents? remaining", output)
    assert re.search(r"\[\+\] " + str(new) + " new incidents? detected", output)


def assert_documentation_url_displayed(output: str, expected_url: str):
    assert re.search(expected_url, output, re.S)
