 
class Enum(object):
    @classmethod
    def name_from_value(cls, value):
        for name, name_value in cls.__dict__.items():
            if name.isupper() and name_value == value:
                return name


class BitFieldEnum(Enum):
    @classmethod
    def name_from_value(cls, value):
        if not isinstance(value, int):
            return
        ret_names = []
        ret_value = 0
        for cls_name, cls_value in sorted(
            [(n, v) for (n, v) in cls.__dict__.items()
             if isinstance(v, int) and n.isupper() and v | value == value],
            reverse=True, key=lambda p: p[1]
        ):
            if ret_value | cls_value != ret_value or cls_value == value:
                ret_names.append(cls_name)
                ret_value |= cls_value
        if ret_value == value:
            return '|'.join(reversed(ret_names)) if ret_names else '0'
