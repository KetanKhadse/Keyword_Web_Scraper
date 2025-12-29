import re

PHONE_REGEX = re.compile(
    r'(\+?\d{1,3}[\s\-]?)?(\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}'
)

def extract_phone_numbers(text):
    matches = PHONE_REGEX.findall(text)

    phones = set()
    for match in matches:
        phone = "".join(match).strip()
        if len(phone) >= 8:
            phones.add(phone)

    return list(phones)
