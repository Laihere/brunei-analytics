from shared.revision_check import page_owner, sources_in_use


def test_sources_in_use_lists_each_datagovbn_file_once_with_its_studies():
    found = sources_in_use()
    assert found
    for s in found.values():
        assert s["source"] == "datagovbn" and s["sha256"] and s["studies"]


def test_page_owner_reads_the_label_after_data_source_owner():
    page = "<div><h4>Data Source Owner</h4><p>Department of Statistics, JPES</p></div>"
    assert page_owner(page) == "Department of Statistics, JPES"
    assert page_owner("<p>nothing here</p>") == ""
