import pytest
from src.domain.nlp.normalizer import VietnameseTextNormalizer, number_to_vietnamese

def test_number_conversion():
    assert number_to_vietnamese("2026") == "hai nghìn không trăm hai mươi sáu"
    assert number_to_vietnamese("100000") == "một trăm nghìn"
    assert number_to_vietnamese("0") == "không"

def test_date_and_time_normalization():
    norm = VietnameseTextNormalizer()
    text = "Hôm nay 20/07/2026 lúc 09:30"
    normalized = norm.normalize(text)
    assert "ngày hai mươi tháng bảy năm hai nghìn không trăm hai mươi sáu" in normalized
    assert "chín giờ ba mươi phút" in normalized

def test_currency_and_measurement_normalization():
    norm = VietnameseTextNormalizer()
    text = "Giá 100.000đ mua 50km vé hết $50 ở 25°C"
    normalized = norm.normalize(text)
    assert "một trăm nghìn đồng" in normalized
    assert "năm mươi ki lô mét" in normalized
    assert "năm mươi đô la" in normalized
    assert "hai mươi lăm độ C" in normalized

def test_abbreviations_and_roman():
    norm = VietnameseTextNormalizer()
    text = "Ủy ban nhân dân TP.HCM thuộc thế kỷ XXI"
    normalized = norm.normalize(text)
    assert "Thành phố Hồ Chí Minh" in normalized
    assert "hai mươi mốt" in normalized
