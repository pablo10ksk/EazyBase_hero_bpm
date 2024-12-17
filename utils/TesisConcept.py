from utils.utils import Utils


class TesisConcept:
    @staticmethod
    def display(tipo: str, data: dict) -> str:
        res = f"Para dar de alta **{tipo}** en Tesis, tienes que darme estos datos:\n"
        for field in data:
            res += f"- **{field['title']}**"
            if field["options"]:
                options = field["options"]

                def clean_option(opt):
                    if "$" in opt:
                        return opt.split("$")[1]
                    return opt

                options = [clean_option(opt) for opt in options]
                options = [f"'{opt}'" for opt in options]
                options_united = Utils.join_spanish(options)
                res += f", con posibles valores: {options_united}."
            else:
                res += "."
            res += "\n"
        return res

    @staticmethod
    def get_mapping(data: dict) -> str:
        res = "I need you to perform the following mapping for each key of the dictionary:"
        for field in data:
            res += f"\n- **{field['title']}** must become **{field['tag']}**: "
            if field["options"]:
                res += "map the values in the following way: "
                options = field["options"]
                for opt in options:
                    assert "$" in opt, f"Option has no dollar sign: {opt}"
                    key, text = opt.split("$")
                    res += f"\n\t- '{text}' -> {key}"
            else:
                res += "leave it as is."
        return res
