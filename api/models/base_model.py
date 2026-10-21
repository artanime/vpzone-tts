from dataclasses import dataclass, fields


@dataclass
class BaseModel:

    @classmethod
    def from_json(cls, data: dict):

        if data is None:
            return None

        field_names = {
            field.name
            for field in fields(cls)
        }

        values = {}

        for key, value in data.items():

            if key in field_names:

                values[key] = value

        return cls(**values)

    def to_dict(self):

        return self.__dict__