from dataclasses import dataclass
from typing import ClassVar, Any, Self
from psygnal import EmissionInfo, SignalGroupDescriptor


# BaseModel as observer to nofitfy dataclasses whenever there is a change / are changes on the dataclass fields
# https://psygnal.readthedocs.io/en/latest/dataclasses/?h=signalgroupdescriptor#evented-dataclasses
@dataclass
class BaseModel:

    # cls var shared across all instance
    # Uses Psygnal's SignalGroupDescriptor to emit signals when fields change
    _events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()

    # connects the event
    def __post_init__(self):
        # connect observer to callback
        self._events.connect(self._on_event)
        # a dict to keep modified fields
        self._modified_fields = {}

    # callback
    def _on_event(self, info: EmissionInfo):
        # unpack EmissionInfo
        # EmissionInfo.args is tuple(new, old)
        # new_value, original_value = list(info.args)
        new_value, original_value = info.args
        # return if no fields changed
        if new_value == original_value:
            return
        # get touched field name
        field_name = info.signal.name

        # add to dict if not in dict
        if field_name not in self._modified_fields:
            self._modified_fields[field_name] = {
                "original_value": original_value,
                "new_value": new_value,
            }
        # update if field in dict
        else:
            self._modified_fields[field_name].update(
                {"new_value": new_value}
            )

    # called when setting attribute
    # and call corresponding validate_<field_name> method
    def __setattr__(self, key: str, value: Any) -> None:
        if method := getattr(self, f"validate_{key}", None):
            value = method(value)
        # avoid infinite recursion
        super().__setattr__(key, value)

    # Accessible by instance.modified_fields
    @property
    def modified_fields(self) -> dict:
        return self._modified_fields

    # rollback changes
    def rollback(self) -> Self:
        for _field, _value in self.modified_fields.items():
            # will call __setattr__
            setattr(self, _field, _value["original_value"])
        # clear dict
        self.modified_fields.clear()
        return self
