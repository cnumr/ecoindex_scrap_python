from ecoindex_scraper.models import Page, Result
from pydantic import ValidationError
from pytest import raises


def test_model_page():
    logs = ["Logs of my page"]
    outer_html = "Html of my page"
    nodes = ["node1", "node2", "node3"]

    page = Page(
        logs=logs,
        outer_html=outer_html,
        nodes=nodes,
    )

    assert page.logs == logs
    assert page.outer_html == outer_html
    assert page.nodes == nodes

    with raises(ValidationError):
        Page(logs=logs)


def test_result_model():
    result = Result(
        size=119,
        nodes=45,
        requests=8,
        url="http://www.myurl.com",
        width=1920,
        height=1080,
        grade="A",
        score=89,
        ges=1.22,
        water=1.89,
    )
    assert result.page_type is None
    assert result.size == 119
    assert result.nodes == 45
    assert result.requests == 8
    assert result.width == 1920
    assert result.height == 1080
    assert result.grade == "A"
    assert result.score == 89
    assert result.ges == 1.22
    assert result.water == 1.89
