class Checker(object):
    def __init__(self):
        pass

    def check(self, data):
        errors = []
        if not "id" in data or data["id"] == None or data["id"].strip() == "":
            errors.append("id field not found or is empty")
        data["errors-check"] = "; ".join(errors)
        return len(errors) == 0
