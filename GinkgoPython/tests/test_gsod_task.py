import pytest
from ginkgo.services.inspector import inspector_service
from ginkgo.services.tasks.gsod import gsod_task


@pytest.fixture(autouse=True)
def reset_inspector(monkeypatch):
    # ensure inspector has a dummy generate method and model/tokenizer state
    inspector_service.model = True
    inspector_service.tokenizer = True
    yield
    inspector_service.model = None
    inspector_service.tokenizer = None


def test_gsod_classification_valid(monkeypatch):
    # stub out the model output to return a known label
    monkeypatch.setattr(
        inspector_service, "generate", lambda prompt_text: "CREDIBLE_ELECTIONS"
    )

    trait, attribute = gsod_task.classify("some input")
    assert trait == "CREDIBLE_ELECTIONS"
    assert attribute == "REPRESENTATION"


def test_gsod_classification_invalid(monkeypatch):
    monkeypatch.setattr(inspector_service, "generate", lambda prompt_text: "INVALID")

    trait, attribute = gsod_task.classify("foo")
    assert trait == "INVALID"
    assert attribute is None


def test_gsod_classification_missing(monkeypatch):
    # output that doesn't match any label
    monkeypatch.setattr(inspector_service, "generate", lambda prompt_text: "UNKNOWN")
    trait, attribute = gsod_task.classify("bar")
    assert trait is None
    assert attribute is None
