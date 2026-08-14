def display_details(name, email, location, score="N/A"):
    """
    Combines and displays name, email, location and score details.
    
    Args:
        name (str): The person's name
        email (str): The person's email address
        location (str): The person's location
        score (float | str, optional): The person's score
    """
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Location: {location}")
    print(f"Score: {score}")
    print("-" * 40)


if __name__ == "__main__":
    display_details(
        name="sm sohel",
        email="iamsmsohel",
        location="kolkata",
    )
