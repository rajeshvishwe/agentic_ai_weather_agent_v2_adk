"""
Common location aliases.

This map intentionally contains only abbreviations, alternate spellings,
and a small number of commonly used canonical names.

Normal world-city discovery is handled dynamically through the Open-Meteo
geocoding service. The alias map is therefore not intended to become a
complete list of cities.
"""

CITY_ALIASES = {

    # ==========================================================
    # India
    # ==========================================================

    "blr": "Bangalore",
    "b'lore": "Bangalore",
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",

    "bom": "Mumbai",
    "bombay": "Mumbai",
    "mumbai": "Mumbai",

    "del": "Delhi",
    "new delhi": "Delhi",
    "delhi": "Delhi",

    "hyd": "Hyderabad",
    "hyderabad": "Hyderabad",

    "maa": "Chennai",
    "che": "Chennai",
    "madras": "Chennai",
    "chennai": "Chennai",

    "ccu": "Kolkata",
    "cal": "Kolkata",
    "calcutta": "Kolkata",
    "kolkata": "Kolkata",

    "pnq": "Pune",
    "pune": "Pune",

    "amd": "Ahmedabad",
    "ahmedabad": "Ahmedabad",

    "jpr": "Jaipur",
    "jaipur": "Jaipur",

    "goi": "Goa",
    "goa": "Goa",

    "cok": "Kochi",
    "cochin": "Kochi",
    "kochi": "Kochi",

    "trv": "Thiruvananthapuram",
    "trivandrum": "Thiruvananthapuram",

    "ixc": "Chandigarh",
    "chandigarh": "Chandigarh",

    "lko": "Lucknow",
    "lucknow": "Lucknow",

    "vns": "Varanasi",
    "banaras": "Varanasi",
    "benares": "Varanasi",

    "idr": "Indore",
    "indore": "Indore",

    "bho": "Bhopal",
    "bhopal": "Bhopal",

    "nag": "Nagpur",
    "nagpur": "Nagpur",

    "pat": "Patna",
    "patna": "Patna",

    "rpr": "Raipur",
    "raipur": "Raipur",

    "bbI": "Bhubaneswar",
    "bhubaneswar": "Bhubaneswar",
    "bhubaneshwar": "Bhubaneswar",

    "gau": "Guwahati",
    "guwahati": "Guwahati",

    "ixb": "Siliguri",
    "siliguri": "Siliguri",

    "ded": "Dehradun",
    "dehradun": "Dehradun",

    "manali": "Manali",
    "shimla": "Shimla",
    "mussoorie": "Mussoorie",
    "rishikesh": "Rishikesh",
    "haridwar": "Haridwar",
    "nainital": "Nainital",

    "jabalpur": "Jabalpur",
    "jlr": "Jabalpur",
    "jbp": "Jabalpur",


    "gurgaon": "Gurugram",
    "gurugram": "Gurugram",

    # ==========================================================
    # United States
    # ==========================================================

    "nyc": "New York",
    "new york city": "New York",
    "new york": "New York",

    "la": "Los Angeles",
    "lax": "Los Angeles",
    "los angeles": "Los Angeles",

    "sf": "San Francisco",
    "sfo": "San Francisco",
    "san francisco": "San Francisco",

    "dc": "Washington",
    "washington dc": "Washington",
    "washington d.c.": "Washington",

    "chi": "Chicago",
    "ord": "Chicago",
    "chicago": "Chicago",

    "bos": "Boston",
    "boston": "Boston",

    "mia": "Miami",
    "miami": "Miami",

    "sea": "Seattle",
    "seattle": "Seattle",

    "las": "Las Vegas",
    "vegas": "Las Vegas",
    "las vegas": "Las Vegas",

    "atl": "Atlanta",
    "atlanta": "Atlanta",

    "dfw": "Dallas",
    "dallas": "Dallas",

    "hou": "Houston",
    "iah": "Houston",
    "houston": "Houston",

    "phx": "Phoenix",
    "phoenix": "Phoenix",

    "den": "Denver",
    "denver": "Denver",

    "san diego": "San Diego",
    "san jose": "San Jose",

    # ==========================================================
    # United Kingdom
    # ==========================================================

    "ldn": "London",
    "lon": "London",
    "lhr": "London",
    "london": "London",

    "man": "Manchester",
    "manchester": "Manchester",

    "bhx": "Birmingham",
    "birmingham uk": "Birmingham",

    "edi": "Edinburgh",
    "edinburgh": "Edinburgh",

    "gla": "Glasgow",
    "glasgow": "Glasgow",

    "lpl": "Liverpool",
    "liverpool": "Liverpool",

    # ==========================================================
    # France
    # ==========================================================

    "par": "Paris",
    "cdg": "Paris",
    "paris": "Paris",

    "mrs": "Marseille",
    "marseille": "Marseille",

    "lys": "Lyon",
    "lyon": "Lyon",

    "nce": "Nice",
    "nice france": "Nice",

    # ==========================================================
    # Germany
    # ==========================================================

    "ber": "Berlin",
    "berlin": "Berlin",

    "muc": "Munich",
    "münchen": "Munich",
    "munich": "Munich",

    "fra": "Frankfurt",
    "frankfurt": "Frankfurt",

    "ham": "Hamburg",
    "hamburg": "Hamburg",

    "cologne": "Cologne",
    "köln": "Cologne",

    # ==========================================================
    # Italy
    # ==========================================================

    "rom": "Rome",
    "fco": "Rome",
    "roma": "Rome",
    "rome": "Rome",

    "mil": "Milan",
    "mxp": "Milan",
    "milano": "Milan",
    "milan": "Milan",

    "ven": "Venice",
    "venezia": "Venice",
    "venice": "Venice",

    "nap": "Naples",
    "napoli": "Naples",

    # ==========================================================
    # Spain
    # ==========================================================

    "mad": "Madrid",
    "madrid": "Madrid",

    "bcn": "Barcelona",
    "barcelona": "Barcelona",

    "sev": "Seville",
    "sevilla": "Seville",

    "vlc": "Valencia",
    "valencia": "Valencia",

    # ==========================================================
    # UAE
    # ==========================================================

    "dxb": "Dubai",
    "dubai": "Dubai",

    "auh": "Abu Dhabi",
    "abu dhabi": "Abu Dhabi",

    "shj": "Sharjah",
    "sharjah": "Sharjah",

    # ==========================================================
    # Saudi Arabia
    # ==========================================================

    "ruh": "Riyadh",
    "riyadh": "Riyadh",

    "jed": "Jeddah",
    "jeddah": "Jeddah",

    "med": "Medina",
    "madinah": "Medina",
    "medina": "Medina",

    # ==========================================================
    # Qatar
    # ==========================================================

    "doh": "Doha",
    "doha": "Doha",

    # ==========================================================
    # Singapore
    # ==========================================================

    "sin": "Singapore",
    "sg": "Singapore",
    "singapore": "Singapore",

    # ==========================================================
    # Malaysia
    # ==========================================================

    "kul": "Kuala Lumpur",
    "kl": "Kuala Lumpur",
    "kuala lumpur": "Kuala Lumpur",

    # ==========================================================
    # Thailand
    # ==========================================================

    "bkk": "Bangkok",
    "bangkok": "Bangkok",

    "hkt": "Phuket",
    "phuket": "Phuket",

    # ==========================================================
    # Indonesia
    # ==========================================================

    "jkt": "Jakarta",
    "cgk": "Jakarta",
    "jakarta": "Jakarta",

    "dps": "Denpasar",
    "bali": "Denpasar",

    # ==========================================================
    # Japan
    # ==========================================================

    "tyo": "Tokyo",
    "nrt": "Tokyo",
    "hnd": "Tokyo",
    "tokyo": "Tokyo",

    "osa": "Osaka",
    "kix": "Osaka",
    "osaka": "Osaka",

    "kyo": "Kyoto",
    "kyoto": "Kyoto",

    # ==========================================================
    # South Korea
    # ==========================================================

    "sel": "Seoul",
    "icn": "Seoul",
    "seoul": "Seoul",

    "pus": "Busan",
    "busan": "Busan",

    # ==========================================================
    # China
    # ==========================================================

    "pek": "Beijing",
    "bjs": "Beijing",
    "beijing": "Beijing",
    "peking": "Beijing",

    "sha": "Shanghai",
    "pvg": "Shanghai",
    "shanghai": "Shanghai",

    "can": "Guangzhou",
    "guangzhou": "Guangzhou",
    "canton": "Guangzhou",

    "szx": "Shenzhen",
    "shenzhen": "Shenzhen",

    # ==========================================================
    # Hong Kong
    # ==========================================================

    "hkg": "Hong Kong",
    "hk": "Hong Kong",
    "hong kong": "Hong Kong",

    # ==========================================================
    # Australia
    # ==========================================================

    "syd": "Sydney",
    "sydney": "Sydney",

    "mel": "Melbourne",
    "melbourne": "Melbourne",

    "bne": "Brisbane",
    "brisbane": "Brisbane",

    "per": "Perth",
    "perth": "Perth",

    "adl": "Adelaide",
    "adelaide": "Adelaide",

    # ==========================================================
    # New Zealand
    # ==========================================================

    "akl": "Auckland",
    "auckland": "Auckland",

    "wlg": "Wellington",
    "wellington": "Wellington",

    "chc": "Christchurch",
    "christchurch": "Christchurch",

    # ==========================================================
    # Canada
    # ==========================================================

    "yyz": "Toronto",
    "tor": "Toronto",
    "toronto": "Toronto",

    "yvr": "Vancouver",
    "vancouver": "Vancouver",

    "yul": "Montreal",
    "montreal": "Montreal",
    "montréal": "Montreal",

    "yyc": "Calgary",
    "calgary": "Calgary",

    "yow": "Ottawa",
    "ottawa": "Ottawa",

    # ==========================================================
    # Brazil
    # ==========================================================

    "rio": "Rio de Janeiro",
    "gig": "Rio de Janeiro",
    "rio de janeiro": "Rio de Janeiro",

    "sao paulo": "São Paulo",
    "são paulo": "São Paulo",
    "gru": "São Paulo",

    # ==========================================================
    # Argentina
    # ==========================================================

    "bue": "Buenos Aires",
    "eze": "Buenos Aires",
    "buenos aires": "Buenos Aires",

    # ==========================================================
    # Mexico
    # ==========================================================

    "mex": "Mexico City",
    "cdmx": "Mexico City",
    "mexico city": "Mexico City",

    "cun": "Cancun",
    "cancún": "Cancun",
    "cancun": "Cancun",

    # ==========================================================
    # South Africa
    # ==========================================================

    "jnb": "Johannesburg",
    "joburg": "Johannesburg",
    "johannesburg": "Johannesburg",

    "cpt": "Cape Town",
    "cape town": "Cape Town",

    "dur": "Durban",
    "durban": "Durban",

    # ==========================================================
    # Egypt
    # ==========================================================

    "cai": "Cairo",
    "cairo": "Cairo",

    "alex": "Alexandria",
    "alexandria egypt": "Alexandria",

    # ==========================================================
    # Turkey
    # ==========================================================

    "ist": "Istanbul",
    "istanbul": "Istanbul",

    "ank": "Ankara",
    "ankara": "Ankara",

    # ==========================================================
    # Russia
    # ==========================================================

    "mow": "Moscow",
    "svo": "Moscow",
    "moscow": "Moscow",

    "led": "Saint Petersburg",
    "st petersburg": "Saint Petersburg",
    "saint petersburg": "Saint Petersburg",

    # ==========================================================
    # Netherlands
    # ==========================================================

    "ams": "Amsterdam",
    "amsterdam": "Amsterdam",

    # ==========================================================
    # Switzerland
    # ==========================================================

    "zrh": "Zurich",
    "zürich": "Zurich",
    "zurich": "Zurich",

    "gva": "Geneva",
    "geneva": "Geneva",

    # ==========================================================
    # Austria
    # ==========================================================

    "vie": "Vienna",
    "wien": "Vienna",
    "vienna": "Vienna",

    # ==========================================================
    # Ireland
    # ==========================================================

    "dub": "Dublin",
    "dublin": "Dublin",

    # ==========================================================
    # Iceland
    # ==========================================================

    "rek": "Reykjavik",
    "kef": "Reykjavik",
    "reykjavik": "Reykjavik",

    # ==========================================================
    # Portugal
    # ==========================================================

    "lis": "Lisbon",
    "lisboa": "Lisbon",
    "lisbon": "Lisbon",

    "opo": "Porto",
    "porto": "Porto",
}