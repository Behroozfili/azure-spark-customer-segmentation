def generate_offer(cluster_id):
    if cluster_id == 0:
        return "Offer: 10% discount on all products"
    elif cluster_id == 1:
        return "Offer: Free shipping for next purchase"
    elif cluster_id == 2:
        return "Offer: VIP membership with exclusive deals"
    elif cluster_id == 3:
        return "Offer: 5% cashback on selected items"
    else:
        return "No special offer"