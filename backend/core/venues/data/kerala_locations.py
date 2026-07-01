# Kerala's 14 districts and urban local bodies (6 municipal corporations + 87 municipalities).
# Source: https://en.wikipedia.org/wiki/List_of_urban_local_bodies_in_Kerala

KERALA_DISTRICT_CITIES = {
    "Thiruvananthapuram": [
        "Thiruvananthapuram",
        "Neyyattinkara",
        "Nedumangad",
        "Attingal",
        "Varkala",
    ],
    "Kollam": [
        "Kollam",
        "Punalur",
        "Karunagappally",
        "Paravur",
        "Kottarakkara",
    ],
    "Pathanamthitta": [
        "Pathanamthitta",
        "Thiruvalla",
        "Adoor",
        "Pandalam",
    ],
    "Alappuzha": [
        "Alappuzha",
        "Kayamkulam",
        "Cherthala",
        "Mavelikkara",
        "Chengannur",
        "Haripad",
    ],
    "Kottayam": [
        "Kottayam",
        "Changanassery",
        "Pala",
        "Vaikom",
        "Ettumanoor",
        "Erattupetta",
    ],
    "Idukki": [
        "Thodupuzha",
        "Kattappana",
    ],
    "Ernakulam": [
        "Kochi",
        "Thrippunithura",
        "Thrikkakara",
        "Kalamassery",
        "Perumbavoor",
        "Aluva",
        "Muvattupuzha",
        "Kothamangalam",
        "North Paravur",
        "Angamaly",
        "Maradu",
        "Eloor",
        "Piravom",
        "Koothattukulam",
    ],
    "Thrissur": [
        "Thrissur",
        "Irinjalakuda",
        "Kunnamkulam",
        "Chalakudy",
        "Kodungallur",
        "Guruvayur",
        "Chavakkad",
        "Vadakkancherry",
    ],
    "Palakkad": [
        "Palakkad",
        "Chittur-Thathamangalam",
        "Ottappalam",
        "Shornur",
        "Mannarkkad",
        "Pattambi",
        "Cherupulassery",
    ],
    "Malappuram": [
        "Malappuram",
        "Manjeri",
        "Ponnani",
        "Tirur",
        "Perinthalmanna",
        "Kottakkal",
        "Nilambur",
        "Kondotty",
        "Valanchery",
        "Tanur",
        "Parappanangadi",
        "Tirurangadi",
    ],
    "Kozhikode": [
        "Kozhikode",
        "Vatakara",
        "Koyilandy",
        "Koduvally",
        "Ramanattukara",
        "Feroke",
        "Payyoli",
        "Mukkam",
    ],
    "Wayanad": [
        "Kalpetta",
        "Mananthavady",
        "Sultan Bathery",
    ],
    "Kannur": [
        "Kannur",
        "Thalassery",
        "Taliparamba",
        "Payyanur",
        "Mattanur",
        "Kuthuparamba",
        "Anthoor",
        "Iritty",
        "Panoor",
        "Sreekandapuram",
    ],
    "Kasaragod": [
        "Kasaragod",
        "Kanhangad",
        "Nileshwaram",
    ],
}

# Legacy district names from earlier seeds → official district names.
LEGACY_DISTRICT_MAP = {
    "Trivandrum": "Thiruvananthapuram",
}

# Legacy city names → official city names when merging districts.
LEGACY_CITY_MAP = {
    "Trivandrum": "Thiruvananthapuram",
}
