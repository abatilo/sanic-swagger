def min_str_len(instance, attribute, value):
    min_length = attribute.metadata.get('min_length', None)
    if min_length is None:
        return
    if len(value) <= min_length:
        raise ValueError(
            '\'{}\' must have a minimum length of {} chars'.format(
                attribute.name, min_length
            )
        )


def max_str_len(instance, attribute, value):
    max_length = attribute.metadata.get('max_length', None)
    if max_length is None:
        return
    if len(value) > max_length:
        raise ValueError(
            '\'{}\' must have a maximum length of {} chars'.format(
                attribute.name, max_length
            )
        )


def min_max_str_len(instance, attribute, value):
    min_str_len(instance, attribute, value)
    max_str_len(instance, attribute, value)
