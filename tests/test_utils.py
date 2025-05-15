# tests/test_utils.py

import sys
sys.path.append("src")  

from utils import generate_offer

def test_generate_offer_valid_clusters():
    assert generate_offer(0) == "Offer: 10% discount on all products"
    assert generate_offer(1) == "Offer: Free shipping for next purchase"
    assert generate_offer(2) == "Offer: VIP membership with exclusive deals"
    assert generate_offer(3) == "Offer: 5% cashback on selected items"

def test_generate_offer_invalid_cluster():
    assert generate_offer(999) == "No special offer"
