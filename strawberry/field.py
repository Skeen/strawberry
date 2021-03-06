import dataclasses
from typing import Any, Callable, List, Optional, Type, Union

from .permission import BasePermission
from .types.fields.resolver import StrawberryResolver
from .types.types import FederationFieldParams, FieldDefinition
from .utils.str_converters import to_camel_case


_RESOLVER_TYPE = Union[StrawberryResolver, Callable]


class StrawberryField(dataclasses.Field):
    _field_definition: FieldDefinition

    def __init__(self, field_definition: FieldDefinition):

        self._field_definition = field_definition

        # Copied from dataclasses.Field.__init__, but without setting .name and .type
        # to None
        self.name = field_definition.name
        self.type = field_definition.type
        self.default = dataclasses.MISSING
        self.default_factory = dataclasses.MISSING
        self.init = field_definition.base_resolver is None
        self.repr = True
        self.hash = None
        self.compare = True
        self.metadata = dataclasses._EMPTY_METADATA

        self._field_type = None

    def __call__(self, resolver: _RESOLVER_TYPE) -> "StrawberryField":
        """Add a resolver to the field"""

        # Allow for StrawberryResolvers or bare functions to be provided
        if not isinstance(resolver, StrawberryResolver):
            resolver = StrawberryResolver(resolver)

        self._field_definition.origin_name = resolver.name
        self._field_definition.origin = resolver.wrapped_func
        self._field_definition.base_resolver = resolver
        self._field_definition.arguments = resolver.arguments
        self._field_definition.type = resolver.type

        # Don't add field to __init__ or __repr__
        self.init = False
        self.repr = False

        return self

    def __setattr__(self, name, value):
        if name == "type":
            self._field_definition.type = value

        if value and name == "name":
            if not self._field_definition.origin_name:
                self._field_definition.origin_name = value

            camel_case_name = to_camel_case(value)
            if not self._field_definition.name:
                self._field_definition.name = camel_case_name
            value = camel_case_name

        return super().__setattr__(name, value)

    @property
    def is_child_optional(self) -> bool:
        return self._field_definition.is_child_optional

    @property
    def is_list(self) -> bool:
        return self._field_definition.is_list

    @property
    def is_optional(self) -> bool:
        return self._field_definition.is_optional

    @property
    def is_subscription(self) -> bool:
        return self._field_definition.is_subscription

    @property
    def is_union(self) -> bool:
        return self._field_definition.is_union

    # @property
    # def type_(self) -> Optional[Union[Type, StrawberryUnion]]:
    #     if self._type is not None:
    #         return self._type
    #     elif self._field_definition.base_resolver:
    #         return self._field_definition.base_resolver.type
    #     else:
    #         return None

    @property
    def child(self) -> "StrawberryField":
        return self._field_definition.child

    @property
    def default_value(self) -> Any:
        return self._field_definition.default_value

    @property
    def description(self) -> Optional[str]:
        return self._field_definition.description

    @property
    def is_child_optional(self) -> bool:
        return self._field_definition.is_child_optional

    @property
    def is_list(self) -> bool:
        return self._field_definition.is_list

    @property
    def is_optional(self) -> bool:
        return self._field_definition.is_optional

    @property
    def is_subscription(self) -> bool:
        return self._field_definition.is_subscription

    @property
    def is_union(self) -> bool:
        return self._field_definition.is_union

    @property
    def origin(self) -> Optional[Union[Type, Callable]]:
        return self._field_definition.origin

    @property
    def origin_name(self) -> Optional[str]:
        return self._field_definition.origin_name

    # @property
    # def type_(self) -> Optional[Union[Type, StrawberryUnion]]:
    #     if self._type is not None:
    #         return self._type
    #     elif self._field_definition.base_resolver:
    #         return self._field_definition.base_resolver.type
    #     else:
    #         return None


def field(
    resolver: Optional[_RESOLVER_TYPE] = None,
    *,
    name: Optional[str] = None,
    is_subscription: bool = False,
    description: Optional[str] = None,
    permission_classes: Optional[List[Type[BasePermission]]] = None,
    federation: Optional[FederationFieldParams] = None,
    deprecation_reason: Optional[str] = None,
) -> StrawberryField:
    """Annotates a method or property as a GraphQL field.

    This is normally used inside a type declaration:

    >>> @strawberry.type:
    >>> class X:
    >>>     field_abc: str = strawberry.field(description="ABC")

    >>>     @strawberry.field(description="ABC")
    >>>     def field_with_resolver(self, info) -> str:
    >>>         return "abc"

    it can be used both as decorator and as a normal function.
    """

    field_definition = FieldDefinition(
        origin_name=None,  # modified by resolver in __call__
        name=name,
        type=None,
        description=description,
        is_subscription=is_subscription,
        permission_classes=permission_classes or [],
        arguments=[],  # modified by resolver in __call__
        federation=federation or FederationFieldParams(),
        deprecation_reason=deprecation_reason,
    )

    field_ = StrawberryField(field_definition)

    if resolver:
        return field_(resolver)
    return field_


__all__ = ["FederationFieldParams", "FieldDefinition", "StrawberryField", "field"]
