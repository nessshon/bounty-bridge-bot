class InitValue:
    """
    Base class for initializing class attributes with their names as values.
    """

    def __init_subclass__(cls, **kwargs):
        """
        Initialize subclass attributes with their names as values.

        :param kwargs: Keyword arguments representing the subclass attributes.
        """
        for attr in cls.__annotations__:
            setattr(cls, attr, attr)
        super().__init_subclass__(**kwargs)
