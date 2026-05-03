from app.filters import match_keywords


def test_match_keywords_basic():
    text = "Selling LEGO set"
    keywords = ["lego"]

    result = match_keywords(text, keywords)

    assert result == ["lego"]


def test_match_keywords_case_insensitive():
    text = "Продаю ПРИНТЕР"
    keywords = ["принтер"]

    result = match_keywords(text, keywords)

    assert result == ["принтер"]


def test_match_keywords_no_match():
    text = "Nothing interesting here"
    keywords = ["lego"]

    result = match_keywords(text, keywords)

    assert result == []