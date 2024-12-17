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
                options = [f":gray[{opt}]" for opt in options]
                sum_of_length_options = sum([len(opt) for opt in options])

                # En vez de mirar el número de opciones, miramos si
                # la suma de longitud de opciones es lo suficientemente grande
                # if len(options) > 6:
                # if sum_of_length_options > 500:
                # De momento, no hacerlo nunca
                if False:
                    res += "\n\n"
                    res += "\t| | | | |\n"
                    res += "\t|---|---|---|---|\n"
                    num_rows = (len(options) + 3) // 4
                    for i in range(num_rows):
                        row_options = options[i * 4 : (i + 1) * 4]
                        res += "\t| " + " | ".join(row_options) + " |\n"
                else:
                    options_united = Utils.join_spanish(options)
                    res += f", con posibles valores: {options_united}."
            res += "\n"
        return res
