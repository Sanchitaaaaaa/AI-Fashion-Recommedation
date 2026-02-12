def recommend_outfit(body_type: str, occasion: str):
    recommendations = {
        "Inverted Triangle": {
            "Casual": "Flared jeans with soft tops",
            "Wedding": "A-line gown",
            "Office": "Peplum tops with straight pants"
        },
        "Pear": {
            "Casual": "High-waist jeans with structured tops",
            "Wedding": "Empire waist dress",
            "Office": "Structured blazers"
        },
        "Balanced": {
            "Casual": "Anything suits you!",
            "Wedding": "Bodycon dress",
            "Office": "Tailored suits"
        }
    }

    return recommendations.get(body_type, {}).get(occasion, "Standard outfit")
